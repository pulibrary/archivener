import re
from pathlib import Path
import rdflib
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from typing import Union, IO
from rdflib.term import URIRef, Literal
from shortuuid import uuid
from spacy.tokens.span import Span

from archivener import named_entities, resources


class Graph:
    namespaces = {
        "ecrm": rdflib.Namespace("http://erlangen-crm.org/200717/"),
        "sc": rdflib.Namespace("http://iiif.io/api/presentation/2#"),
        "page": rdflib.Namespace("https://figgy.princeton.edu/concerns/pages/"),
        "actor": rdflib.Namespace("https://figgy.princeton.edu/concerns/actors/"),
        "appellation": rdflib.Namespace(
            "https://figgy.princeton.edu/concerns/appellations/"
        ),
        "entity": rdflib.Namespace("https://figgy.princeton.edu/concerns/entities/"),
        "inscription": rdflib.Namespace(
            "https://figgy.princeton.edu/concerns/inscriptions/"
        ),
        "etype": rdflib.Namespace("https://figgy.princeton.edu/concerns/adam/"),
    }

    def __init__(self):
        self.graph = rdflib.Graph()
        for prefix, namespace in self.namespaces.items():
            self.graph.bind(prefix, namespace)

    def namespace(self, prefix):
        return self.namespaces[prefix]

    def gen_id(self, ns):
        return self.namespace(ns)[uuid()]

    def serialize(
        self, path: Union[str, Path, IO[bytes], None] = None, format: str = "ttl"
    ):
        if path == None:
            self.graph.serialize(format=format)
        else:
            self.graph.serialize(destination=path, format=format)


class Canvas(Graph):
    def __init__(self, canvas: resources.Canvas):
        super().__init__()
        self.canvas = canvas
        self.id = URIRef(self.canvas.id)
        self.create()

    def create(self):
        people = self.canvas.people
        for person in people:
            name = re.sub(r'\W+', ' ', person.text)
            inscription_id = self.gen_id("inscription")
            appellation_id = self.gen_id("appellation")
            self.graph.add(
                (inscription_id, RDF.type, self.namespace("ecrm")["E34_Inscription"])
            )
            self.graph.add((self.id, RDFS.label, Literal(name)))
            self.graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["P190_has_symbolic_content"],
                    Literal(name),
                )
            )
            self.graph.add(
                (inscription_id, self.namespace("ecrm")["P128i_is_carried_by"], self.id)
            )
            # self.graph.add(
            #     (
            #         inscription_id,
            #         self.namespace("ecrm")["P106_is_composed_of"],
            #         appellation_id,
            #     )
            # )
            self.graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["E55_Type"],
                    Literal(person.label_),
                )
            )


class Person(Graph):
    def __init__(self, ent: Span):
        super().__init__()
        self.ent = ent
        self.name = re.sub(r'\W+', ' ', self.ent.text)
        self.id = self.gen_id("appellation")
        self.create()

    def __repr__(self) -> str:
        return f"{self.ent.label_}({self.name})"

    def create(self):
        content = rdflib.Literal(self.name)
        inscription_id = self.gen_id("inscription")
        self.graph.add((self.id, RDF.type, self.namespace("ecrm")["E41_Appellation"]))
        self.graph.add(
            (inscription_id, RDF.type, self.namespace("ecrm")["E34_Inscription"])
        )

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
