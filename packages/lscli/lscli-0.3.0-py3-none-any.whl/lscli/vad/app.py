import os
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from label_studio_sdk import LabelStudio
from yarl import URL

from lscli.vad.annotation import annotation_data_pair, annotation_df

app = typer.Typer()


@app.command(name="df")
def annotation_df_cli(
    task_id: int = typer.Argument(..., help="Task ID"),
    df_path: Path = typer.Argument(..., help="Path to save the annotation dataframe"),
):
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    base_url = os.getenv("LABEL_STUDIO_BASE_URL")
    if not api_key:
        typer.echo("Error: LABEL_STUDIO_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)
    if not base_url:
        typer.echo("Error: LABEL_STUDIO_BASE_URL environment variable is not set.")
        raise typer.Exit(code=1)

    client = LabelStudio(
        api_key=api_key,
        base_url=URL(base_url),
    )
    df = pd.read_csv(df_path, sep="\t")
    annotation_df(client, task_id, df)


@app.command(name="pair")
def annotation_data_pair_cli(
    minio_alias: str = typer.Argument("minio", help="MinIO alias"),
    audio_path: Path = typer.Option(
        None, "-a", "--audio", help="Path to the audio file"
    ),
    label_path: Path = typer.Option(
        None, "-l", "--label", help="Path to the label file"
    ),
    bucket_name: str = typer.Option(
        "tmp", "-b", "--bucket", help="Bucket name in MinIO"
    ),
    object_name: Optional[str] = typer.Option(
        None, "-o", "--object", help="Object name in MinIO"
    ),
    project_name: str = typer.Option(
        "vad", "-p", "--project", help="Label Studio project name"
    ),
):
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    base_url = os.getenv("LABEL_STUDIO_BASE_URL")
    if not api_key:
        typer.echo("Error: LABEL_STUDIO_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)
    if not base_url:
        typer.echo("Error: LABEL_STUDIO_BASE_URL environment variable is not set.")
        raise typer.Exit(code=1)
    client = LabelStudio(
        api_key=api_key,
        base_url=URL(base_url),
    )
    annotation_data_pair(
        client,
        audio_path=audio_path,
        label_path=label_path,
        minio_alias=minio_alias,
        bucket_name=bucket_name,
        object_name=object_name,
        project_name=project_name,
    )


def main():
    app()


if __name__ == "__main__":
    app()
