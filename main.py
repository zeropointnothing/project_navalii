import sys
import os
import hashlib
import json
import time
import subprocess
import traceback
from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

# C:\Users\username\AppData\Local\Navalii Browser\QtWebEngine\Default
blockerSites = [
    "tpc.googlesyndication.com/simgad/",
    "adclick.g.doubleclick.net/",
    "googleads.g.doubleclick.net",
    'https://s0.2mdn.net/simgad/',
    "https://static.pc-adroute",
    "adroute",
    "https://img.gsspat.jp",

    'ezoic',
    "google_image",
    'ad_unit',
    'google_image_div',
    'GoogleActiveViewElement',
    "amznBanners_assoc_banner",
    "google_ads",
    "gnpbad_",
]


def cls():
    """
    Clears the screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Logger:
    """
    Logger.
    """

    def __init__(self):
        self.name = "NAVA"

    def info(self, text: str | None) -> None:
        """
        For general information.
        """
        if not text:
            return

        print(f"[{time.strftime('%H:%M:%S')}] {self.name}: " + text)
        sys.stdout.flush()

    def warn(self, text: str | None) -> None:
        """
        For less serious, but still noteworthy problems.
        """
        if not text:
            return

        print(f"[{time.strftime('%H:%M:%S')}] {self.name}:WARNING: " + text)
        sys.stdout.flush()

    def error(self, text: str | None) -> None:
        """
        For critical bugs, usually followed by the program halting or the process restarting.
        """
        if not text:
            return

        print(f"[{time.strftime('%H:%M:%S')}] {self.name}:ERROR: " + text)
        sys.stdout.flush()


log = Logger()


class NavaRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        for site in blockerSites:
            if site in url:
                # Block the request by setting it to an empty URL
                log.info(f"Blocked request to black-listed URL: {url}")

                info.redirect(QUrl("about:blank"))


class MainWindow(QMainWindow):
    def __init__(self, nava, config, web_view):
        sys.excepthook = self.excepthook

        super(MainWindow, self).__init__()
        self.browser = web_view

        self.home = "https://zeropointnothing.github.io" if not config["browser"]["home"] else config["browser"]["home"]
        self.version = "v0.0.2-alpha"
        self.config = config
        self.navacfg = nava

        self.browser.setUrl(QUrl(self.home))
        self.setCentralWidget(self.browser)

        self.showMaximized()

        # navbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        back_btn = QAction('Back', self)
        back_btn.setToolTip("Go back to the previous page.")
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        foreward_btn = QAction('Foreward', self)
        foreward_btn.setToolTip("Go foreward one page.")
        foreward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(foreward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.setToolTip("Reload the page.")
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)
        self.browser.titleChanged.connect(self.update_title)
        self.browser.page().profile().downloadRequested.connect(self.on_downloadRequested)

    def navigate_home(self):
        """
        Return to home page.
        :return:
        """
        # self.update_title("Loading...")

        self.browser.setUrl(QUrl(self.home))

    def update_title(self, title=None):
        self.browser.window().setWindowTitle(f"{title} - Navalii Web Browser")

    def update_url(self, q):
        """
        Update the url so it can display correctly in the url bar.
        :param q:
        :return:
        """
        self.url_bar.setText(q.toString())

        # self.update_title()

    def navigate_url(self):
        """
        Navigate to the url contained in the url_bar.
        :return:
        """
        url: str = self.url_bar.text()

        self.update_title("Loading...")

        if not url.startswith("https://"):
            # If the user has set the search-non-valid key to True, search for any non valid urls.
            # else, assume it was supposed to be a link.
            if self.config["browser"]["default_search-non-valid"]:
                url = "https://www.google.com/search?q=" + url
            else:
                url = "https://" + url

        self.browser.setUrl(QUrl(url))

        # raise AttributeError("men")
        #
        # page = self.browser.page()
        #
        # page.profile().cookieStore().deleteAllCookies()

    def on_downloadRequested(self, download):
        old_path = download.path()
        suffix = QFileInfo(old_path).suffix()
        path, _ = QFileDialog.getSaveFileName(self.browser.page().view(), "Save File", old_path, "*." + suffix)
        if path:
            download.setPath(path)
            download.accept()

    def excepthook(self, exctype, value, tb):
        """
        Hook for all exceptions so that the VoxelEngine may shut down and have the error handling be taken over.
        """

        # Don't handle CTRL+C errors.
        if exctype == KeyboardInterrupt:
            sys.exit()

        # Obtain the full exception details as a string
        full_exception = "".join(traceback.format_exception(exctype, value, tb))

        # Replace line breaks with lnbrk
        full_exception = full_exception.replace("\n", "lnbrk")

        # Hand over the error handling to error.py so the VoxelEngine can completely shut down.
        subprocess.Popen(
            ["start", "cmd", "/k", "python", "./assets/error.py", "--fullexc", full_exception, "--details",
             f"{exctype.__name__}: {value}"],
            shell=True,
        )

        sys.exit()


def initNavalii():
    """
    Setup function for Navlii.
    :return:
    """
    if not os.path.isfile("./nava.json"):
        print("Unable to load Navalii config. Entering setup mode.")
        sleep(3)

        cls()

        print("Welcome!")
        print("This setup utility will get you ready for browsing on Navlii!")
        print()
        print("First, let's set up your account. This is just local and is used to store your Favorites and "
              "customization.")

        print()
        username = input("Enter a username: ")
        password = input("Enter a password or leave it blank for none: ")

        print()
        print(f"{username} is a wonderful name!")
        print("Give us a second to prepare some files...")
        sleep(2)

        if password:
            password = hashlib.new("sha256", password.encode()).hexdigest()
        else:
            password = None

        with open("./nava.json", "w") as f:
            json.dump(
                {"user":
                    {
                        "name": username,
                        "password": password,
                        "bookmarks": []
                    }
                },
                f)

        with open("./config.json", "w") as f:
            json.dump({
                "browser": {
                    "home": None,
                    "s-engine": "google",
                    "default_search-non-valid": True,
                    "default_block-ad-urls": False
                }
            }, f)

        cls()
        print("Done!")
        print()
        print(f"Welcome, {username}, to your Navlii.")
        sleep(4)
        cls()

    if not os.path.isfile("./config.json"):
        raise FileNotFoundError("nava config was found, but user config was not. Code: c:001")

    with open("./nava.json", "r") as f:
        navadat = json.load(f)
    with open("./config.json", "r") as f:
        configdat = json.load(f)

    return {"nava": navadat, "config": configdat}


initdata = initNavalii()

if initdata["nava"]["user"]["password"]:
    print("This account requires a password to log in.")
    password = input("Please input your password: ")
    password = hashlib.new("sha256", password.encode()).hexdigest()

    if password != initdata["nava"]["user"]["password"]:
        print("Incorrect password!")
        sleep(2)
        sys.exit()
    print()

app = QApplication(sys.argv)
QApplication.setApplicationName("Navalii Browser")
app.setWindowIcon(QIcon("assets/navalii_icon.png"))

web_view = QWebEngineView()


if initdata["config"]["browser"]["default_block-ad-urls"]:
    if os.path.isfile("./bl.json"):
        with open("./bl.json", "r") as f:
            data = json.load(f)

            # Funnel all requests through this function to filter them for ads.
            blockerSites.append(*data)
            request_interceptor = NavaRequestInterceptor()
            web_view.page().profile().setRequestInterceptor(request_interceptor)

window = MainWindow(initdata["nava"], initdata["config"], web_view)

print(f"Welcome to Navalii, {initdata['nava']['user']['name']}!")
print()
print(f"Running version {window.version}")
print("Note: This is a debug console tied to the main window. You may see many errors or warnings from Javascript.")
print("You can ignore these unless they are crash related.")
print("In future versions, this console window will be hidden.")
print()

sys.exit(app.exec_())
