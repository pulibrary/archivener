import pytest
import spacy
from archivener.resources import Manifest, Canvas
import iiif.resources as iiif

sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'


@pytest.fixture
def a_model():
    return spacy.load('en_core_web_sm')


@pytest.fixture
def a_manifest(a_model):
    iiif_manifest = iiif.ResourceFactory().manifest(sample_manifest_uri)
    return Manifest(iiif_manifest, a_model)


@pytest.fixture
def a_canvas(a_manifest):
    return a_manifest.canvases[0]


def test_properties(a_manifest):
    assert a_manifest.id == a_manifest.manifest.id
    assert a_manifest.label == a_manifest.manifest.label
    assert len(a_manifest.canvases) == len(a_manifest.manifest.sequences[0].canvases)


def test_canvas(a_canvas):
    assert a_canvas.label == '1'
    assert a_canvas.name == '2ae6db12-575c-4708-a8a9-8b8408c171b7'
    assert a_canvas.id == str(a_canvas.canvas.ref)
    assert len(a_canvas.images) == 1
    assert len(a_canvas.entities) == 17
    assert str(list(a_canvas.persnames)[0]) == 'George Kennan Papers'
