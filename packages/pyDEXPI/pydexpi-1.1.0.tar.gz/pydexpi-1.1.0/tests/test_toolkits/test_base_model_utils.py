"""This test module contains tests for the base_model_utils module"""

import pytest

from pydexpi.dexpi_classes.pydantic_classes import ActuatingSystem, Equipment, PipingNetworkSegment
from pydexpi.toolkits import base_model_utils as bmt


def test_get_composition_attributes(simple_pns_factory):
    """Test function to retrieve composition attributes."""
    # Define the expected set of composition attributes
    attributes = bmt.get_composition_attributes(simple_pns_factory())
    # Check if all composition attributes were found
    comp_attrs = {"connections", "items", "customAttributes"}
    assert set(attributes) == comp_attrs


def test_get_reference_attributes(simple_pns_factory):
    """Test function to retrieve reference attributes."""
    attributes = bmt.get_reference_attributes(simple_pns_factory())
    # Define the expected set of reference attributes
    ref_attrs = {"sourceNode", "sourceItem", "targetNode", "targetItem"}
    # Check if all reference attributes were found
    assert set(attributes) == ref_attrs


def test_get_data_attributes(simple_pns_factory):
    """Test function to retrieve data attributes."""
    attributes = bmt.get_data_attributes(simple_pns_factory())
    # Define the expected set of data attributes
    data_attribute_names = {
        "colorCode",
        "flowDirection",
        "fluidCode",
        "heatTracingType",
        "heatTracingTypeRepresentation",
        "inclination",
        "insulationThickness",
        "insulationType",
        "jacketedPipe",
        "lowerLimitHeatTracingTemperature",
        "nominalDiameterNumericalValueRepresentation",
        "nominalDiameterRepresentation",
        "nominalDiameterStandard",
        "nominalDiameterTypeRepresentation",
        "onHold",
        "operatingTemperature",
        "pipingClassCode",
        "pressureTestCircuitNumber",
        "primarySecondaryPipingNetworkSegment",
        "segmentNumber",
        "siphon",
        "slope",
    }
    # Check if all data attributes were found
    assert set(attributes) == data_attribute_names


def test_get_attributes_with_category(simple_pns_factory):
    """Test the function get get_attributes_with_category, though mostly already
    covered by implementation functions with data, composition, and reference.
    """
    assert bmt._get_attributes_with_category(simple_pns_factory(), "data")
    assert not bmt._get_attributes_with_category(simple_pns_factory(), "something else")


def test_get_dexpi_class() -> None:
    """Test the function get_dexpi_class."""
    assert bmt.get_dexpi_class("PipingNetworkSegment") == PipingNetworkSegment
    assert bmt.get_dexpi_class("Equipment") == Equipment
    assert bmt.get_dexpi_class("ActuatingSystem") == ActuatingSystem

    with pytest.raises(AttributeError):
        bmt.get_dexpi_class("NonExistentClass")


def test_get_dexpi_class_from_uri() -> None:
    pns = PipingNetworkSegment()
    assert bmt.get_dexpi_class_from_uri(pns.uri) == PipingNetworkSegment

    equipment = Equipment()
    assert bmt.get_dexpi_class_from_uri(equipment.uri) == Equipment

    actuating_system = ActuatingSystem()
    assert bmt.get_dexpi_class_from_uri(actuating_system.uri) == ActuatingSystem

    with pytest.raises(AttributeError):
        bmt.get_dexpi_class_from_uri("http://example.com/NonExistentClass")
