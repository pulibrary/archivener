from pathlib import Path
import typer
import logging
from archivener.fns import manifest_graph
import iiif.resources as iiif
from src.ocrannotator import OcrAnnotator


app = typer.Typer()


@app.command()
def ocr(uri: str, dest_file: str, ocr_dir: str):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    manifest: iiif.Manifest = iiif.ResourceFactory().manifest(uri)
    ocrd = Path(ocr_dir)
    ocrd.mkdir(parents=True, exist_ok=False)
    annotator: OcrAnnotator = OcrAnnotator(manifest, ocrd)
    logging.info("Generating OCR")
    annotator.ocr()
    logging.info("Generating annotations")
    annotator.annotate()
    logging.info("Serialize annotations")
    annotator.graph.serialize(Path(dest_file))


if __name__ == "__main__":
    app()
