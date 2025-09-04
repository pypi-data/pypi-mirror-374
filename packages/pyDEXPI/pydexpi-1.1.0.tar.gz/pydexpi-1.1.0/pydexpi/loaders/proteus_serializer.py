"""This module contains the Proteus serializer, extending the abstract
serializer class. It parses the information from and to a dexpi conform
proteus xml file."""

import types
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from pydexpi.dexpi_classes import (
    dataTypes,
    dexpiModel,
    enumerations,
    equipment,
    instrumentation,
    physicalQuantities,
    piping,
)
from pydexpi.loaders.serializer import Serializer
from pydexpi.toolkits import piping_toolkit


class ProteusSerializer(Serializer):
    """
    This class loads an XML file containing data in Proteus format into memory
    and transforms it into a Dexpi format.
    """

    def __init__(self) -> None:
        self.proteus_root = None
        self._all_objects = {}

    def save(self, model: dexpiModel.DexpiModel, dir_path: Path, filename: str):
        """Transforms a DexpiModel to the Proteus format. Not implemented yet."""
        raise NotImplementedError

    def load(self, dir_path: Path, filename: str):
        """Transforms the data in the Proteus .xml file to a DexpiModel class.

        Parameters
        ----------
        dir_path : Path
            Directory where the proteus file is stored.
        filename : str
            Filename of the proteus file.

        Returns
        -------
        DexpiModel
            Loaded DEXPI model.
        """
        if not filename.endswith(".xml"):
            filename += ".xml"
        path = Path(dir_path) / filename

        self.proteus_root = ET.parse(path).getroot()
        # call all lower lever parsers methods
        equipment = self.parse_equipment()
        piping_network_systems = self.parse_piping_network_systems()
        actuating_systems = self.parse_actuating_system()
        p_signal_generating_system = self.parse_process_signal_generating_systems()
        p_instrumentation_function = self.parse_process_instrumentation_functions()
        i_loop_functions = self.parse_instrumentation_loop_functions()

        # Make a conceptual model
        conceptual_model = dexpiModel.ConceptualModel(
            taggedPlantItems=equipment,
            pipingNetworkSystems=piping_network_systems,
            actuatingSystems=actuating_systems,
            processSignalGeneratingSystems=p_signal_generating_system,
            instrumentationLoopFunctions=i_loop_functions,
            processInstrumentationFunctions=p_instrumentation_function,
        )
        # Make a dexpi model with only the conceptual model
        plant_information = self.proteus_root.findall("PlantInformation")[0]
        the_date = tuple(int(i) for i in plant_information.get("Date").split("-"))
        raw_time = tuple(float(i) for i in plant_information.get("Time").split(":"))
        microseconds = int((raw_time[2] - int(raw_time[2])) * 1000000)
        the_time = (
            int(raw_time[0]),
            int(raw_time[1]),
            int(raw_time[2]),
            microseconds,
        )
        date_time = datetime(*(the_date + the_time))
        the_system = plant_information.get("OriginatingSystem")
        the_vendor = plant_information.get("OriginatingSystemVendor")
        the_version = plant_information.get("OriginatingSystemVersion")
        dexpi_plant = dexpiModel.DexpiModel(
            conceptualModel=conceptual_model,
            exportDateTime=date_time,
            originatingSystemName=the_system,
            originatingSystemVendorName=the_vendor,
            originatingSystemVersion=the_version,
        )
        return dexpi_plant

    def parse_equipment(self):
        """Parse all proteus equipment found in the root element to DEXPI
        equipment classes.

        Returns
        -------
        list of Equipment
            A list of DEXPI equipment objects that have been created.

        """

        def add_by_inferring_type(to_be_added, to_be_added_to):
            """Adds an attribute to a class by inferring the correct type. Tries
            to set all attributes or add them to existing lists in that field.
            Returns the name of the field found
            """
            field_found = False
            found_field = None
            for field in to_be_added_to.model_fields:
                try:
                    setattr(to_be_added_to, field, to_be_added)
                    field_found = True
                    found_field = field
                    break
                except ValidationError:
                    pass
                try:
                    new_list = list(getattr(to_be_added_to, field))
                    new_list.append(to_be_added)
                    setattr(to_be_added_to, field, new_list)
                    field_found = True
                    found_field = field
                    break
                except (ValidationError, TypeError):
                    pass
            if not field_found:
                raise ValueError(f"No suitable field found in {to_be_added_to} for {to_be_added}")

            return found_field

        def make_equipment(root_element: ET.Element, depth: int):
            """Function to extract an equipment from a root element. Defined here
            to be used recursively.

            Parameters
            ----------
            root_element : ET.Element
                The proteus xml element corresponding to the equipment

            Returns
            -------
            equipment.Equipment
                Extracted equipment with nested equipment
            """
            class_name = root_element.get("ComponentClass")
            # Manage the differentiation between subtagged and tagged column sections
            if class_name == "ColumnSection":
                class_name = "TaggedColumnSection" if depth == 0 else "SubTaggedColumnSection"
            kwargs = {}
            # If class name not part of equipment, treat it as custom equipment
            try:
                MyClass = getattr(equipment, class_name)
            except AttributeError:
                MyClass = equipment.CustomEquipment
                kwargs["typeName"] = class_name
            nozzles = []
            # Retrieve equipment nozzles
            for prot_nozzle in root_element.findall("Nozzle"):
                nozzle_piping_nodes = self.retrieve_piping_nodes(prot_nozzle)
                dexpi_nozzle = self.make_or_retrieve_class(
                    equipment.Nozzle,
                    prot_nozzle.get("ID"),
                    prot_nozzle,
                    nodes=nozzle_piping_nodes,
                )
                nozzles.append(dexpi_nozzle)

            # Make new equipment instance
            new_equipment = self.make_or_retrieve_class(
                MyClass,
                root_element.get("ID"),
                root_element,
                nozzles=nozzles,
                **kwargs,
            )
            # Manage and add subequipments
            for subequipment in root_element.findall("Equipment"):
                new_subequipment = make_equipment(subequipment, depth + 1)
                add_by_inferring_type(new_subequipment, new_equipment)
            # Manage "is located in" relationships
            for association_element in root_element.findall("Association"):
                # Add after occurring the "is location of" or the "is located in"
                # relationship. To avoid redundance, this is only invoked if the
                # other object of the relationship has already been created and
                # is found in _all_objects
                item_id = association_element.get("ItemID")
                try:
                    associated_object = self._all_objects[item_id]
                except KeyError:
                    pass
                else:
                    if association_element.get("Type") == "is the location of":
                        try:
                            add_by_inferring_type(associated_object, new_equipment)
                        # This error handling is necessary because sometimes the association
                        # is the other way around for reference attributes in dexpi (e.g. for nozzles and chambers)
                        except ValueError:
                            add_by_inferring_type(new_equipment, associated_object)
                    elif association_element.get("Type") == "is located in":
                        try:
                            add_by_inferring_type(new_equipment, associated_object)
                        # This error handling is necessary because sometimes the association
                        # is the other way around for reference attributes in dexpi (e.g. for tube bundles and chambers)
                        except ValueError:
                            add_by_inferring_type(associated_object, new_equipment)

            return new_equipment

        tagged_plant_items = []
        for prot_equipment in self.proteus_root.findall("Equipment"):
            new_equipment = make_equipment(prot_equipment, 0)
            if isinstance(new_equipment, equipment.TaggedPlantItem):
                tagged_plant_items.append(new_equipment)

        return tagged_plant_items

    def parse_piping_network_systems(self):
        """Parse all proteus piping network systems found in the root element
        to DEXPI equipment classes.

        Returns
        -------
        list of PipingNetworkSystems:
            DEXPI equipment objects that have been created.

        """

        def get_item_connection_nodes(proteus_item: ET.Element):
            if proteus_item is None:
                return None
            connection_dict = {"inlet": None, "outlet": None}
            cpoints_list = proteus_item.findall("ConnectionPoints")
            if cpoints_list:
                if len(cpoints_list) > 1:
                    raise NotImplementedError(
                        "Case for more than 1 conntectionpoints not known and implemented"
                    )
                cpoints = cpoints_list[0]
            else:
                return connection_dict
            out_flow_node_index = cpoints.get("FlowOut")
            in_flow_node_index = cpoints.get("FlowIn")
            no_process_nodes = len(
                [i for i in cpoints.findall("Node") if i.get("Type") == "process"]
            )
            if out_flow_node_index is None:
                if in_flow_node_index != 2 and no_process_nodes >= 2:
                    out_flow_node_index = 2  # Defaults to 2 in proteus schema
            else:
                out_flow_node_index = int(out_flow_node_index)

            if in_flow_node_index is None:
                if out_flow_node_index != 1 and no_process_nodes >= 1:
                    in_flow_node_index = 1  # Defaults to 1 in proteus schema
            else:
                in_flow_node_index = int(in_flow_node_index)

            connection_dict["outlet"] = out_flow_node_index
            connection_dict["inlet"] = in_flow_node_index
            return connection_dict

        def get_ordered_segment_elements(pr_segment):
            """This method determines if the proteus segment is reversed,
            as determined by the outside connections."""
            connections = pr_piping_network_segment.findall("Connection")
            pr_seg_connection = connections[0] if connections else None
            segment_elements = list(pr_segment.iter())
            if pr_seg_connection is None:
                return segment_elements
            frID = pr_seg_connection.get("FromID")
            toID = pr_seg_connection.get("ToID")
            item_tags = [
                "PipingComponent",
                "PipeOffPageConnector",
                "PropertyBreak",
            ]
            items = [element for element in segment_elements if element.tag in item_tags]
            # Check if last item is referenced as source, or first item as
            # target. In this case, the segment is reversed
            if len(items) >= 2:
                if frID == items[-1].get("ID") or toID == items[0].get("ID"):
                    return reversed(segment_elements)

            # Accommodate edge case: There is one item, and the order needs to
            # inferred by the presence of a center line
            if len(items) == 1:
                only_item = items[0]
                only_item_id = only_item.get("ID")
                if frID == only_item.get("ID"):
                    # Reiterate over elements to see if a center line occurrs
                    # before the only item
                    for element in segment_elements:
                        # Normal case element is encountered before a center
                        # line
                        if element.get("ID") == only_item_id:
                            break
                        # Edge case: Center line encountered before the item
                        if element.tag == "CenterLine":
                            return reversed(segment_elements)
                # In case the item is referenced as a target, invert the
                # procedure by reversing the order
                if toID == only_item.get("ID"):
                    for element in reversed(segment_elements):
                        # Normal case element is encountered before a center
                        # line
                        if element.get("ID") == only_item_id:
                            break
                        # Edge case: Center line encountered after the target
                        # item
                        if element.tag == "CenterLine":
                            return reversed(segment_elements)

            # If no special case, return normal elements
            return segment_elements

        @contextmanager
        def temporary_config(model, config_key, temp_value):
            """Context manager to temporarily set pydantic model configurations.
            This is needed to construct piping network systems starting in an
            off page connector, that is temporarily an invalid target
            """
            original_value = model.model_config[config_key]
            model.model_config[config_key] = temp_value
            try:
                yield
            finally:
                model.model_config[config_key] = original_value

        # First pass over piping network systems to create all segments, and
        # connect implicit connections
        for pr_piping_network_system in self.proteus_root.findall("PipingNetworkSystem"):
            for pr_piping_network_segment in pr_piping_network_system.findall(
                "PipingNetworkSegment"
            ):
                # Create new, empty segment with data atributes
                the_segment = self.make_or_retrieve_class(
                    piping.PipingNetworkSegment,
                    pr_piping_network_segment.get("ID"),
                    pr_piping_network_segment,
                )

                # Iterate over elements and look for items and center lines,
                # i.e pipes
                connection_counter = 0
                last_was_connection = True
                last_outlet_index = None
                previous_final_connector_item = None
                previous_final_connector_node_idx = None
                previous_segment = None
                prev_prot_segment = None
                # Keep track of first and last connector (i.e. node and item)
                # to manage implicit connection. Leave as None if segment starts
                # or ends in connection (in which case it would have to
                # reference the final connection rather than be referenced)
                first_connector_item = None
                first_connector_node_idx = None
                last_connector_item = None
                last_connector_node_idx = None
                is_first = True  # Switch for first_connector
                for element in get_ordered_segment_elements(pr_piping_network_segment):
                    if element.tag in [
                        "PipingComponent",
                        "PipeOffPageConnector",
                        "PropertyBreak",
                    ]:
                        # If no center line was encountered since the last item,
                        # establish direct connection (Not for fist element as
                        # last_was_connection starts as True)
                        if not last_was_connection:
                            id = ".".join(
                                [
                                    pr_piping_network_system.get("ID"),
                                    pr_piping_network_segment.get("ID"),
                                    str(connection_counter),
                                ]
                            )
                            connection_counter += 1
                            the_pipe = self.make_or_retrieve_class(
                                piping.DirectPipingConnection, id, element
                            )
                            piping_toolkit.append_connection_to_unconnected_segment(
                                the_segment, the_pipe, last_outlet_index
                            )
                            last_was_connection = True

                        # Make class
                        class_name = element.get("ComponentClass")
                        kwargs = {}
                        # If no piping component found, treat as custom component
                        try:
                            the_class = getattr(piping, class_name)
                        except AttributeError:
                            the_class = piping.CustomPipingComponent
                            kwargs["typeName"] = class_name
                        nodes = self.retrieve_piping_nodes(element)
                        # TODO: for off page connector, implement reference
                        item = self.make_or_retrieve_class(
                            the_class,
                            element.get("ID"),
                            element,
                            nodes=nodes,
                            **kwargs,
                        )
                        cnct_node_indices = get_item_connection_nodes(element)
                        if cnct_node_indices["inlet"] is None:
                            inlet_node_index = None
                        else:
                            inlet_node_index = cnct_node_indices["inlet"] - 1
                        if cnct_node_indices["outlet"] is None:
                            last_outlet_index = None
                        else:
                            last_outlet_index = cnct_node_indices["outlet"] - 1
                        # Pass the outlet node to the new segment if it is empty
                        segment_isnt_empty = the_segment.items or the_segment.connections
                        outlet_node_index = None if segment_isnt_empty else last_outlet_index
                        # Workaround to be able to add an OPC as first element
                        if (
                            isinstance(item, piping.FlowInPipeOffPageConnector)
                            and not the_segment.items
                            and not the_segment.connections
                        ):
                            with temporary_config(
                                piping.PipingNetworkSegment,
                                "validate_assignment",
                                False,
                            ):
                                piping_toolkit.append_item_to_unconnected_segment(
                                    the_segment,
                                    item,
                                    inlet_node_index,
                                    outlet_node_index,
                                )
                        # Normal case
                        else:
                            piping_toolkit.append_item_to_unconnected_segment(
                                the_segment,
                                item,
                                inlet_node_index,
                                outlet_node_index,
                            )
                        if is_first:
                            first_connector_item = item
                            first_connector_node_idx = inlet_node_index
                            is_first = False
                        last_connector_item = item
                        last_connector_node_idx = last_outlet_index
                        last_was_connection = False

                    elif element.tag == "CenterLine":
                        # Two consecutive center lines are permitted. E.g. if
                        # two line representations belong to a pipe when it
                        # is interrupted, for example. In this case, only one
                        # pipe element should be created
                        if last_was_connection and the_segment.connections:
                            continue
                        else:
                            id = ".".join(
                                [
                                    pr_piping_network_system.get("ID"),
                                    pr_piping_network_segment.get("ID"),
                                    str(connection_counter),
                                ]
                            )
                            connection_counter += 1
                            the_pipe = self.make_or_retrieve_class(piping.Pipe, id, element)
                            piping_toolkit.append_connection_to_unconnected_segment(
                                the_segment, the_pipe, last_outlet_index
                            )
                            is_first = False
                            last_was_connection = True

                # Check if the segment has outside connections, and manage
                # missing direct connections
                connections = pr_piping_network_segment.findall("Connection")
                pr_seg_connection = connections[0] if connections else None
                from_needs_connection = False
                to_needs_connection = False
                if pr_seg_connection is not None:
                    frID = pr_seg_connection.get("FromID")
                    if frID is not None:
                        if frID in self._all_objects.keys():
                            if self._all_objects[frID] not in the_segment.items:
                                from_needs_connection = True
                        else:
                            from_needs_connection = True
                    toID = pr_seg_connection.get("ToID")
                    if toID is not None:
                        if toID in self._all_objects.keys():
                            if self._all_objects[toID] not in the_segment.items:
                                to_needs_connection = True
                        else:
                            to_needs_connection = True

                if from_needs_connection and not piping_toolkit.segment_is_free_and_unconnected(
                    the_segment, as_source=True
                ):
                    id = ".".join(
                        [
                            pr_piping_network_system.get("ID"),
                            pr_piping_network_segment.get("ID"),
                            str(connection_counter),
                        ]
                    )
                    connection_counter += 1
                    the_pipe = self.make_or_retrieve_class(
                        piping.DirectPipingConnection, id, element
                    )
                    piping_toolkit.append_connection_to_unconnected_segment(
                        the_segment,
                        the_pipe,
                        last_outlet_index,
                        insert_before=True,
                    )
                if to_needs_connection and not piping_toolkit.segment_is_free_and_unconnected(
                    the_segment
                ):
                    id = ".".join(
                        [
                            pr_piping_network_system.get("ID"),
                            pr_piping_network_segment.get("ID"),
                            str(connection_counter),
                        ]
                    )
                    connection_counter += 1
                    the_pipe = self.make_or_retrieve_class(
                        piping.DirectPipingConnection, id, element
                    )
                    piping_toolkit.append_connection_to_unconnected_segment(
                        the_segment, the_pipe, last_outlet_index
                    )
                    last_was_connection = True

                # Create implicit connection to predecessor if no connection
                # data given
                if last_was_connection:
                    last_connector_item = last_connector_node_idx = None

                connections = pr_piping_network_segment.findall("Connection")
                pr_seg_connection = connections[0] if connections else None
                pr_seg_has_from = False
                if pr_seg_connection is not None:
                    if pr_seg_connection.get("FromID") is not None:
                        pr_seg_has_from = True
                if (
                    (not pr_seg_has_from)
                    and first_connector_item is None
                    and previous_final_connector_item is not None
                ):
                    piping_toolkit.connect_piping_network_segment(
                        the_segment,
                        previous_final_connector_item,
                        connector_node_index=previous_final_connector_node_idx,
                        as_source=True,
                    )
                if prev_prot_segment is not None:
                    connections = pr_piping_network_segment.findall("Connection")
                    prev_seg_connection = connections[0] if connections else None
                    prev_pr_seg_has_to = False
                    if prev_seg_connection is not None:
                        if prev_seg_connection.get("ToID") is not None:
                            prev_pr_seg_has_to = True
                    if (
                        (not prev_pr_seg_has_to)
                        and previous_final_connector_item is None
                        and first_connector_item is not None
                    ):
                        piping_toolkit.connect_piping_network_segment(
                            previous_segment,
                            first_connector_item,
                            connector_node_index=first_connector_node_idx,
                            as_source=False,
                        )

                previous_final_connector_item = last_connector_item
                previous_final_connector_node_idx = last_connector_node_idx
                previous_segment = the_segment
                prev_prot_segment = pr_piping_network_segment

        # Second pass to connect the segments and create the systems
        dx_piping_network_systems = []
        for pr_piping_network_system in self.proteus_root.findall("PipingNetworkSystem"):
            pn_segments = []
            for pr_piping_network_segment in pr_piping_network_system.findall(
                "PipingNetworkSegment"
            ):
                dx_segment = self._all_objects[pr_piping_network_segment.get("ID")]
                connections = pr_piping_network_segment.findall("Connection")
                pr_seg_connection = connections[0] if connections else None
                src_item = None
                trg_item = None
                src_node_index = None
                trg_node_index = None

                # Check if connection IDs exists
                pr_seg_has_from = False
                pr_seg_has_to = False
                if pr_seg_connection is not None:
                    if pr_seg_connection.get("FromID") is not None:
                        pr_seg_has_from = True
                    if pr_seg_connection.get("ToID") is not None:
                        pr_seg_has_to = True

                # Find source and target items. Skip if the item references itsf
                if pr_seg_has_from:
                    src_item = self._all_objects[pr_seg_connection.get("FromID")]
                    if src_item in dx_segment.items:
                        src_item = None
                        src_node_index = None
                    else:
                        if pr_seg_connection.get("FromNode") is not None:
                            src_node_index = int(pr_seg_connection.get("FromNode")) - 1
                        else:
                            src_node_index = None
                if pr_seg_has_to:
                    trg_item = self._all_objects[pr_seg_connection.get("ToID")]
                    if trg_item in dx_segment.items:
                        trg_item = None
                        trg_node_index = None
                    else:
                        if pr_seg_connection.get("ToNode") is not None:
                            trg_node_index = int(pr_seg_connection.get("ToNode")) - 1
                        else:
                            trg_node_index = None

                # Perform connection
                if src_item is not None:
                    piping_toolkit.connect_piping_network_segment(
                        dx_segment,
                        src_item,
                        connector_node_index=src_node_index,
                        as_source=True,
                    )
                if trg_item is not None:
                    piping_toolkit.connect_piping_network_segment(
                        dx_segment,
                        trg_item,
                        connector_node_index=trg_node_index,
                        as_source=False,
                    )

                # Because model validation is temporarily suspended in case a
                # segment starts with an off page connector, check if the
                # segment references the off page connector as target
                if isinstance(dx_segment.targetItem, piping.FlowInPipeOffPageConnector):
                    msg = "Segment cannot reference FlowInPipeOffPageConnector as target. This may be caused if the segment consists only of the connector, which is not permitted."
                    raise piping_toolkit.DexpiCorruptPipingSegmentException(msg)

                pn_segments.append(dx_segment)

            the_network = self.make_or_retrieve_class(
                piping.PipingNetworkSystem,
                pr_piping_network_system.get("ID"),
                pr_piping_network_system,
                segments=pn_segments,
            )
            dx_piping_network_systems.append(the_network)

        return dx_piping_network_systems

    def parse_actuating_system(self) -> list:
        """Parse proteus actuating system to DEXPI actuating system classes.

        Returns
        -------
        list
            DEXPI actuating system objects that have been created.
        """
        actuating_systems = []
        for pr_actuating_system in self.proteus_root.findall("ActuatingSystem"):
            act_system_kwargs = {}
            for pr_actuating_system_component in pr_actuating_system.findall(
                "ActuatingSystemComponent"
            ):
                component_class = pr_actuating_system_component.get("ComponentClass")
                if component_class == "OperatedValveReference":
                    association = pr_actuating_system_component.find("Association")
                    if association is not None:
                        association_id = association.get("ItemID")
                        act_system_kwargs["operatedValveReference"] = self.make_or_retrieve_class(
                            instrumentation.OperatedValveReference,
                            pr_actuating_system_component.get("ID"),
                            pr_actuating_system_component,
                            valve=self._all_objects[association_id],
                        )
                elif component_class == "ControlledActuator":
                    act_system_kwargs["controlledActuator"] = self.make_or_retrieve_class(
                        instrumentation.ControlledActuator,
                        pr_actuating_system_component.get("ID"),
                        pr_actuating_system_component,
                    )
                elif component_class == "Positioner":
                    act_system_kwargs["positioner"] = self.make_or_retrieve_class(
                        instrumentation.Positioner,
                        pr_actuating_system_component.get("ID"),
                        pr_actuating_system_component,
                    )
            new_actuating_system = self.make_or_retrieve_class(
                instrumentation.ActuatingSystem,
                pr_actuating_system.get("ID"),
                pr_actuating_system,
                **act_system_kwargs,
            )
            actuating_systems.append(new_actuating_system)
        return actuating_systems

    def parse_process_signal_generating_systems(self) -> list:
        """Parses the process signal generating systems from a proteus xml
        element tree to DEXPI classes. Needs to be parsed before process
        instrumentation function.

        Returns
        -------
        list
            List of all system objects
        """
        p_s_generating_systems = []
        for p_s_generating_system in self.proteus_root.findall("ProcessSignalGeneratingSystem"):
            p_s_generating_systems_kwargs = {}
            for component in p_s_generating_system.findall(
                "ProcessSignalGeneratingSystemComponent"
            ):
                class_name = component.get("ComponentClass")
                if class_name == "Transmitter":
                    new_component = self.make_or_retrieve_class(
                        instrumentation.Transmitter,
                        component.get("ID"),
                        component,
                    )
                    p_s_generating_systems_kwargs["transmitter"] = new_component

                else:  # PrimaryElement
                    primary_element_kwargs = {}
                    if class_name == "InlinePrimaryElementReference":
                        association = component.find("Association")
                        if association is not None:
                            association_id = association.get("ItemID")
                            primary_element_kwargs["inlinePrimaryElement"] = self._all_objects[
                                association_id
                            ]
                    MyClass = getattr(instrumentation, class_name)
                    new_component = self.make_or_retrieve_class(
                        MyClass,
                        component.get("ID"),
                        component,
                        **primary_element_kwargs,
                    )
                    p_s_generating_systems_kwargs["primaryElement"] = new_component
            class_name = p_s_generating_system.get("ComponentClass")
            MyClass = getattr(instrumentation, class_name)
            new_generating_system = self.make_or_retrieve_class(
                MyClass,
                p_s_generating_system.get("ID"),
                p_s_generating_system,
                **p_s_generating_systems_kwargs,
            )
            p_s_generating_systems.append(new_generating_system)
        return p_s_generating_systems

    def parse_process_instrumentation_functions(self) -> list:
        """Parses the instrumentation from a proteus xml element tree to DEXPI
        classes.

        Returns
        -------
        list
            List of all instrumentation objects
        """

        # First pass: Create all instances for process instrumentation function
        for p_instrumentation_function in self.proteus_root.findall(
            "ProcessInstrumentationFunction"
        ):
            # create actuating function
            actuatingFunctions = []
            for actuating_function in p_instrumentation_function.findall("ActuatingFunction"):
                act_funct_kwargs = {}
                for association in actuating_function.findall("Association"):
                    association_id = association.get("ItemID")
                    # Reference to PipingNetworkSegment
                    if association.get("Type") == "is located in":
                        act_funct_kwargs["actuatingLocation"] = self._all_objects[association_id]
                    # Reference to ActuatingSystem
                    if association.get("Type") == "is fulfilled by":
                        act_funct_kwargs["systems"] = self._all_objects[association_id]

                new_actuating_function = self.make_or_retrieve_class(
                    instrumentation.ActuatingFunction,
                    actuating_function.get("ID"),
                    actuating_function,
                    **act_funct_kwargs,
                )
                actuatingFunctions.append(new_actuating_function)

            class_name = p_instrumentation_function.get("ComponentClass")
            MyClass = getattr(instrumentation, class_name)
            self.make_or_retrieve_class(
                MyClass,
                p_instrumentation_function.get("ID"),
                p_instrumentation_function,
                actuatingFunctions=actuatingFunctions,
            )

        for p_instrumentation_function in self.proteus_root.findall(
            "ProcessInstrumentationFunction"
        ):
            for information_flow in p_instrumentation_function.findall("InformationFlow"):
                class_name = information_flow.get("ComponentClass")
                MyClass = getattr(instrumentation, class_name)
                self.make_or_retrieve_class(
                    MyClass,
                    information_flow.get("ID"),
                    information_flow,
                )
            for p_signal_g_f in p_instrumentation_function.findall(
                "ProcessSignalGeneratingFunction"
            ):
                self.make_or_retrieve_class(
                    instrumentation.ProcessSignalGeneratingFunction,
                    p_signal_g_f.get("ID"),
                    p_signal_g_f,
                )
            for actuating_e_f in p_instrumentation_function.findall("ActuatingElectricalFunction"):
                self.make_or_retrieve_class(
                    instrumentation.ActuatingElectricalFunction,
                    actuating_e_f.get("ID"),
                    actuating_e_f,
                )
            for signal_o_p_c in p_instrumentation_function.findall("SignalOffPageConnector"):
                class_name = signal_o_p_c.get("ComponentClass")
                MyClass = getattr(instrumentation, class_name)
                self.make_or_retrieve_class(
                    MyClass,
                    signal_o_p_c.get("ID"),
                    signal_o_p_c,
                )
            # From the DEXPI documentation it is not clear whether ActuatingElectricalSystem
            # is a sub element of ProcessInstrumentationFunction or of
            # ActuatingElectricalFunction. Implementation assumes ProcessInstrumentationFunction.
            for actuating_e_s in p_instrumentation_function.findall("ActuatingElectricalSystem"):
                a_e_s_component = actuating_e_s.find("ActuatingElectricalSystemComponent")
                if a_e_s_component is not None:
                    new_converter = self.make_or_retrieve_class(
                        instrumentation.ElectronicFrequencyConverter,
                        a_e_s_component.get("ID"),
                        a_e_s_component,
                    )
                else:
                    new_converter = None
                self.make_or_retrieve_class(
                    instrumentation.ActuatingElectricalSystem,
                    actuating_e_s.get("ID"),
                    actuating_e_s,
                    electronicFrequencyConverter=new_converter,
                )

        # Second pass: Connect all instances of the process instrumentation function.
        p_instrumentation_functions = []
        for p_instrumentation_function in self.proteus_root.findall(
            "ProcessInstrumentationFunction"
        ):
            p_instrumentation_f_id = p_instrumentation_function.get("ID")

            # SignalConveyingFunctions
            signalConveyingFunctions = []
            for signal_c_f in p_instrumentation_function.findall("InformationFlow"):
                signal_c_f_id = signal_c_f.get("ID")
                for association in signal_c_f.findall("Association"):
                    association_id = association.get("ItemID")
                    if association.get("Type") == "has logical start":
                        self._all_objects[signal_c_f_id].source = self._all_objects[association_id]
                    if association.get("Type") == "has logical end":
                        self._all_objects[signal_c_f_id].target = self._all_objects[association_id]
                signalConveyingFunctions.append(self._all_objects[signal_c_f_id])
            self._all_objects[
                p_instrumentation_f_id
            ].signalConveyingFunctions = signalConveyingFunctions

            # ProcessSignalGeneratingFunctions
            processSignalGeneratingFunctions = []
            for p_signal_g_f in p_instrumentation_function.findall(
                "ProcessSignalGeneratingFunction"
            ):
                p_signal_g_f_id = p_signal_g_f.get("ID")
                for association in p_signal_g_f.findall("Association"):
                    association_id = association.get("ItemID")
                    if association.get("Type") == "is located in":
                        self._all_objects[p_signal_g_f_id].sensingLocation = self._all_objects[
                            association_id
                        ]
                    if association.get("Type") == "is fulfilled by":
                        self._all_objects[p_signal_g_f_id].systems = self._all_objects[
                            association_id
                        ]
                processSignalGeneratingFunctions.append(self._all_objects[p_signal_g_f_id])
            self._all_objects[
                p_instrumentation_f_id
            ].processSignalGeneratingFunctions = processSignalGeneratingFunctions

            # ActuatingElectricalFunctions
            actuatingElectricalFunctions = []
            for actuating_e_f in p_instrumentation_function.findall("ActuatingElectricalFunction"):
                actuating_e_f_id = actuating_e_f.get("ID")
                for association in actuating_e_f.findall("Association"):
                    association_id = association.get("ItemID")
                    if association.get("Type") == "is located in":
                        self._all_objects[
                            actuating_e_f_id
                        ].actuatingElectricalLocation = self._all_objects[association_id]
                    if association.get("Type") == "is fulfilled by":
                        self._all_objects[actuating_e_f_id].systems = self._all_objects[
                            association_id
                        ]
                actuatingElectricalFunctions.append(self._all_objects[actuating_e_f_id])
            self._all_objects[
                p_instrumentation_f_id
            ].actuatingElectricalFunctions = actuatingElectricalFunctions

            # SignalOffPageConnectors
            signalOffPageConnectors = []
            for signal_o_p_c in p_instrumentation_function.findall("SignalOffPageConnector"):
                signal_o_p_c_id = signal_o_p_c.get("ID")
                for s_o_p_c_reference in signal_o_p_c.findall("SignalOffPageConnectorReference"):
                    class_name = s_o_p_c_reference.get("ComponentClass")
                    s_o_p_c_reference_kwargs = {}
                    if class_name == "SignalOffPageConnectorObjectReference":
                        association = s_o_p_c_reference.find("Association")
                        if association is not None:
                            association_id = association.get("ItemID")
                            if association.get("type") == "refers to":
                                s_o_p_c_reference_kwargs["referencedConnector"] = self._all_objects[
                                    association_id
                                ]
                    MyClass = getattr(instrumentation, class_name)
                    connector_reference = self.make_or_retrieve_class(
                        MyClass,
                        s_o_p_c_reference.get("ID"),
                        s_o_p_c_reference,
                        **s_o_p_c_reference_kwargs,
                    )
                self._all_objects[signal_o_p_c_id].connectorReference = connector_reference
                signalOffPageConnectors.append(self._all_objects[signal_o_p_c_id])
            self._all_objects[p_instrumentation_f_id].signalConnectors = signalOffPageConnectors

            p_instrumentation_functions.append(self._all_objects[p_instrumentation_f_id])
        return p_instrumentation_functions

    def parse_instrumentation_loop_functions(self) -> list:
        """Parse proteus instrumentation loop function to DEXPI instrumentation
        loop function classes.

        Returns:
            i_loop_functions(list): DEXPI instrumentation loop
                function objects that have been created."""
        i_loop_functions = []
        for i_loop_function in self.proteus_root.findall("InstrumentationLoopFunction"):
            p_intrumentation_functions = []
            for association in i_loop_function.findall("Association"):
                association_id = association.get("ItemID")
                # ProcessInstrumentationFunction
                if association.get("Type") == "is a collection including":
                    p_intrumentation_functions.append(self._all_objects[association_id])

            new_i_loop_functions = self.make_or_retrieve_class(
                instrumentation.InstrumentationLoopFunction,
                i_loop_function.get("ID"),
                processInstrumentationFunctions=p_intrumentation_functions,
            )
            i_loop_functions.append(new_i_loop_functions)
        return i_loop_functions

    def retrieve_piping_nodes(self, connection_point_owner: ET.Element):
        """Get a list of piping nodes associated to a proteus connection_point
        owner (i.e. PipingNodeOwner in Dexpi). Create piping nodes new if
        non_existent and add them to self._piping_nodes_dict, or get them from
        self._piping_nodes_dict

        Returns
        -------
            list(PipingNode)
                List of piping node objects associated to the connection_point_owner
        """
        piping_nodes = []
        for connection_point in connection_point_owner.findall("ConnectionPoints"):
            for node in connection_point.findall("Node"):
                if node.get("Type") == "process":
                    piping_node = self.make_or_retrieve_class(
                        piping.PipingNode, node.get("ID"), node
                    )
                    piping_nodes.append(piping_node)
        return piping_nodes

    def make_or_retrieve_class(
        self,
        class_type,
        proteus_id: str,
        proteus_element: ET.Element = None,
        **kwargs,
    ):
        """
        Creates a class with the id and the class type. If an object with this
        ID has been created before, the method returns this object, provided the
        class type matches. An exception is thrown otherwise. If no object with
        this ID is found, a new object is created and added to the _all_classes
        dictionary.

        Parameters
        ----------
            class_type: Any
                type of the class to be created
            proteus_id : str
                ID of the object for the lookup table. Should be the proteus id
                if available
            proteus_element : ET.Element, optional
                Corresponding proteus element, from which the generic attributes
                are parsed if not None
            kwargs:
                keyword arguments to be passed to the constructor
        Returns
        -------
            class_type
                object corresponding to the ID

        """
        if proteus_id in list(self._all_objects.keys()):
            if type(self._all_objects[proteus_id]) is not class_type:
                msg = (
                    f"Class type of entry for ID {proteus_id} is "
                    f"{type(self._all_objects[proteus_id])} and doesnt match"
                    f"class type {class_type} in argument"
                )
                raise TypeError(msg)
            else:
                return self._all_objects[proteus_id]
        else:
            # Parse generic attributes if proteus element is given.
            if proteus_element is not None:
                generic_attributes = self.parse_generic_attributes(class_type, proteus_element)
                kwargs.update(generic_attributes)

            # Patch unavailable class type for custom components
            if "Custom" in str(class_type) and "typeName" not in kwargs:
                kwargs["typeName"] = ""

            new_object = class_type(**kwargs)
            self._all_objects[proteus_id] = new_object
            return new_object

    def parse_generic_attributes(self, component_class, proteus_component: ET) -> dict:
        """Parse generic attributes from xml tree to DEXPI data classes.

        Args:
            component_class: DEXPI class for which we want to parse attributes
            proteus_attributes (ET): Proteus element tree of the DEXPI class.

        Returns:
            dict: attributes, DEXPI data classes
        """
        attributes = {}
        component_attributes = component_class.model_fields
        # We assume all DEXPI attributes are stored as GenericAttributes in proteus
        # Return none in case no attributes are found
        if proteus_component.find("GenericAttributes") is None:
            return {}
        multi_language_strings = {}
        for attribute_set in proteus_component.findall("GenericAttributes"):
            valid_attribute_lists = [
                "DexpiAttributes",
                "CustomAttributes",
                "DexpiCustomAttributes",
            ]
            if attribute_set.get("Set") not in valid_attribute_lists:
                continue
            for attribute in attribute_set:
                # Edit proteus attribute name to correspond to DEXPI class field.
                name = attribute.get("Name")
                name = name.removesuffix("AssignmentClass")
                name = name.removesuffix("Specialization")
                name = name[0].lower() + name[1:]
                # Only parse an attribute if it exists both in proteus and DEXPI.
                if name in component_attributes:
                    value = attribute.get("Value")
                    # skip attribute if value is not given
                    if value is None:
                        continue
                    field_annotation = component_attributes[name].annotation
                    if isinstance(field_annotation, types.UnionType):
                        unit = component_attributes[name].annotation.__args__[0]
                    else:
                        unit = component_attributes[name].annotation
                    unit_name = unit.__name__
                    if unit is str:
                        attributes[name] = str(value)
                    elif unit is int:
                        attributes[name] = int(value)
                    elif unit is dataTypes.MultiLanguageString:
                        if name not in multi_language_strings.keys():
                            multi_language_strings[name] = []
                        single_language_string = dataTypes.SingleLanguageString(
                            language=attribute.get("Language"),
                            value=attribute.get("Value"),
                        )
                        multi_language_strings[name].append(single_language_string)
                    elif hasattr(physicalQuantities, unit_name):
                        # null value for a physical quantity is currently not implemented
                        unit_name = unit_name.removeprefix("Nullable")
                        unit_class = getattr(physicalQuantities, unit_name)
                        dexpi_attribute = unit_class(
                            value=value,
                            unit=unit_class.model_fields["unit"]
                            .annotation[attribute.get("Units")]
                            .value,
                        )
                        attributes[name] = dexpi_attribute
                    elif hasattr(enumerations, unit_name):
                        unit_class = getattr(enumerations, unit_name)
                        attributes[name] = unit_class[value]
                    else:
                        raise Exception(f"Attribute {name} not defined.")
        for attribute_name in multi_language_strings.keys():
            single_language_strings = multi_language_strings[attribute_name]
            multi_language_string = dataTypes.MultiLanguageString(
                singleLanguageStrings=single_language_strings
            )
            attributes[attribute_name] = multi_language_string
        return attributes
