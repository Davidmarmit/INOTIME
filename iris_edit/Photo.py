class Photo:
    # constructor of Image
    def __init__(self, name, original_path):
        self.name = name.split(".")[0]
        self.original_path = original_path
        self.edited = False

    def get_name(self):
        return self.name

    def get_original_path(self):
        return self.original_path

    def set_edited(self, edited):
        self.edited = edited
