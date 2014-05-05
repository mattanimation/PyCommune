#!/usr/bin/env python
"""
@newField description: Description
@newField revisions: Revisions
@newField applications: Applications

@author: Matt Murray [@mattanimation]
@organization: Atmos Interactive LLC
@description: This is the main entry file for SideMail

@revisions:
            -04.28.2014

@todo:
        A TON!
        -figure out how to mask image for user node
        -draw to background of whole graphWidget area
        -change userdata file to merge to core or utils
        -update userdata filename and data structre to add user image
        -get all custom images under one module
        -figure out how to do transparent widgets
        -figure out how to animate widgets in layout   

"""
VERSION = 0.01

#----------------------------------------------------------------------------#
#----------------------------------------------------------------- IMPORTS --#
# Built-in
import sys, os, math, logging

# Third-Party

# UI related
from PyQt4 import QtGui,QtCore

import SideMail.utils as utils
import SideMail.userdata as userdata
import SideMail.customWidgets as customWidgets
import SideMail.core as core

logging.basicConfig(level=logging.DEBUG)


#----------------------------------------------------------------------------#
#--------------------------------------------------------------- FUNCTIONS --#
def main():
    """
    This is where the main program execution begins.
    @return: None
    """
    app = QtGui.QApplication(sys.argv)
    app.setStyle('Plastique')
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))

    #make a splash screen to show while application initializes
    screendir = os.path.dirname(os.path.abspath('__file__'))
    pixmap = QtGui.QPixmap(os.path.join(screendir,"SideMail/Resources/splashscreen.png"))
    splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(pixmap.mask())
    splash.show()
    splash.showMessage((u'Starting...'),
                       QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,
                       QtCore.Qt.yellow)
    
    app.processEvents()
    widget = SideMail()
    widget.show()
    #hide splash when done loading
    splash.finish(widget)

    sys.exit(app.exec_())
    

#----------------------------------------------------------------------------#
#----------------------------------------------------------------- CLASSES --#

class SideMail(QtGui.QMainWindow):
    """This is my main window for my email client.
    """
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self, parent) # frameless window QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint
        self.setGeometry(150,150,800,600)
        self.setWindowTitle("SideMail v{0}".format(VERSION))

        #load styledata
        self.styleData = utils.get_stylesheet()

        #user data file is stored in c:\\users\matt as .imapqt
        USERDATA = userdata.GetUserData()
        print "derp {0}".format(USERDATA)
        #if ret==1:
        #   QtGui.QApplication.quit()
        #else:
        
        #this will hold all ui elements throughout application
        self.uiWidgets = {}
        
        self.CreateActions()
        self.CreateMenu()
        self.uiWidgets['mailWidget'] = customWidgets.MailWidget(USERDATA)
        self.setCentralWidget(self.uiWidgets['mailWidget'])
        self.setStyleSheet(self.styleData)
        
        #load any external plugins here after building core ui?
        pl = core.PluginLoader()
        #test calling a command from plugins
        pl.test_command("foo")
        

    def CreateMenu(self):
        """
        Create the main menu bar
        """
        self.uiWidgets['fileMenu'] = self.menuBar().addMenu("&File")
        self.uiWidgets['fileMenu'].addAction(self.exitAction)

        self.uiWidgets['itemMenu'] = self.menuBar().addMenu("&Item")
        self.uiWidgets['itemMenu'].addAction(self.deleteAction)
        self.uiWidgets['itemMenu'].addSeparator()
        self.uiWidgets['itemMenu'].addAction(self.toFrontAction)
        self.uiWidgets['itemMenu'].addAction(self.sendBackAction)

        self.uiWidgets['aboutMenu'] = self.menuBar().addMenu("&Help")
        self.uiWidgets['aboutMenu'].addAction(self.aboutAction)

    def CreateActions(self):
        """
        create the actions that are tied to the menu bar
        """
        self.toFrontAction = QtGui.QAction(
            QtGui.QIcon(':/images/bringtofront.png'), "Bring to &Front",
            self, shortcut="Ctrl+F", statusTip="Bring item to front",
            triggered=self.bringToFront)

        self.sendBackAction = QtGui.QAction(
            QtGui.QIcon(':/images/sendtoback.png'), "Send to &Back", self,
            shortcut="Ctrl+B", statusTip="Send item to back",
            triggered=self.sendToBack)

        self.deleteAction = QtGui.QAction(QtGui.QIcon(':/images/delete.png'),
                                          "&Delete", self, shortcut="Delete",
                                          statusTip="Delete item from diagram",
                                          triggered=self.deleteItem)

        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+X",
                                        statusTip="Quit Scenediagram example", triggered=self.close)


        self.aboutAction = QtGui.QAction("A&bout", self, shortcut="Ctrl+B",
                                         triggered=self.about)

    def deleteItem(self):
        pass

    def bringToFront(self):
        pass

    def sendToBack(self):
        pass

    def about(self):
        """
        show a small pop-up dialog with info about author/check for updates
        """
        mb = utils.generic_msg("""SideMail is a product of \n
        Atmos Interactive LLC. Please Use At Own RISK!""",
                               "info",
                               True)
        #mb.setStyleSheet(self.styleData)

    def closeEvent(self, event):
        #close Imap connection
        self.centralWidget().messageCenter.EndSession()
        event.accept()
        QtGui.QApplication.quit()




if __name__ == "__main__":
    main()

