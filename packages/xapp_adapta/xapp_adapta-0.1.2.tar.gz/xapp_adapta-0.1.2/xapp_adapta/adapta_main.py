#!/usr/bin/python3

# sudo apt install libgirepository-2.0-dev
from typing import Callable
import gi
import sys
import os
import subprocess
import importlib.metadata as metadata
import datetime

# import translate, window, module name and app domain
# you do not have to change xapp_adapta as it's gotten from the __file__
from .adapta_test import _, MainWindow, xapp_adapta, domain


gi.require_version("Gtk", "4.0")
gi.require_version("XApp", "1.0")
# so Gtk for graphics
# Gio for data files
# GLib.Error (FileDialog?)
from gi.repository import Gtk, Gio, GLib

# form gi.repository import XApp

# libAdapta uses its own module name (Adap.ApplicationWindow etc..).
# We would normally import it like this:
# from gi.repository import Adap
# Since libAdapta and libAdwaita use the same class names,
# the same code can work with both libraries, as long as we rename
# the module when importing it
try:
    gi.require_version("Adap", "1")
    from gi.repository import Adap as Adw
except ImportError or ValueError as ex:
    # To use libAdwaita, we would import this instead:
    print("Using Adwaita as Adapta not found:\n", ex)
    gi.require_version("Adw", "1")
    from gi.repository import Adw


# no .svg suffix is required
def make_icon(named: str):
    return domain + "." + named


# the app icon id the .py removed filename on the end of the domain
app_name: str = ".".join(os.path.basename(__file__).split(".")[:-1])
app_icon = make_icon(app_name)
notify_proc = []
map_buttons: dict[str, Callable] = {}
datetime_file = datetime.datetime.fromtimestamp(
    os.path.getmtime(os.path.realpath(__file__))
)


# schedule for 1 second using notify_done -> False to one shot
def schedule(arg):
    GLib.timeout_add_seconds(1, notify_done, arg)


# linux dbus message with possible button dictionary { label: Callable, ... }
# so this makes for an easy StatusIcon replacement
# the __qualname__ of the Callable is used to index the calls
def notify(
    message: str,
    body: str | None = None,
    buttons: dict[str, Callable] = {},
    tray: bool = False,
):
    global notify_proc
    b: list[str] = ["notify-send", "-i", app_icon]
    for label in buttons:
        b.append("-A")
        # code and button label
        key = buttons[label].__qualname__
        b.append(key + "=" + label)
        map_buttons[key] = buttons[label]
    if tray:
        b.extend(["-h", "boolean:tray:true"])
        # and botch supress-sound
        b.extend(["-h", "boolean:supress-sound:true"])
    b.extend(["-a", app_name, message])
    # and a body texy if it's not None
    if body is not None:
        b.append(body)
    notify_proc.append(
        subprocess.Popen(
            b,
            stdout=subprocess.PIPE,
            text=True,
        )
    )


# obtain notification button name if available
def notify_done(arg) -> bool:
    global notify_proc
    # schedule test interval one shot
    # print(".")
    # no notifications
    if not notify_proc:
        schedule(arg)
        return False
    # N.B. don't need to iterate over copy as return if communicated
    # No danger of a skipped item
    for p in notify_proc:
        try:
            # apparently this is less blocking than poll() with a .stdout.read()
            out, err = p.communicate(timeout=0)
            # remove the communicated subprocess
            notify_proc.remove(p)
            # retray botch for sort of persistance on clicked button/menu
            # and the message dbus "knowns" how to place a tray icon?
            cmd: list[str] = p.args  # type: ignore
            for i, v in enumerate(cmd):
                if v == "-h":
                    # is hint to retray
                    if cmd[i + 1].lower() == "boolean:tray:true":
                        # maybe it should imply ["-h", "boolean:supress-sound:true"]
                        # so that a notification manager may place it as a tray icon?
                        # This is perhaps a good way of XApp StatusIcons and with
                        # buttons as menus placed in context menu?
                        notify_proc.append(
                            subprocess.Popen(
                                cmd,
                                stdout=subprocess.PIPE,
                                text=True,
                            )
                        )
            todo = map_buttons[out]
            if todo is not None:
                # call it
                todo()
            schedule(arg)
            return False
        except subprocess.TimeoutExpired:
            pass
    schedule(arg)
    return False


# doesn't need to be class method
def button(icon: str, callback: Callable):
    button = Gtk.Button()
    button.set_icon_name(icon)
    button.connect("clicked", callback)
    return button


# the big main window of the application
class MyWindow(MainWindow):  # pyright: ignore
    # override for different behaviour
    def layout(self):
        # this appears in some window managers
        # cinnaman hover taskbar ...
        self.set_title(sys.argv[0])
        self.set_default_size(800, 600)
        self.split_view.set_min_sidebar_width(200)
        self.split_view.set_max_sidebar_width(300)
        # multipaned content by selection widget
        # set list name [] and button nav {}
        self.pages = [self.content()]
        self.buttons = {
            # yes the lest about icon (long close ad) and more oft menu burger UI
            "right": [self.burger()],  # the burger menu
            "left": [button(app_icon, self.about)],  # about icon
            # 1:1 pages match of subtitle injection
            "subs": [_("Sub Title")],
            # 1:1 pages match of icon names injection
            "icons": ["utilities-terminal"],
        }
        # run schedule event loop
        schedule(self)

    # methods to define navigation pages
    def content(self) -> Adw.NavigationPage:
        # Create the content page _() for i18n
        content_box = self.fancy()
        status_page = Adw.StatusPage()
        status_page.set_title("Python libAdapta Example")
        status_page.set_description(
            "Split navigation view, symbolic icon and a calendar widget to feature the accent color."
        )
        status_page.set_icon_name("document-open-recent-symbolic")
        calendar = Gtk.Calendar()
        content_box.append(status_page)
        content_box.append(calendar)
        # set title and bar
        return self.top(content_box, _("Content"), **{})

    # automatic fill of an about dialog from pyproject.toml and built metadata
    def about(self, action):
        about = Gtk.AboutDialog()
        about.set_transient_for(
            self
        )  # Makes the dialog always appear in from of the parent window
        about.set_modal(
            True
        )  # Makes the parent window unresponsive while dialog is showing
        # metadata more in here to auto ...
        authors = metadata.metadata(xapp_adapta).get_all("Author-email")
        if authors is not None:
            # make edit modification of this file be Copyright
            about.set_copyright(
                "©" + str(datetime_file.year) + " " + authors[0].split(" <")[0]
            )
            about.set_authors(authors)
        about.set_license_type(Gtk.License.LGPL_3_0_ONLY)
        urls = metadata.metadata(xapp_adapta).get_all("Project-URL")
        splitter = "Homepage, "
        if urls is not None:
            for u in urls:
                if splitter in u:
                    # about.set_website("https://github.com/jackokring/mint-python-adapta")
                    about.set_website(u.split(splitter)[1])
        about.set_website_label(xapp_adapta)
        about.set_version(metadata.version(xapp_adapta))
        about.set_logo_icon_name(app_icon)
        about.set_visible(True)


# passed command args or open with target
def open_file(name: str):
    # common file import code from CLI and GUI
    print("File to open: " + name + "\n")


# application boiler plate (no editing required)
class MyApp(Adw.Application):  # pyright: ignore
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        self.connect("command-line", self.on_command_line)
        self.set_flags(Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.win = None

    def on_activate(self, app):
        if not self.win:
            # the application window
            self.win = MyWindow(application=app)
        self.win.present()

    def on_command_line(self, app, argv):
        self.on_activate(app)
        for file in argv.get_arguments()[1:]:
            open_file(file)
        return 0


# enter Gtk toolkit event loop
def main():
    app = MyApp(application_id=app_icon)
    sys.exit(app.run(sys.argv))
