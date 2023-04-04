import iiif.resources as iiif
import rdflib
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.term import URIRef
from pathlib import Path
from ocr import Tesseract
from shortuuid import uuid


def short_id(canvas_id: str) -> str:
    return canvas_id.split('/')[-1]


class OcrAnnotator:
    namespaces = {
        "oa": rdflib.Namespace("http://www.w3.org/ns/oa#"),
        "sc": rdflib.Namespace("http://iiif.io/api/presentation/2#"),
        "hocr": rdflib.Namespace("https://figgy.princeton.edu/concerns/hocr/"),
        "annot": rdflib.Namespace("https://figgy.princeton.edu/concerns/annotations/"),
    }

    def __init__(self, manifest: iiif.Manifest, ocr_store: Path) -> None:
        self.manifest = manifest
        self.ocr_store = ocr_store
        self.graph = rdflib.Graph()
        for prefix, namespace in self.namespaces.items():
            self.graph.bind(prefix, namespace)

    def ocr(self):
        for canvas in self.manifest.sequences[0].canvases:
            self.ocr_canvas(canvas)

    def annotate(self):
        for canvas in self.manifest.sequences[0].canvases:
            self.annotate_canvas(canvas)

    def namespace(self, prefix):
        return self.namespaces[prefix]

    def ocr_canvas(self, canvas: iiif.Canvas):
        image_uri = canvas.images[0].resource
        ocr = Tesseract(image_uri)
        hocr = ocr.hocr
        filepath = self.ocr_store / Path(short_id(canvas.id))
        with open(filepath, mode='w', encoding='utf-8') as f:
            f.write(hocr)

    def annotate_canvas(self, canvas: iiif.Canvas):
        annot_id = self.namespace('annot')[uuid()]
        hocr_id = self.namespace('hocr')[short_id(canvas.id)]

        self.graph.add((annot_id, RDF.type, self.namespace('oa')['Annotation']))
        self.graph.add(
            (
                annot_id,
                self.namespace('sc')['motivation'],
                self.namespace('oa')['linking'],
            )
        )
        self.graph.add((annot_id, self.namespace('oa')['hasTarget'], canvas.ref))
        self.graph.add((annot_id, self.namespace('oa')['hasBody'], hocr_id))


sample_manifest_uri = 'https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest'

m = iiif.ResourceFactory().manifest(sample_manifest_uri)
ocr_dir = Path("/tmp/ocr_dir")
ocr_dir.mkdir(parents=True, exist_ok=True)
annotator = OcrAnnotator(m, ocr_dir)
c = m.sequences[0].canvases[0]
