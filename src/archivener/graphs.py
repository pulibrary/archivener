import re
from pathlib import Path
import rdflib
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from typing import Union, IO
from rdflib.term import URIRef, Literal
from shortuuid import uuid
from spacy.tokens.span import Span
import iiif.resources as iiif
import spacy

from archivener import resources


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
        self._graph = None

    def init_graph(self):
        self._graph = rdflib.Graph()
        for prefix, namespace in self.namespaces.items():
            self._graph.bind(prefix, namespace)

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


class Manifest(Graph):
    def __init__(self, manifest_uri: str, model: spacy.language.Language):
        super().__init__()
        iiif_manifest = iiif.ResourceFactory().manifest(manifest_uri)
        self.manifest = resources.Manifest(iiif_manifest, model)
        self._canvases = None

    @property
    def label(self):
        return self.manifest.label

    @property
    def id(self):
        return self.manifest.id

    @property
    def canvases(self):
        if self._canvases is None:
            self._canvases = []
            for canvas in self.manifest.canvases:
                self._canvases.append(Canvas(canvas))
        return self._canvases

    @property
    def graph(self):
        if self._graph is None:
            self.init_graph()
            for canvas in self.canvases:
                self._graph += canvas.graph


class Canvas(Graph):
    def __init__(self, canvas: resources.Canvas):
        super().__init__()
        self.canvas = canvas
        self.id = URIRef(self.canvas.id)

    @property
    def graph(self):
        if self._graph is None:
            self.init_graph()
            self.create_graph()
        return self._graph

    def create_graph(self):
        self._graph.add((self.id, RDF.type, self.namespace('sc')['Canvas']))
        self._graph.add((self.id, RDFS.label, self.canvas.label))

        persnames = self.canvas.persnames
        for persname in persnames:
            name = re.sub(r'\W+', ' ', persname.text)
            inscription_id = self.gen_id("inscription")
            appellation_id = self.gen_id("appellation")
            self._graph.add(
                (inscription_id, RDF.type, self.namespace("ecrm")["E34_Inscription"])
            )
            # self._graph.add((self.id, RDFS.label, Literal(name)))
            self._graph.add((inscription_id, RDFS.label, Literal(name)))
            self._graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["P190_has_symbolic_content"],
                    Literal(name),
                )
            )
            self._graph.add(
                (inscription_id, self.namespace("ecrm")["P128i_is_carried_by"], self.id)
            )

            self._graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["E55_Type"],
                    Literal(persname.label_),
                )
            )


# deprecated?
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
