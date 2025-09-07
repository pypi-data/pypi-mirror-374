
# Core Python.
import sys

# Local.
from .docker import DockerImage

# Get command line inputs.
if len(sys.argv) == 5:
    if (sys.argv[1] == "docker") and (sys.argv[2] == "image") and (sys.argv[3] == "save"):
        image_path = sys.argv[4]
        image = DockerImage(image_path)
        image.pull()
        image.save()

else:
    print("Command does not exist!")