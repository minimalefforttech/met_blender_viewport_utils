# rez package configuration
name = "met_blender_viewport_utils"
version = "0.0.1"
authors = ["alex.telford"]
description = "minimaleffort.tech Blender specific viewport utilities"
requires = [
    "python-3.9+<3.12",
    "blender-3.6+<4.1",
    "numpy-1.23+<2",
    "met_viewport_utils-0.1.1<0.2.0",
]
build_requires = [
    "python-3.9+<3.12",
]
tools = []
variants = []
build_command = "python {root}/build.py {install}"

tests = {}  # TODO

def commands():
    env.MET_BLENDER_VIEWPORT_UTILS_ROOT = "{this.root}"
    env.MET_BLENDER_VIEWPORT_UTILS_VERSION = "{version}"
    env.PYTHONPATH.append("{this.root}/python")
