import pytest
import spacy
from archivener.named_entities import Manifest
from rdflib.term import URIRef

sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'


@pytest.fixture
def a_model():
    return spacy.load('en_core_web_sm')


@pytest.fixture
def a_manifest(a_model):
    manifest = Manifest(sample_manifest_uri, a_model)
    return manifest


def test_manifest_canvases(a_manifest):
    assert len(a_manifest.canvases) == 24
