from iiif.resources import ResourceFactory, Manifest
from ner import Ner
from ner_graph import NerGraph, PersonGraph
import spacy


class NamedEntities:
    def __init__(self, manifest_uri: str, model: spacy.language.Language):
        self.model = model
        factory = ResourceFactory()
        self.manifest = factory.manifest(manifest_uri)
        self._canvases = None

    @property
    def canvases(self):
        if self._canvases is None:
            self._canvases = [
                Ner(canvas, self.model)
                for canvas in self.manifest.sequences[0].canvases
            ]
        return self._canvases

    def canvas_persons(self, canvas_ner):
        canvas_graph = NerGraph()
        g = canvas_graph.graph


sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'

model = spacy.load('en_core_web_sm')

ne = NamedEntities(sample_manifest_uri, model)
c = ne.canvases[1]
people = [PersonGraph(person) for person in c.persons]
