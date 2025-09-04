from pathlib import Path

from minio import Minio
import json


def get_minio_client(alias: str) -> Minio:
    config = json.load(Path(Path.home(), ".mc", "config.json").open())
    alias = config["aliases"][alias]
    return Minio(
        endpoint=alias["url"].replace("https://", "").replace("http://", ""),
        access_key=alias["accessKey"],
        secret_key=alias["secretKey"],
        secure=alias["url"].startswith("https://"),
    )


def upload(input_dir: Path, bucket_name: str, minio_client: Minio, prefix: str):
    file_list = input_dir.glob("**/*")
    for file_path in file_list:
        if file_path.is_file():
            try:
                object_name = str(Path(prefix) / file_path.relative_to(input_dir))
                minio_client.fput_object(
                    bucket_name=bucket_name,
                    object_name=file_path.name,
                    file_path=str(file_path),
                )
                print(f"Uploaded {file_path.name} to MinIO.")
            except Exception as e:
                print(f"Failed to upload {file_path.name}: {e}")
