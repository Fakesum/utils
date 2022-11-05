from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

def __find_free_port():
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

__port = __find_free_port() 

class __MainWindow(QMainWindow):

    def __init__(self, port, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.browser = QWebEngineView()

        self.browser.setUrl(QUrl(f"http://localhost:"+str(port)))

        self.browser.loadFinished.connect((lambda: self.setWindowTitle("% s" % self.browser.page().title())))

        self.setCentralWidget(self.browser)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.show()

def gui_begin(flask_app, name="Gui"):
    import threading
    threading.Thread(target=(lambda: flask_app.run(port=__port)), daemon=True).start()

    import sys
    qt_app = QApplication(sys.argv + ['--enable-smooth-scrolling'])
    qt_app.setApplicationName(name)

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    window = __MainWindow(__port)
    qt_app.exec()
