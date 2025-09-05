import requests
from .constants import BASE_URL


class StorageClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })

    def get_presigned_url(self, file_name: str, content_type: str, size: int) -> dict:
        dto = {
            "fileName": file_name,
            "contentType": content_type,
            "size": size
        }
        response = self.session.post(BASE_URL, json=dto)
        response.raise_for_status()
        return response.json()

    def download_file(self, file_id: str, destination: str):
        url = f"{BASE_URL}/{file_id}"
        with self.session.get(url, stream=True) as response:
            response.raise_for_status()
            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    def mark_as_uploaded(self, file_id: str) -> dict:
        url = f"{BASE_URL}/{file_id}"
        response = self.session.patch(url)
        response.raise_for_status()
        return response.json()

    def delete_file(self, file_id: str) -> dict:
        url = f"{BASE_URL}/{file_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()
