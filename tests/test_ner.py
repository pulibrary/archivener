import pytest
import spacy
from archivener import Ner, NerGraph, PersonGraph
from iiif.resources import ResourceFactory, Manifest, Canvas
from rdflib.term import URIRef

sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'


@pytest.fixture
def a_canvas():
    factory = ResourceFactory()
    manifest = factory.manifest(sample_manifest_uri)
    return manifest.sequences[0].canvases[0]


@pytest.fixture
def a_model():
    return spacy.load('en_core_web_sm')


@pytest.fixture
def an_ner(a_canvas, a_model):
    return Ner(a_canvas, a_model)


def test_persons(an_ner):
    assert len(list(an_ner.persons)) == 4


def test_graph(an_ner):
    person = PersonGraph(next(an_ner.persons))
    assert person.id.__class__ == URIRef
