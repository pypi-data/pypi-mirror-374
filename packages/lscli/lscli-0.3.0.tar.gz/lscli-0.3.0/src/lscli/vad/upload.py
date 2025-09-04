from datetime import timedelta
from pathlib import Path

from lscli.upload import get_minio_client


def upload(audio_path: Path, alias: str, bucket_name: str, object_name: str):
    client = get_minio_client(alias)
    client.fput_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=str(audio_path),
    )
    # 返回预签名url
    expires = timedelta(hours=1)
    audio_url = client.presigned_get_object(bucket_name, object_name, expires=expires)
    return audio_url
