import spacy
from ocr import Tesseract
import iiif.resources as iiif


class Manifest:
    def __init__(self, manifest: iiif.Manifest, model: spacy.language.Language):
        self.manifest = manifest
        self.model = model
        self._canvases = None

    def __repr__(self) -> str:
        return f"Resource_Manifest({self.manifest.label})"

    @property
    def canvases(self):
        if self._canvases is None:
            self._canvases = [
                Canvas(c, self.model) for c in self.manifest.sequences[0].canvases
            ]
        return self._canvases

    @property
    def entities(self):
        return [c.entities for c in self.canvases]


class Canvas:
    def __init__(self, canvas: iiif.Canvas, model: spacy.language.Language):
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
    def entities(self):
        return self.doc.ents

    @property
    def people(self):
        return filter(lambda e: e.label_ == "PERSON", self.doc.ents)
