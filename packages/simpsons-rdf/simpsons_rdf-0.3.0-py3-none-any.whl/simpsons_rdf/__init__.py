import importlib.resources
from functools import cache
from pathlib import Path

from rdflib import Graph, Namespace

SIM = Namespace("https://simpsons.example.org/")
FAM = Namespace("https://vocab.example.org/family#")


class Simpsons:
    @property
    @cache
    def graph(self) -> Graph:
        return Graph(identifier=SIM[""]).parse(self.graph_file, format="turtle")

    @property
    def graph_file(self) -> Path:
        with importlib.resources.path(self.__module__, "simpsons.ttl") as data_path:
            return data_path


simpsons = Simpsons()
