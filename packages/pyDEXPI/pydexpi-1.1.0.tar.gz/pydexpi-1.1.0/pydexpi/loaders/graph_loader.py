from abc import ABC, abstractmethod

from networkx import Graph

from pydexpi.dexpi_classes.dexpiModel import DexpiModel


class NXGraphLoader(ABC):
    """
    Abstract base class for loading and transforming NX graphs and Dexpi models.

    Provides an interface for parsing between pyDEXPI models and NetworkX graph
    representations.
    """

    @abstractmethod
    def dexpi_to_graph(self, dexpi_model: DexpiModel) -> Graph:
        """
        Parse a pyDEXPI model into a NetworkX graph representation.

        Parameters
        ----------
        pydexpi_model : DexpiModel
            The pyDEXPI model to be parsed into a NetworkX graph.

        Returns
        -------
        nx.Graph
            The parsed NetworkX graph representation of the pyDEXPI model.
        """
        pass

    @abstractmethod
    def graph_to_dexpi(self, plant_graph: Graph) -> DexpiModel:
        """
        Parse a NetworkX graph into a pyDEXPI model representation.

        Parameters
        ----------
        plant_graph : nx.Graph
            The NetworkX graph representation of a plant to be parsed into a Dexpi model.

        Returns
        -------
        DexpiModel
            The parsed pyDEXPI model representation of the plant graph.
        """
        pass

    @abstractmethod
    def validate_graph_format(self, plant_graph: Graph) -> bool:
        """
        Validate that the given NetworkX graph conforms to the expected format.

        This method ensures that the structure, nodes, edges, and associated metadata
        in the graph meet the requirements for parsing or transformation into a
        Dexpi model.

        Parameters
        ----------
        plant_graph : nx.Graph
            The NetworkX graph to validate.

        Returns
        -------
        bool
            True if the graph is valid, False otherwise.
        """
        pass
