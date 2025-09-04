from pydexpi.toolkits import model_toolkit as mt, piping_toolkit as pt


# @pytest.mark.dependency(depends=["test_load_proteus"])
def test_parse_proteus_to_dexpi(loaded_example_dexpi):
    """Parse proteus root tree to dexpi classes."""
    dexpi_model = loaded_example_dexpi
    # Check if total number of objects is still correct (for equipment, piping,
    # and instrumentation)
    assert len(mt.get_all_instances_in_model(dexpi_model)) == 214
    # Check the piping network segments
    for system in dexpi_model.conceptualModel.pipingNetworkSystems:
        for segment in system.segments:
            assert (
                pt.piping_network_segment_validity_check(segment)[0] == pt.PipingValidityCode.VALID
            )
    # Run some misc tests
    assert len(dexpi_model.conceptualModel.actuatingSystems) == 3
    assert (
        dexpi_model.conceptualModel.taggedPlantItems[0].__class__.__name__ == "PlateHeatExchanger"
    )


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
