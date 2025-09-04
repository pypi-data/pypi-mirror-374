from collections.abc import Callable

import networkx as nx
import pytest

from pydexpi.dexpi_classes.pydantic_classes import DexpiModel, PipingNetworkSegment
from pydexpi.loaders.json_serializer import JsonSerializer
from pydexpi.loaders.ml_graph_loader import MLGraphLoader


def test_json_loader_dict_simple_pns(simple_pns_factory: Callable[[], PipingNetworkSegment]):
    """Test if the JSONLoader can convert a simple PNS to dict and back."""

    json_loader = JsonSerializer()
    simple_pns = simple_pns_factory()

    # Convert PNS to dict
    pns_dict = json_loader.model_to_dict(simple_pns)

    # Convert dict back to PNS
    reconstructed_pns = json_loader.dict_to_model(pns_dict)

    # Check if the original and reconstructed PNS have equal features
    assert len(simple_pns.items) == len(reconstructed_pns.items)
    assert len(simple_pns.connections) == len(reconstructed_pns.connections)
    assert simple_pns.items[0].nodes[0].id == reconstructed_pns.items[0].nodes[0].id

    # Compare via identity, which references the object ids
    assert simple_pns.connections[1].sourceItem == reconstructed_pns.connections[1].sourceItem
    assert simple_pns.connections[1].targetItem == reconstructed_pns.connections[1].targetItem
    assert simple_pns.connections[1].sourceNode == reconstructed_pns.connections[1].sourceNode


def test_json_loader_on_full_model(loaded_example_dexpi: DexpiModel):
    """Test if the JSONLoader can convert a full Dexpi model to dict and back."""

    json_loader = JsonSerializer()

    # Convert Dexpi model to dict
    json_dict = json_loader.model_to_dict(loaded_example_dexpi)

    # Convert dict back to Dexpi model
    reconstructed_model = json_loader.dict_to_model(json_dict)

    # Compare via graph export
    gr_loader = MLGraphLoader()
    orig_graph = gr_loader.dexpi_to_graph(loaded_example_dexpi)
    recon_graph = gr_loader.dexpi_to_graph(reconstructed_model)

    # Check if the original and reconstructed graphs are isomorphic
    is_isomorphic = nx.is_isomorphic(
        orig_graph,
        recon_graph,
        node_match=lambda n1, n2: n1 == n2,
        edge_match=lambda e1, e2: e1 == e2,
    )
    assert is_isomorphic, "The original and reconstructed graphs are not isomorphic."

    # Check via the json export. It should be the same as the original dict.
    reconstructed_json_dict = json_loader.model_to_dict(reconstructed_model)
    assert json_dict == reconstructed_json_dict, (
        "The original and reconstructed JSON dicts do not match."
    )


def test_load_save_json(loaded_example_dexpi: DexpiModel, tmp_path: str):
    """Test if the JSONLoader can save and load a Dexpi model correctly."""

    json_loader = JsonSerializer()

    # Save the dict to a file
    json_loader.save(loaded_example_dexpi, tmp_path, "test_model.json")

    # Load the dict from the file
    reconstructed_model = json_loader.load(tmp_path, "test_model.json")

    # Compare via graph export
    gr_loader = MLGraphLoader()
    orig_graph = gr_loader.dexpi_to_graph(loaded_example_dexpi)
    recon_graph = gr_loader.dexpi_to_graph(reconstructed_model)

    # Check if the original and reconstructed graphs are isomorphic
    is_isomorphic = nx.is_isomorphic(
        orig_graph,
        recon_graph,
        node_match=lambda n1, n2: n1 == n2,
        edge_match=lambda e1, e2: e1 == e2,
    )
    assert is_isomorphic, "The original and reconstructed graphs are not isomorphic."

    # Test for non-existent file ending
    json_loader.save(loaded_example_dexpi, tmp_path, "test_model2")

    # Load the dict from the file and check that no error is raised
    _ = json_loader.load(tmp_path, "test_model2.json")
    _ = json_loader.load(tmp_path, "test_model2")

    # Test loadin a non-existent file
    with pytest.raises(FileNotFoundError):
        json_loader.load(tmp_path, "non_existent_file.json")
