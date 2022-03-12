import sys
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QLineEdit, QApplication

from Interfaces.download_window import Ui_Dialog


# main window class (to create a window)-sub class of QMainWindow class
class Window(QMainWindow):

    # defining constructor function
    def __init__(self):
        # To generate an executable program, put the absolute directory of the button icons folder
        path = '/Users/sandro/Documents/Programming_Repository/Python/Wallhaven_Download_Engine/Interfaces/button_icons/'
        # creating connnection with parent class constructor
        super(Window, self).__init__()
        # ---------------------adding browser-------------------
        self.browser = QWebEngineView()
        # setting url for browser, you can use any other url also
        self.browser.setUrl(QUrl('http://wallhaven.cc'))
        # to display google search engine on our browser
        self.setCentralWidget(self.browser)
        # -------------------full screen mode------------------
        # to display browser in full screen mode, you may comment below line if you don't want to open your browser in full screen mode
        self.showMaximized()
        # ----------------------navbar-------------------------
        # creating a navigation bar for the browser
        navbar = QToolBar()
        navbar.setIconSize(QSize(20, 20))
        # adding created navbar
        self.addToolBar(navbar)
        # -----------------prev Button-----------------
        # creating prev button
        # prevBtn = QAction('Prev', self)
        prevBtn = QAction(QIcon(f'{path}prev_button.png'), 'prev', self)
        # when triggered set connection
        prevBtn.triggered.connect(self.browser.back)
        # adding prev button to the navbar
        navbar.addAction(prevBtn)
        # -----------------next Button---------------
        nextBtn = QAction(QIcon(f'{path}next_button.png'), 'Next', self)
        nextBtn.triggered.connect(self.browser.forward)
        navbar.addAction(nextBtn)
        # -----------refresh Button--------------------
        refreshBtn = QAction(QIcon(f'{path}refresh_button.png'), 'Refresh', self)
        refreshBtn.triggered.connect(self.browser.reload)
        navbar.addAction(refreshBtn)
        # -----------home button----------------------
        homeBtn = QAction(QIcon(f'{path}home_button.png'), 'Home', self)
        # when triggered call home method
        homeBtn.triggered.connect(self.home)
        navbar.addAction(homeBtn)
        # ---------------------search bar---------------------------------
        # to maintain a single line
        self.searchBar = QLineEdit()
        # when someone presses return(enter) call loadUrl method
        self.searchBar.returnPressed.connect(self.loadUrl)
        # adding created search bar to navbar
        navbar.addWidget(self.searchBar)
        # if url in the searchBar is changed then call updateUrl method
        self.browser.urlChanged.connect(self.updateUrl)
        # -----------------down Button-----------------
        # creating down button
        downBtn = QAction(QIcon(f'{path}Hedgehog_button.png'), 'Download', self)
        #downBtn.setIcon(QtGui.QIcon('button_icons/Hedgehog_button.png'))
        downBtn.triggered.connect(self.open_download_window)
        navbar.addAction(downBtn)

    # method to navigate back to home page
    def home(self):
        self.browser.setUrl(QUrl('http://wallhaven.cc'))

    # method to load the required url
    def loadUrl(self):
        # fetching entered url from searchBar
        url = self.searchBar.text()
        if '.' not in url:
            url = f'google.com/search?q={url}'
        # loading url
        url = url.replace('https://', '')
        self.browser.setUrl(QUrl('http://' + url))

    # method to update the url
    def updateUrl(self, url):
        # changing the content(text) of searchBar
        self.searchBar.setText(url.toString())

    # Show the download window when download button pressed
    def open_download_window(self):
        #self.window = QtWidgets.QDialog()
        self.ui = Ui_Dialog()
        #self.ui.setupUi(self.window)
        self.ui.show()

        self.ui.url = self.searchBar.text()

    # Overwritten the method to close the child windows when the main window closes
    def closeEvent(self, event):
        sys.exit(0)


if __name__ == '__main__':
    MyApp = QApplication(sys.argv)
    # setting application name
    QApplication.setApplicationName('Wallhaven Engine')
    # creating window
    window = Window()
    # executing created app
    MyApp.exec_()

def run():
    MyApp = QApplication(sys.argv)
    # setting application name
    QApplication.setApplicationName('Wallhaven Engine')
    # creating window
    window = Window()
    # executing created app
    MyApp.exec_()

