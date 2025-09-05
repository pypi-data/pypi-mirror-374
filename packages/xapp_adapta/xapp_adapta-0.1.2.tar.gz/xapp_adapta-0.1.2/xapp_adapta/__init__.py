# module initialization
# These are the command imports
# N.B. Ignore the errors and warnings, as the pyproject.toml does use these
from .adapta_test import main as test  # pyright: ignore
from .adapta_main import main  # pyright: ignore
import shutil
from pathlib import Path
import os
import sys

here = Path(__file__).parent
sys.path.insert(0, str(here))
import xapp_adapta.so as so

print(so.hello())
path = os.path.dirname(__file__) + "/"


def copy_with(dir, fn=shutil.copy2):
    # ah, OS kind is for later as Windows/MacOS ...
    home_local = os.path.expanduser("~/.local/share/")
    shutil.copytree(path + dir, home_local + dir, dirs_exist_ok=True, copy_function=fn)


def update_resources(installing):
    # maybe order and refresh is required
    if installing:
        mime = "install"
    else:
        mime = "uninstall"
    for file in os.scandir(os.path.expanduser("~/.local/share/mime/packages")):
        os.system("xdg-mime " + mime + " " + os.fsdecode(file))
    os.system("touch $HOME/.local/share/icons/hicolor && gtk-update-icon-cache")


# make_local icons and desktop files
def make_local():
    copy_with("locale")
    copy_with("icons")
    for file in os.scandir(path + "applications"):
        # fix VIRTUAL ENVIRONMENT in user's local install context
        # and remove the sed backup chaff
        # ooooh some / action ....
        file = os.fsdecode(file)
        os.system(
            "sed -ir 's/\\$VIRTUAL_ENV/"
            + os.path.expandvars("$VIRTUAL_ENV").replace("/", "\\/")
            + "/' "
            + file
            + "&& rm "
            + file
            + "r"
        )
    copy_with("applications")
    copy_with("mime")
    update_resources(True)


# using as a copy function?
def remove(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    return dst


# ininstall
def remove_local():
    # remove app .desktop before icons
    copy_with("mime", fn=remove)
    copy_with("applications", fn=remove)
    copy_with("icons", fn=remove)
    copy_with("locale", fn=remove)
    update_resources(False)
