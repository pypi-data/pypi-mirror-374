from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from label_studio_sdk import LabelStudio

from lscli.vad.upload import upload


def annotation(
    client: LabelStudio,
    annotation_id: int,
    label_data: List[Dict],
):
    client.annotations.create(
        id=annotation_id,
        ground_truth=True,
        result=label_data,
        was_cancelled=False,
    )


def to_seconds(x):
    t = datetime.strptime(x, "%M:%S.%f")
    return t.minute * 60 + t.second + t.microsecond / 1e6


def annotation_df(
    ls_client: LabelStudio,
    annotation_id: int,
    df: pd.DataFrame,
):
    starts = df["Start"].apply(to_seconds).to_numpy()
    durations = df["Duration"].apply(to_seconds).to_numpy()
    ends = starts + durations
    label_data = [
        {
            "id": f"annotation_{i}",
            "from_name": "label",
            "to_name": "audio",
            "type": "labels",
            "value": {
                "start": start,
                "end": end,
                "labels": ["speech"],
            },
        }
        for i, (start, end) in enumerate(zip(starts, ends))
    ]
    annotation(ls_client, annotation_id, label_data)


def annotation_data_pair(
    ls_client: LabelStudio,
    audio_path: Optional[Path] = None,
    label_path: Optional[Path] = None,
    minio_alias: str = "minio",
    bucket_name: str = "tmp",
    object_name: Optional[str] = None,
    project_name: str = "vad",
):
    # 确保两个文件都存在
    if audio_path is None and label_path is None:
        raise ValueError("audio_path or label_path must be provided")
    if audio_path is not None:
        label_path = audio_path.with_suffix(".csv")
    if label_path is not None:
        audio_path = label_path.with_suffix(".wav")
    if not audio_path.exists() or not label_path.exists():
        raise FileNotFoundError(
            f"File not found: {str(audio_path)} or {str(label_path)}"
        )
    if object_name is None:
        object_name = audio_path.name
    # 上传音频文件并获取预签名url
    presign_url = upload(
        audio_path=audio_path,
        alias=minio_alias,
        bucket_name=bucket_name,
        object_name=object_name,
    )

    projects = ls_client.projects.list()
    project = next((p for p in projects.items if p.title == project_name), None)
    project_id = project.id
    request = [{"audio": presign_url}]
    results = ls_client.projects.import_tasks(
        project_id,
        request=request,
        return_task_ids=True,
    )
    task_id = results.task_ids[0]
    label_df = pd.read_csv(label_path, sep="\t")
    annotation_df(ls_client, task_id, label_df)
