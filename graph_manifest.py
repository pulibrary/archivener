import logging
import typer
from src.archivener.fns import manifest_graph


app = typer.Typer()


@app.command()
def main(uri: str, dest: str) -> None:
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
    logging.info(f"{uri}, {dest}")
    logging.info("Generating graph")
    g = manifest_graph(uri)
    logging.info("Serializing graph")
    with open(dest, "wb") as f:
        g.serialize(f)


if __name__ == "__main__":
    app()
