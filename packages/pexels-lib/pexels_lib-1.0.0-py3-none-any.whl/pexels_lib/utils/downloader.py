class Downloader:
    def __init__(self, dest_folder):
        self.dest_folder = dest_folder

    def download(self, url, filename) -> str:
        import os
        import requests

        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(self.dest_folder, filename)
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return file_path
        else:
            response.raise_for_status()
