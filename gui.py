# Standard QT improts
from PyQt5.QtWidgets import QMainWindow as __QMainWindow

#function to find a free port
def __find_free_port():
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

__port = __find_free_port() 

# QT Brower class
class __MainWindow(__QMainWindow):
    # Webengine for QT in order to make a browser
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    # import QUrl type
    from PyQt5.QtCore import QUrl
    def __init__(self, port, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.browser = self.QWebEngineView()

        self.browser.setUrl(self.QUrl(f"http://localhost:"+str(port)))

        self.browser.loadFinished.connect((lambda: self.setWindowTitle("% s" % self.browser.page().title())))

        self.setCentralWidget(self.browser)
        self.show()

"""
    function: gui_begin(flask_app, name)
        @brief This function runs any given flask app in a seprate custom browser window 

    description:
        It will run any given flask app in a seprate custom browser window,
        Any external links in the app will be visited by browser in the same
        window.

        This allows anyone to make a Desktop gui with the same features as a 
        website Including javascript libraries and css libraries. Allowing for
        flexibility and support for both node side computation in python as well
        as website side libraires.

        Since This is run on a user defined flask server, anyone is able to create
        an interface between the gui and flask much like a localserver
"""
def gui_begin(flask_app, name: str="Gui") -> None:
    from PyQt5.QtWidgets import QApplication

    # The local server must be run on a seprate daemon Thread
    import threading
    threading.Thread(target=(lambda: flask_app.run(port=__port)), daemon=True).start()

    # config for QT application
    import sys
    qt_app: QApplication = QApplication(sys.argv + ['--enable-smooth-scrolling'])
    qt_app.setApplicationName(name)

    # don't show eccessive logs
    import logging
    log: logging.Logger = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # start Brower
    window: __MainWindow = __MainWindow(__port)
    qt_app.exec()
