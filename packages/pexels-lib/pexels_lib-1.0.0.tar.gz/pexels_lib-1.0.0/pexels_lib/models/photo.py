class Photo:
    def __init__(self, id, width, height, url, src):
        self.id = id
        self.width = width
        self.height = height
        self.url = url
        self.src = src

    def __repr__(self):
        return (f"Photo Details:\n"
                f"  ID: {self.id}\n"
                f"  Width: {self.width}\n"
                f"  Height: {self.height}\n"
                f"  URL: {self.url}")
