from typing import Union
import iiif.resources as iiif
import archivener.graphs as graphs
import archivener.resources as resources
import spacy


class Manifest:
    def __init__(self, manifest_uri: str, model: spacy.language.Language):
        self.model = model
        factory = iiif.ResourceFactory()
        self.manifest: iiif.Manifest = factory.manifest(manifest_uri)
        self._canvases: Union[list[Canvas], None] = None
        self._graph: Union[graphs.Graph, None] = None

    def __repr__(self) -> str:
        return f"Graph_Manifest({self.manifest.label})"

    @property
    def graph(self):
        if self._graph is None:
            self._graph = graphs.Graph()
            for canvas in self.canvases:
                self._graph.graph += canvas.graph.graph
        return self._graph

    @property
    def canvases(self):
        if self._canvases is None:
            self._canvases = []
            for canvas in self.manifest.sequences[0].canvases:
                g_canvas = resources.Canvas(canvas, model)
                self._canvases.append(Canvas(g_canvas))
        return self._canvases

    def serialize(self, path):
        with open(path, 'wb') as f:
            self.graph.serialize(f)


class Canvas:
    def __init__(self, canvas: resources.Canvas):
        self.canvas = canvas
        self._graph: Union[graphs.Graph, None] = None

    @property
    def graph(self):
        if self._graph is None:
            self._graph = graphs.Graph()
            self._graph.graph += graphs.Canvas(self.canvas).graph
        return self._graph


sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'

model = spacy.load('en_core_web_sm')

manifest = Manifest(sample_manifest_uri, model)
