from typing import Optional
import typer
import argparse, logging
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


@app.command()
def hello(name: Optional[str] = typer.Argument(None)):
    if name is None:
        print("Hello, everybody")
    else:
        print(f"Hello, {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye, Ms {name}")
    else:
        print(f"Bye, {name}")


if __name__ == '__main__':
    app()
