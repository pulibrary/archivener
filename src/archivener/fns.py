from functools import partial
import re
from typing import List, Optional
import spacy
from ocr import Tesseract
import iiif.resources as iiif
from rdflib import Namespace, Graph, URIRef, Literal, RDF, RDFS
from shortuuid import uuid

CRM = Namespace("http://erlangen-crm.org/200717/")
SC = Namespace("http://iiif.io/api/presentation/2#")
INSCR = Namespace("https://figgy.princeton.edu/concerns/inscriptions/")
APPEL = Namespace("https://figgy.princeton.edu/concerns/appellations/")


def text_of(canvas: iiif.Canvas) -> str:
    image_uri = canvas.images[0].resource
    ocr = Tesseract(image_uri)
    return ocr.string


def entities_in(text: str, model: spacy.lang) -> List[tuple]:
    doc = model(text)
    return doc.ents


def persnames_from(ents: List[tuple]) -> List[tuple]:
    return filter(lambda e: e.label_ == "PERSON", ents)


def inscription_id() -> URIRef:
    return INSCR[uuid()]


def appellation_id() -> URIRef:
    return APPEL[uuid()]


def cleaned_name(name_string: str) -> str:
    return re.sub(r'\W+', ' ', name_string).strip()


def archivener_graph() -> Graph:
    bindings = {
        "crm": "http://erlangen-crm.org/200717/",
        "sc": "http://iiif.io/api/presentation/2#",
        "inscr": "https://figgy.princeton.edu/concerns/inscriptions/",
        "appel": "https://figgy.princeton.edu/concerns/appellations/",
    }
    g = Graph()
    for k, v in bindings.items():
        g.bind(k, v)
    return g


def canvas_graph(canvas: iiif.Canvas, model: Optional[spacy.lang] = None) -> Graph:
    g: Graph = archivener_graph()
    if model is None:
        model = spacy.load('en_core_web_sm')
    canvas_id: URIRef = URIRef(canvas.id)
    persnames: List[tuple] = persnames_from(entities_in(text_of(canvas), model))
    for persname in persnames:
        inscription: URIRef = inscription_id()
        name: Literal = Literal(cleaned_name(persname.text))
        g.add((inscription, RDF.type, CRM.E34_Inscription))
        g.add((inscription, RDFS.label, name))
        g.add((inscription, CRM.E55_type, Literal(persname.label_)))
        g.add((inscription, CRM.P190_has_symbolic_content, name))
        g.add((inscription, CRM.P128i_is_carried_by, canvas_id))
    return g


def manifest_graph(manifest_uri: str, model: Optional[spacy.lang] = None) -> Graph:
    manifest: iiif.Manifest = iiif.ResourceFactory().manifest(manifest_uri)
    g: Graph = archivener_graph()
    if model is None:
        model = spacy.load('en_core_web_sm')
    for canvas in manifest.sequences[0].canvases:
        g += canvas_graph(canvas, model)
    return g


# sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'

# model = spacy.load('en_core_web_sm')

# factory = iiif.ResourceFactory()
# manifest = factory.manifest(sample_manifest_uri)
