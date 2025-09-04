from pydexpi.loaders.proteus_serializer import ProteusSerializer
from pydexpi.loaders.proteus_serializer.core import ErrorLevels
from pydexpi.toolkits import base_model_utils as bmu, model_toolkit as mt, piping_toolkit as pt


def test_parse_proteus_to_dexpi():
    """Parse proteus root tree to dexpi classes."""
    path = "data"
    filename = "C01V04-VER.EX01"
    serializer = ProteusSerializer()
    example_dexpi = serializer.load(path, filename)
    # Check if total number of objects is still correct (for equipment, piping,
    # and instrumentation)
    assert len(mt.get_all_instances_in_model(example_dexpi)) == 214
    # Check the piping network segments
    for system in example_dexpi.conceptualModel.pipingNetworkSystems:
        for segment in system.segments:
            assert (
                pt.piping_network_segment_validity_check(segment)[0] == pt.PipingValidityCode.VALID
            )
    # Run some misc tests
    assert len(example_dexpi.conceptualModel.actuatingSystems) == 3
    assert (
        example_dexpi.conceptualModel.taggedPlantItems[0].__class__.__name__ == "PlateHeatExchanger"
    )

    # Assert that there are only ErrorLevels.INFO in the parser
    error_registry = serializer.proteus_loader.error_registry
    non_info_errors = error_registry.get_errors(
        [ErrorLevels.ERROR, ErrorLevels.WARNING, ErrorLevels.CRITICAL]
    )
    assert len(non_info_errors) == 0


def test_parse_generic_attributes(loaded_example_dexpi):
    """Test if DEXPI generic attributes are parsed correctly from proteus."""
    dexpi_model = loaded_example_dexpi
    assert dexpi_model.conceptualModel.taggedPlantItems[0].plateHeight.unit.value == "mm"
    assert float(dexpi_model.conceptualModel.taggedPlantItems[0].plateHeight.value) == 850
    assert (
        dexpi_model.conceptualModel.taggedPlantItems[4]
        .nozzles[0]
        .nodes[0]
        .nominalDiameterRepresentation
        == "DN 80"
    )


def test_parse_all_attributes(loaded_example_dexpi):
    """Count all None attributes in the loaded dexpi model and make sure they are the expected amount."""
    all_instances = mt.get_all_instances_in_model(loaded_example_dexpi)

    # Count all attributes that are None
    attr_count = 0
    not_none_fields = 0
    for instance in all_instances:
        raw_attrs = bmu.get_data_attributes(instance)
        for fld_value in raw_attrs.values():
            if fld_value is not None:
                not_none_fields += 1
                if isinstance(fld_value, list):
                    attr_count += len(fld_value)
                else:
                    attr_count += 1

    assert attr_count == 732
    assert not_none_fields == 732
