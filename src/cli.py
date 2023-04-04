from typing import Optional
from pathlib import Path
import typer
import logging
from archivener.named_entities import Manifest
import iiif.resources as iiif
from ocrannotator import OcrAnnotator
import spacy


app = typer.Typer()


@app.command()
def graph(uri: str, dest: str):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logging.info(f"{uri}, {dest}")
    model = spacy.load('en_core_web_sm')
    manifest = Manifest(uri, model)
    logging.info("Generating graph")
    manifest.graph
    logging.info("Serializing graph")
    manifest.serialize(dest)


@app.command()
def ocr(uri: str, dest_file: str, ocr_dir: str):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    manifest = iiif.ResourceFactory().manifest(uri)
    ocrd = Path(ocr_dir)
    ocrd.mkdir(parents=True, exist_ok=False)
    annotator = OcrAnnotator(manifest, ocrd)
    logging.info("Generating OCR")
    annotator.ocr()
    logging.info("Generating annotations")
    annotator.annotate()
    annotator.graph.serialize(Path(dest_file))


if __name__ == "__main__":
    app()
