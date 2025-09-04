"""
JSON Loader module for DEXPI model serialization and deserialization.

This module provides functionality to serialize DEXPI models to JSON format
and deserialize JSON data back into DEXPI model objects. It includes classes
for encoding models to dictionaries and decoding dictionaries to models.
"""

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import pydexpi.toolkits.base_model_utils as bmt
from pydexpi.dexpi_classes.pydantic_classes import DexpiBaseModel, DexpiDataTypeBaseModel
from pydexpi.loaders.serializer import Serializer
from pydexpi.toolkits.base_model_utils import (
    get_composition_attributes,
    get_data_attributes,
    get_reference_attributes,
)


class JsonSerializer(Serializer):
    """
    JSON implementation of the Serializer interface for DEXPI models.

    This class provides methods to save DEXPI models to JSON files and load
    DEXPI models from JSON files. It handles the conversion between DEXPI model
    objects and JSON-serializable dictionaries.
    """

    def __init__(self) -> None:
        """Initialize a new JSONLoader by constructing encoder and decoder objects as attributes."""
        super().__init__()
        self.encoder = DexpiToDictEncoder()
        self.decoder = DictToDexpiDecoder()

    def save(self, model: DexpiBaseModel, dir_path: str | Path, filename: str) -> None:
        """
        Save a DEXPI model to a JSON file.

        Parameters
        ----------
        model : DexpiBaseModel
            The DEXPI model to save
        dir_path : str or Path
            Directory path where the file will be saved
        filename : str
            Name of the file without extension

        Returns
        -------
        None
        """
        # Add json ending if not explicitly given
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        path = Path(dir_path) / filename
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.model_to_dict(model), file, indent=4, ensure_ascii=False)

    def load(self, dir_path: str | Path, filename: str) -> DexpiBaseModel:
        """
        Load a DEXPI model from a JSON file.

        Parameters
        ----------
        dir_path : str or Path
            Directory path where the file is located
        filename : str
            Name of the file without extension

        Returns
        -------
        DexpiBaseModel
            The loaded DEXPI model

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist
        """
        # Add json ending if not explicitly given
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        path = Path(dir_path) / filename
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist.")

        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        return self.dict_to_model(data, external_refs={})

    def model_to_dict(self, model: DexpiBaseModel) -> dict:
        """
        Convert a DEXPI model to a JSON serializable dictionary.

        Parameters
        ----------
        model : DexpiBaseModel
            The DEXPI model to convert

        Returns
        -------
        dict
            A dictionary representation of the DEXPI model
        """
        return self.encoder.dexpi_element_to_dict(model)

    def dict_to_model(self, data: dict, external_refs: dict = None) -> DexpiBaseModel:
        """
        Convert a dictionary to a DEXPI model.

        Parameters
        ----------
        data : dict
            Dictionary representation of the DEXPI model
        external_refs : dict, optional
            Dictionary of external references, by default None

        Returns
        -------
        DexpiBaseModel
            The created DEXPI model
        """
        return self.decoder.dict_to_dexpi_element(data, external_refs)


class DexpiToDictEncoder:
    """
    Encoder class for converting DEXPI models to JSON-serializable dictionaries.

    This class contains static methods to convert DEXPI model objects
    and their attributes to dictionaries that can be serialized to JSON.
    """

    @staticmethod
    def dexpi_element_to_dict(element: DexpiBaseModel | DexpiDataTypeBaseModel) -> dict:
        """
        Convert a DEXPI model element to a JSON serializable dictionary.

        Parameters
        ----------
        element : DexpiBaseModel or DexpiDataTypeBaseModel
            The element to convert

        Returns
        -------
        dict
            A dictionary representation of the element
        """

        # Get all attributes of the element by type
        raw_comp_attributes = get_composition_attributes(element)
        raw_reference_attributes = get_reference_attributes(element)
        raw_data_attributes = get_data_attributes(element)

        # Initialize dictionaries to hold the unpacked attributes for later constructor kwargs use
        comp_attribute_dict = {}
        reference_attribute_dict = {}
        data_attribute_dict = {}

        # Package composition attributes. This is done recursively with dexpi_element_to_dict
        # to ensure that nested elements are also converted to dictionaries.
        for attr, attr_val in raw_comp_attributes.items():
            comp_attribute_dict[attr] = _call_on_list_or_object_or_none(
                DexpiToDictEncoder.dexpi_element_to_dict, attr_val
            )

        # Package reference attributes. For reference attributes, we only store the IDs.
        for attr, attr_val in raw_reference_attributes.items():
            reference_attribute_dict[attr] = _call_on_list_or_object_or_none(
                lambda x: x.id, attr_val
            )

        # Package data attributes with package_data_attribute.
        for attr, attr_val in raw_data_attributes.items():
            data_attribute_dict[attr] = _call_on_list_or_object_or_none(
                DexpiToDictEncoder.package_data_attribute, attr_val
            )

        # Combine all attributes into a single dictionary. Add the type of the element and the ID if
        # it exists.
        element_dict = {"uri": element.uri}
        if isinstance(element, DexpiBaseModel):
            element_dict["id"] = element.id
        if comp_attribute_dict:
            element_dict["composition"] = comp_attribute_dict
        if reference_attribute_dict:
            element_dict["reference"] = reference_attribute_dict
        if data_attribute_dict:
            element_dict["data"] = data_attribute_dict

        return element_dict

    @staticmethod
    def package_data_attribute(
        attribute_val: DexpiDataTypeBaseModel | str | int | float | datetime,
    ) -> dict | str | int | float:
        """
        Unpack a data attribute to a JSON serializable format.

        Uses the correct method to convert the attribute value based on its type. If it is a DEXPI
        DataTypeBaseModel, it will be converted to a dictionary using dexpi_element_to_dict.
        Primitive types (str, int, float) are returned as is, and datetime objects are converted to
        strings.

        Parameters
        ----------
        attribute_val : DexpiDataTypeBaseModel or str or int or float or datetime
            The attribute value to package

        Returns
        -------
        dict or str or int or float
            JSON serializable representation of the attribute

        Raises
        ------
        TypeError
            If the attribute has an unsupported data type
        """
        if isinstance(attribute_val, DexpiDataTypeBaseModel):
            return DexpiToDictEncoder.dexpi_element_to_dict(attribute_val)
        elif isinstance(attribute_val, str | int | float):
            return attribute_val
        elif isinstance(attribute_val, datetime):
            return str(attribute_val)
        else:
            raise TypeError(f"Unsupported data type: {type(attribute_val)}")


class DictToDexpiDecoder:
    """
    Decoder class for converting dictionaries to DEXPI model objects.

    This class handles the reconstruction of DEXPI model objects from
    dictionary representations, including resolving object references.
    """

    def __init__(self) -> None:
        """Initialize a new decoder with an empty object registry.

        This registry is used to keep track of objects created during the
        compositional pass, allowing for reference resolution in the
        reference pass."""
        self.object_registry = {}

    def dict_to_dexpi_element(self, data: dict, external_refs: dict = None) -> DexpiBaseModel:
        """
        Convert a dictionary to a DEXPI model element.

        This is done in two passes:
        1. Compositional pass: Create the DEXPI model objects and their attributes and resolve
           compositional and data dependencies.
        2. Reference pass: Once all objects are created, resolve reference relationships by
           retrieving referenced objects from the object registry.

        Parameters
        ----------
        data : dict
            Dictionary representation of the DEXPI model
        external_refs : dict, optional
            Dictionary of external references, by default None

        Returns
        -------
        DexpiBaseModel
            The reconstructed DEXPI model
        """
        # Reset and set the object registry
        self.object_registry = external_refs if external_refs else {}

        # Create the object with compositional and data attributes
        the_object = self._compositional_pass(data)

        # Resolve references in the object
        self._reference_pass(data)
        return the_object

    def _compositional_pass(self, data: dict) -> DexpiBaseModel:
        """Recursively convert dictionaries to nested DEXPI model elements.

        This method handles the creation of DEXPI model objects including
        their composition and data attributes but not references.

        Parameters
        ----------
        data : dict
            Dictionary representation of the DEXPI model

        Returns
        -------
        DexpiBaseModel
            The constructed DEXPI model without resolved references
        """

        # Retrieve the model class from the Dexpi classes
        model_uri = data.get("uri")
        model_class = bmt.get_dexpi_class_from_uri(model_uri)

        raw_comp_attrs = data.get("composition", {})

        # Prepare the composition attributes for the model
        comp_attr_args = {}
        for attr, attr_val in raw_comp_attrs.items():
            comp_attr_args[attr] = _call_on_list_or_object_or_none(
                self._compositional_pass, attr_val
            )

        # Prepare the data attributes for the model

        raw_data_attrs = data.get("data", {})

        data_attr_args = {}
        for attr, attr_val in raw_data_attrs.items():
            if isinstance(attr_val, list):
                data_attr_args[attr] = [self._unpack_data_attribute(item) for item in attr_val]
            else:
                data_attr_args[attr] = self._unpack_data_attribute(attr_val)

        # Construct the new object with the model class and attributes by stacking the arguments
        model_id = data.get("id")
        model_args = {"id": model_id} if model_id else {}
        model_args.update(comp_attr_args)
        model_args.update(data_attr_args)

        # Create an instance of the model class with the arguments
        new_object = model_class(**model_args)

        # Register the new object in the object registry for the reference pass if there is an ID
        # If there isn't, then the object cannot be referenced, so it doesn't need to be registered.
        if model_id is not None:
            self.object_registry[new_object.id] = new_object

        return new_object

    def _unpack_data_attribute(self, attribute_val: dict | str | int | float) -> Any:
        """
        Unpack data attributes from a dictionary to the appropriate type.

        Parameters
        ----------
        attribute_val : dict or str or int or float
            The attribute value to unpack

        Returns
        -------
        Any
            The unpacked value, either a DEXPI model or primitive type
        """

        # If data type base model, unpack as a DexpiBaseModel element
        if isinstance(attribute_val, dict):
            return self._compositional_pass(attribute_val)
        # Else, return as is if it's a primitive type
        else:
            return attribute_val

    def _reference_pass(self, data: dict) -> None:
        """
        Resolve references in the data dictionary.

        This method resolves object references using the object registry
        after all objects have been created in the compositional pass.

        Parameters
        ----------
        data : dict
            Dictionary representation of the DEXPI model

        Returns
        -------
        None
        """

        # Retrieve the model class from the Dexpi classes
        object_id = data.get("id")

        the_object = self.object_registry.get(object_id)

        raw_reference_attrs = data.get("reference", {})

        for attr, attr_val in raw_reference_attrs.items():
            resolved_refs = _call_on_list_or_object_or_none(
                self.object_registry.__getitem__, attr_val
            )
            setattr(the_object, attr, resolved_refs)

        # Call on all composition in the hierarchy
        raw_comp_attrs = data.get("composition", {})

        for attr, attr_val in raw_comp_attrs.items():
            _call_on_list_or_object_or_none(self._reference_pass, attr_val)


def _call_on_list_or_object_or_none(func: Callable, obj: Any) -> Any:
    """
    Call a function on an object, list of objects, or return None if the object is None.

    This helper function provides a unified interface for applying a function to
    either a single object or a list of objects, handling None values appropriately.

    Parameters
    ----------
    func : Callable
        The function to call on the object.
    obj : Any
        The object to process, which can be a list, a single object, or None.

    Returns
    -------
    Any
        The result of the function call on the object, a list of results if the input
        was a list, or None if the input was None.
    """
    if obj is None:
        return None
    elif isinstance(obj, list):
        return [func(item) for item in obj]
    else:
        return func(obj)
