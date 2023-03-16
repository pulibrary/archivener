import re
import io
from pathlib import Path
from rdflib import Graph, Namespace, Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from typing import Union, IO
from shortuuid import uuid
from spacy.tokens.span import Span
import spacy


class NerGraph:
    namespaces = {
        "ecrm": Namespace("http://erlangen-crm.org/200717/"),
        "sc": Namespace("http://iiif.io/api/presentation/2#"),
        "page": Namespace("https://figgy.princeton.edu/concerns/pages/"),
        "actor": Namespace("https://figgy.princeton.edu/concerns/actors/"),
        "appellation": Namespace("https://figgy.princeton.edu/concerns/appellations/"),
        "entity": Namespace("https://figgy.princeton.edu/concerns/entities/"),
        "inscription": Namespace("https://figgy.princeton.edu/concerns/inscriptions/"),
        "etype": Namespace("https://figgy.princeton.edu/concerns/adam/"),
    }

    def __init__(self):
        self.graph = Graph()
        for prefix, namespace in self.namespaces.items():
            self.graph.bind(prefix, namespace)

    def namespace(self, prefix):
        return self.namespaces[prefix]

    def gen_id(self, ns):
        return self.namespace(ns)[uuid()]

    def serialize(
        self, path: Union[str, Path, IO[bytes], None] = None, fmt: str = "ttl"
    ):
        self.graph.serialize(destination=path, format=fmt)


class PersonGraph(NerGraph):
    def __init__(self, ent: Span):
        super().__init__()
        self.ent = ent
        self.name = re.sub('\W+', ' ', self.ent.text)
        self.id = self.gen_id("appellation")
        self.create()

    def __repr__(self) -> str:
        return f"{self.ent.label_}({self.name})"

    def create(self):
        content = Literal(self.name)
        self.graph.add((self.id, RDF.type, self.namespace("ecrm")["E41_Appellation"]))
        self.graph.add(
            (
                self.id,
                self.namespace("ecrm")["E55_Type"],
                self.namespace("etype")[self.ent.label_],
            )
        )

        self.graph.add((self.id, RDFS.label, content))

        self.graph.add(
            (self.id, self.namespace("ecrm")["P190_has_symbolic_content"], content)
        )
