from pathlib import Path


class Config:
    @property
    def working_directory(self):
        return Path("~/.homepress_server").expanduser().absolute()

    @property
    def uploads_directory(self):
        return self.working_directory / "uploads"

    def make(self):
        self.working_directory.mkdir(exist_ok=True)
        if self.uploads_directory.exists():
            # Empty out the upload files from previous run
            self.uploads_directory.rmdir()
            self.uploads_directory.mkdir()

config = Config()
config.make()