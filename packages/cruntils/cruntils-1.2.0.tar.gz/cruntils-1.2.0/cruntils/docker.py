
# Core Python.
import json
import subprocess

class DockerImage:
    def __init__(self, image_path: str = ""):
        """Constructor"""
        self.image_path: str = image_path
    #==========================================================================
    # Internal, alphabetic.
    def _get_details(self):
        """Get image details."""
        cmd_parts = ["docker", "image", "inspect", self.image_path]
        proc = subprocess.run(
            cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.details = json.loads(proc.stdout)
    def get_id(self):
        """Get image ID"""
        self._get_details()
        return self.details[0]["Id"]
    #==========================================================================
    # External, alphabetic.
    def set_path(self, image_path: str):
        """Set the image path"""
        self.image_path = image_path
    def pull(self):
        """Pull image to local machine"""
        print(f"Pulling image {self.image_path}", end="", flush=True)
        cmd_parts = [
            "docker",
            "image",
            "pull",
            self.image_path
            ]
        proc = subprocess.run(
            cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("done!")
    def archive_name_to_image_path(self, archive_name: str):
        """Work out image path from archive name"""
        pass
    def get_archive_name(self):
        """Work out archive name from image path"""
        image_archive_name = self.image_path.replace("-", "_")
        image_archive_name = image_archive_name.replace("/", "__")
        image_archive_name = image_archive_name.replace(":", "___")
        return image_archive_name
    def save(self):
        """Save image to tar file"""
        print(f"Saving image {self.image_path} to archive file...", end="", flush=True)
        cmd_parts = [
            "docker",
            "image",
            "save",
            "--output-string",
            self.get_archive_name(),
            self.image_path
        ]
        proc = subprocess.run(
            cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"done!")