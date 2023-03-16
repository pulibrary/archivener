import io
from pathlib import Path
import requests
import spacy
from ocr import Tesseract
from iiif.resources import ResourceFactory, Manifest, Canvas
from rdflib import Graph, Namespace, Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS

from shortuuid import uuid
from typing import Union, IO, TextIO

uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'


class Ner:
    def __init__(self, canvas: Canvas, model):
        self.canvas = canvas
        self.model = model
        self._doc = None

    @property
    def doc(self):
        if self._doc is None:
            image_uri = self.canvas.images[0].resource
            ocr = Tesseract(image_uri)
            self._doc = self.model(ocr.string)
        return self._doc

    @property
    def persons(self):
        return filter(lambda e: e.label_ == 'PERSON', self.doc.ents)


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
    def __init__(self, ent):
        super().__init__()
        self.ent = ent
        self.id = self.gen_id("appellation")
        self.create()

    def __repr__(self) -> str:
        return f"{self.ent.label_}({self.ent.text})"

    def create(self):
        content = Literal(self.ent.text)
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


factory = ResourceFactory()
m = factory.manifest(uri)
c = m.sequences[0].canvases[1]
ocr = Tesseract(c.images[0].resource)

ner = Ner(c, spacy.load('en_core_web_sm'))
