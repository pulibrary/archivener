from typing import Optional
import typer
import logging
from archivener.named_entities import Manifest
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


def main():
    app()
