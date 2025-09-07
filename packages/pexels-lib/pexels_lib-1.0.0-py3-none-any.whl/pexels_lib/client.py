import requests
from pexels_lib.models.photo import Photo
from pexels_lib.utils.downloader import Downloader

class PexelsClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/v1/"
        self.downloader = None

    def _get_headers(self):
        return {
            "Authorization": self.api_key
        }

    def search_photos(self, query, **kwargs) -> list[Photo]:
        headers = self._get_headers()

        params = {
            "query": query,
            "per_page": kwargs.pop("per_page", 15),
            "page": kwargs.pop("page", 1)
        }

        allowed_params = ["orientation", "size", "color"]     

        for key in allowed_params:
            if key in kwargs:
                params[key] = kwargs[key]

        response = requests.get(f"{self.base_url}search", headers=headers, params=params)
        
        if response.status_code == 200:
            photos = [
                Photo(
                    id=photo["id"],
                    width=photo["width"],
                    height=photo["height"],
                    url=photo["url"],
                    src=photo["src"]
                )
                for photo in response.json().get("photos", [])
            ]
            return photos
        else:
            response.raise_for_status()

    def get_photo(self, photo_id) -> Photo:
        headers = self._get_headers()

        response = requests.get(f"{self.base_url}photos/{photo_id}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            return Photo(
                id=data["id"],
                width=data["width"],
                height=data["height"],
                url=data["url"],
                src=data["src"]
            )
        else:
            response.raise_for_status()

    def download_photo(self, photo: Photo, dest_folder: str, filename: str = None) -> str:
        if self.downloader is None or self.downloader.dest_folder != dest_folder:
            self.downloader = Downloader(dest_folder)
        
        if not filename:
            filename = f"{photo.id}.jpg"
        return self.downloader.download(photo.src["original"], filename)
