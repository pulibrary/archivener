import pytest
import archivener.graphs as graph
import archivener.resources
import iiif.resources as iiif
import spacy

sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'


@pytest.fixture
def a_model():
    return spacy.load('en_core_web_sm')


@pytest.fixture
def graph_manifest(a_model):
    return graph.Manifest(sample_manifest_uri, a_model)


def test_properties(graph_manifest):
    assert (
        graph_manifest.id
        == "https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest"
    )
