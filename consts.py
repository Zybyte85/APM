"""Contains global constants"""

import os

HOME = os.path.expandvars("$HOME")
APM_PATH = os.path.join(HOME, ".apm")
ICONS_PATH = os.path.join(APM_PATH, "icons")
REGISTRY_PATH = os.path.join(APM_PATH, "registry.json")


def make_path():
    if not os.path.exists(ICONS_PATH):
        os.makedirs(ICONS_PATH)
    if not os.path.isfile(REGISTRY_PATH):
        f = open(REGISTRY_PATH, "w")
        f.write("{}")
        f.close()
