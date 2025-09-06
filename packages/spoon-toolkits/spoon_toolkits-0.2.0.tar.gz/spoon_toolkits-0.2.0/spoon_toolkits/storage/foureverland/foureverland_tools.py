import asyncio
import os

from ..base_storge_tool import S3Tool


class FourEverlandStorageTool(S3Tool):
    """S3Tool implementation for 4EVERLAND Storage."""
    endpoint_env_key: str = "FOREVERLAND_ENDPOINT_URL"
    aws_access_key_id: str = "FOREVERLAND_ACCESS_KEY"
    aws_secret_access_key: str = "FOREVERLAND_SECRET_KEY"


class UploadFileToFourEverland(FourEverlandStorageTool):
    name: str = "upload_file_to_4everland"
    description: str = "Upload a file to 4EVERLAND Storage"
    parameters: dict = {
        "type": "object",
        "properties": {
            "bucket_name": {"type": "string", "description": "Target bucket name in 4EVERLAND"},
            "file_path": {"type": "string", "description": "Local path to file to upload"}
        },
        "required": ["bucket_name", "file_path"]
    }

    async def execute(self, bucket_name: str, file_path: str) -> str:
        return self._upload_file(bucket_name, file_path)


class ListFourEverlandBuckets(FourEverlandStorageTool):
    name: str = "list_4everland_buckets"
    description: str = "List all buckets in 4EVERLAND Storage"
    parameters: dict = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self) -> str:
        return self._list_buckets()


class DownloadFileFromFourEverland(FourEverlandStorageTool):
    name: str = "download_file_from_4everland"
    description: str = "Download a file from 4EVERLAND Storage"
    parameters: dict = {
        "type": "object",
        "properties": {
            "bucket_name": {"type": "string", "description": "Name of the 4EVERLAND bucket"},
            "object_key": {"type": "string", "description": "Key of the file to download"},
            "download_path": {"type": "string", "description": "Local path to save the downloaded file"}
        },
        "required": ["bucket_name", "object_key", "download_path"]
    }

    async def execute(self, bucket_name: str, object_key: str, download_path: str) -> str:
        return self._download_file(bucket_name, object_key, download_path)


class DeleteFourEverlandObject(FourEverlandStorageTool):
    name: str = "delete_4everland_object"
    description: str = "Delete an object from a 4EVERLAND Storage bucket"
    parameters: dict = {
        "type": "object",
        "properties": {
            "bucket_name": {"type": "string", "description": "Bucket name"},
            "object_key": {"type": "string", "description": "Object key to delete"}
        },
        "required": ["bucket_name", "object_key"]
    }

    async def execute(self, bucket_name: str, object_key: str) -> str:
        return self._delete_object(bucket_name, object_key)


class GenerateFourEverlandPresignedUrl(FourEverlandStorageTool):
    name: str = "generate_4everland_presigned_url"
    description: str = "Generate a temporary URL to access a 4EVERLAND object"
    parameters: dict = {
        "type": "object",
        "properties": {
            "bucket_name": {"type": "string", "description": "Bucket name"},
            "object_key": {"type": "string", "description": "Object key"},
            "expires_in": {"type": "integer", "default": 3600, "description": "Expiration time in seconds"}
        },
        "required": ["bucket_name", "object_key"]
    }

    async def execute(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        return self._generate_presigned_url(bucket_name, object_key, expires_in)



async def test_list_foureverland_buckets():
    tool = ListFourEverlandBuckets()
    result = await tool.execute()
    print("🧪 List 4EVERLAND Buckets:\n", result)


async def test_upload_file_to_foureverland():
    bucket_name = os.getenv("FOREVERLAND_BUCKET_NAME")
    file_path = "/Users/weixiaole/Downloads/file1.txt"

    # Create test file
    with open(file_path, 'w') as f:
        f.write("🌍 4EVERLAND test content")

    tool = UploadFileToFourEverland()
    result = await tool.execute(bucket_name=bucket_name, file_path=file_path)
    print("🧪 Upload File Result:\n", result)


async def test_generate_presigned_url_foureverland():
    bucket_name = os.getenv("FOREVERLAND_BUCKET_NAME")
    object_key = "file1.txt"

    tool = GenerateFourEverlandPresignedUrl()
    result = await tool.execute(bucket_name=bucket_name, object_key=object_key, expires_in=600)
    print("🧪 Generate Presigned URL Result:\n", result)


async def test_download_file_from_foureverland():
    bucket_name = os.getenv("FOREVERLAND_BUCKET_NAME")
    object_key = "file1.txt"
    download_path = "/Users/weixiaole/Downloads/test_file_downloaded.txt"

    tool = DownloadFileFromFourEverland()
    result = await tool.execute(bucket_name=bucket_name, object_key=object_key, download_path=download_path)
    print("🧪 Download File Result:\n", result)


async def test_delete_foureverland_object():
    bucket_name = os.getenv("FOREVERLAND_BUCKET_NAME")
    object_key = "file1.txt"

    tool = DeleteFourEverlandObject()
    result = await tool.execute(bucket_name=bucket_name, object_key=object_key)
    print("🧪 Delete Object Result:\n", result)


if __name__ == '__main__':
    async def run_all_foureverland_tests():
        await test_list_foureverland_buckets()
        await test_upload_file_to_foureverland()
        await test_generate_presigned_url_foureverland()
        await test_download_file_from_foureverland()
        await test_delete_foureverland_object()


    asyncio.run(run_all_foureverland_tests())
