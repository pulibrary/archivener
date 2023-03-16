import spacy
from ocr import Tesseract
from iiif.resources import Canvas


class Ner:
    def __init__(self, canvas: Canvas, model: spacy.language.Language):
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
