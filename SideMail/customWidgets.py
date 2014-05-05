#!/usr/bin/env python
__author__ = '@mattanimation'

"""
Hold all the custom pyQt widget in here
"""

from PyQt4 import QtGui,QtCore,QtWebKit
import os, math

import core
import userdata
import utils
from messageviewer import emailWidget

from nodes import Edge, Node, UserNode
from messedit import MessageEditor
import random
from Resources import ui_rc

DEFAULT_ATTACHMENTS = "./attachements"
IMAGES = ["jpg","png","gif","jpeg","bmp"]


class MailWidget(QtGui.QWidget):
    """
    Create the mail widget
    """

    def __init__(self, userdata, parent=None):
        """
        init the main window widget
        @param: userdata - dict, a dict containing the user login info
        """
        QtGui.QWidget.__init__(self,parent)
        self.USERDATA = userdata
        self.messageCenter = core.ImapReader(userdata)
        self.CONTACTS = self.messageCenter.BuildContactList(userdata)

        self.Graph = GraphWidget()
        self.Graph.CreateContactNodes(self.CONTACTS)
        self.Graph.show()

        mboxlist = [item.split()[-1] for item in self.messageCenter.boxes]
        #create the mailbox left hand list
        self.MailBoxList = MailboxList(mboxlist)
        # create the messages for the selected mailbox right hand list
        self.MessageListBox = MessageList()

        self.ContactList = ContactList()

        #create the right side buttons
        self.Controls = MailControls()

        #list and controls to vert layout
        vWidget = QtGui.QWidget(self)
        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(self.Controls)
        vLayout.addWidget(self.MailBoxList)
        vLayout.addWidget(self.MessageListBox)
        vLayout.addWidget(self.ContactList)
        vWidget.setLayout(vLayout)

        #add lists and controls to main layout
        mLayout = QtGui.QHBoxLayout()
        mLayout.addWidget(self.Graph)
        vWidget.setMaximumWidth(250)
        mLayout.addWidget(vWidget)
        self.setLayout(mLayout)

        self.ShowContactList()

        #connect the signals to the buttons/controls
        self.connect(self.Controls.NewMessageButton,
                     QtCore.SIGNAL("clicked()"),
                     self.NewMessage)
        self.connect(self.Controls.DelButton,
                     QtCore.SIGNAL("clicked()"),
                     self.DeleteMessage)
        self.connect(self.Controls.AddContactButton,
                     QtCore.SIGNAL("clicked()"),
                     self.AddNewContact)
        self.connect(self.MailBoxList,
                     QtCore.SIGNAL("ShowBox( QString )"),
                     self.ShowMessageList)
        self.connect(self.MessageListBox,
                     QtCore.SIGNAL("ShowMessage( QString )"),
                     self.ShowHTMLMessage)
        self.connect(self.MailBoxList,
                     QtCore.SIGNAL("dropped ()"),
                     self.MoveMessage)

    def ShowMessageList(self,item):
        """
        Create the list of messages in a selected mailbox
        """
        self.messageCenter.SelectBox(str(item).split()[-1])
        self.messageDict = self.messageCenter.GetMessages()
        displaylist = ["%s\t%s\tFrom:%s"%(a,b.get('subject'),b.get('from')) for (a,b) in self.messageDict.items()]
        displaylist.sort(key=lambda x: int(x.split('\t')[0]),reverse=True)
        self.MessageListBox.RefreshList(displaylist)


    def ShowHTMLMessage(self,item):
        """
        select a message from the mailbox and display in a new widget
        """
        this_message = self.messageDict.get(str(item).split('\t')[0])
        self.HTML = emailWidget(this_message,self.USERDATA)
        self.HTML.show()

    def ShowContactList(self, item=None):
        """
        create a list from the contacts data
        """
        self.ContactList.RefreshList(self.CONTACTS["contacts"])

    def OpenContactInfo(self, item):
        """
        load the clicked on contacts info
        """
        print "eh?"

    def AddNewContact(self):
        """
        create a new contact and add a node
        """
        #show the contact dialog
        ncWin = NewContactWidget(self.USERDATA, self.Graph)
        QtGui.QMainWindow.layout.addWidget(ncWin)


    def NewMessage(self, address=""):
        """
        create a new window to send a message
        @param address: default address to set as to field
        @type address: str
        """
        self.newMessage = MessageEditor(self.USERDATA, address)
        self.newMessage.show()

    def DeleteMessage(self):
        """
        get selected message from list and delete it
        """
        mi = self.MessageListBox.getSelected()
        if mi:
            self.messageCenter.DeleteMessage(mi)
            self.ShowMessageList(self.MailBoxList.currentItem().text())

    def MoveMessage(self):
        """
        move a message from a give mailbox
        """
        box = self.MailBoxList.currentItem()
        mess = self.MessageListBox.currentItem()
        if box and mess:
            self.messageCenter.MoveMessage(str(mess.text()).split('\t')[0],str(box.text()))
            self.ShowMessageList(self.messageCenter.MBOX)

class MailControls(QtGui.QWidget):
    """
    The main control buttons
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.NewMessageButton = QtGui.QPushButton("New Message", self)
        self.DelButton = QtGui.QPushButton("Delete",self)
        self.PurgeButton = QtGui.QPushButton("Purge Deleted",self)
        self.AddContactButton = QtGui.QPushButton("Add Contact", self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.NewMessageButton)
        layout.addWidget(self.DelButton)
        layout.addWidget(self.PurgeButton)
        layout.addWidget(self.AddContactButton)
        
        self.setLayout(layout)

class GraphWidget(QtGui.QGraphicsView):
    """
    This is the main graph widget that will house the nodes
    """
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.timerId = 0

        self.mainScene = QtGui.QGraphicsScene(self)
        self.mainScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        #self.mainScene.setSceneRect(-200, -200, 400, 400)
        self.setScene(self.mainScene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)


        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle("Elastic Nodes")

    def CreateContactNodes(self, contactList):
        """
        @param contactList - list - all email addresses
        """

        #initially here the nodes should be created based on the contacts list of the user
        #use the contact data and create nodes

        node1 = Node(self)
        node2 = Node(self)
        node3 = Node(self)
        node4 = Node(self)
        self.centerNode = UserNode(self)
        node6 = Node(self)
        node7 = Node(self)
        node8 = Node(self)
        node9 = Node(self)
        self.mainScene.addItem(node1)
        self.mainScene.addItem(node2)
        self.mainScene.addItem(node3)
        self.mainScene.addItem(node4)
        self.mainScene.addItem(self.centerNode)
        self.mainScene.addItem(node6)
        self.mainScene.addItem(node7)
        self.mainScene.addItem(node8)
        self.mainScene.addItem(node9)

        self.mainScene.addItem(Edge(node1, node2))
        self.mainScene.addItem(Edge(node2, node3))
        self.mainScene.addItem(Edge(node2, self.centerNode))
        self.mainScene.addItem(Edge(node3, node6))
        self.mainScene.addItem(Edge(node4, node1))
        self.mainScene.addItem(Edge(node4, self.centerNode))
        self.mainScene.addItem(Edge(self.centerNode, node6))
        self.mainScene.addItem(Edge(self.centerNode, node8))
        self.mainScene.addItem(Edge(node6, node9))
        self.mainScene.addItem(Edge(node7, node4))
        self.mainScene.addItem(Edge(node8, node7))
        self.mainScene.addItem(Edge(node9, node8))

        node1.setPos(-50, -50)
        node2.setPos(0, -50)
        node3.setPos(50, -50)
        node4.setPos(-50, 0)
        self.centerNode.setPos(0, 0)
        node6.setPos(50, 0)
        node7.setPos(-50, 50)
        node8.setPos(0, 50)
        node9.setPos(50, 50)

        #create nodes by number of contacts
        i=0
        for c in contactList["contacts"]:
            #print c
            if i < 10:
                self.AddNode(c)
            i += 1

    def itemMoved(self):
        if not self.timerId:
            self.timerId = self.startTimer(1000 / 25)

    def AddNode(self, address=""):
        newNode = Node(self)
        newNode.address = address
        self.mainScene.addItem(newNode)
        self.mainScene.addItem(Edge(newNode, self.centerNode))
        newNode.setPos(random.randint(-100, 100),random.randint(-100, 100))


    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Up:
            self.centerNode.moveBy(0, -20)
        elif key == QtCore.Qt.Key_Down:
            self.centerNode.moveBy(0, 20)
        elif key == QtCore.Qt.Key_Left:
            self.centerNode.moveBy(-20, 0)
        elif key == QtCore.Qt.Key_Right:
            self.centerNode.moveBy(20, 0)
        elif key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
            for item in self.scene().items():
                if isinstance(item, Node):
                    item.setPos(-150 + QtCore.qrand() % 300, -150 + QtCore.qrand() % 300)
        else:
            super(GraphWidget, self).keyPressEvent(event)

    def timerEvent(self, event):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]

        for node in nodes:
            node.calculateForces()

        itemsMoved = False
        for node in nodes:
            if node.advance():
                itemsMoved = True

        if not itemsMoved:
            self.killTimer(self.timerId)
            self.timerId = 0

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, event.delta() / 240.0))

    def drawBackground(self, painter, rect):
        # Shadow.
        """
        sceneRect = self.sceneRect()
        rightShadow = QtCore.QRectF(sceneRect.right(), sceneRect.top() + 5, 5,
                sceneRect.height())
        bottomShadow = QtCore.QRectF(sceneRect.left() + 5, sceneRect.bottom(),
                sceneRect.width(), 5)
        if rightShadow.intersects(rect) or rightShadow.contains(rect):
	        painter.fillRect(rightShadow, QtCore.Qt.darkGray)
        if bottomShadow.intersects(rect) or bottomShadow.contains(rect):
	        painter.fillRect(bottomShadow, QtCore.Qt.darkGray)"""

        # Fill.
        """
        gradient = QtGui.QLinearGradient(sceneRect.topLeft(),
                sceneRect.bottomRight())
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(1, QtCore.Qt.lightGray)
        painter.fillRect(rect.intersect(sceneRect), QtGui.QBrush(gradient))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(sceneRect)"""

        # Text.
        #textRect = QtCore.QRectF(sceneRect.left() + 4, sceneRect.top() + 4,
        #        sceneRect.width() - 4, sceneRect.height() - 4)
        #message = "Click and drag the nodes around, and zoom with the " \
        #        "mouse wheel or the '+' and '-' keys"

        """
        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.lightGray)
        painter.drawText(textRect.translated(2, 2), message)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(textRect, message)"""
        fillCol = QtGui.QColor()
        fillCol.setRgb(18, 19, 20, alpha=255)
        painter.setBrush(fillCol)
        painter.drawRect(self.sceneRect())
        

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)



class NewContactWidget(QtGui.QWidget):
    """
    create a form to add a new contact
    """
    def __init__(self, userdata, graph, name="", eaddress="", twit="", fb="",  parent=None):
        """
        init the window
        """
        super(NewContactWidget, self).__init__()

        self.USERDATA= userdata
        self.mainGraph = graph

        mLayout = QtGui.QVBoxLayout()
        self.setLayout(mLayout)

        fLayout = QtGui.QFormLayout()
        fWidget = QtGui.QWidget()
        fWidget.setLayout(fLayout)

        nLabel = QtGui.QLabel("Name: ")
        self.cName = QtGui.QLineEdit(name ,self)
        eLabel = QtGui.QLabel("Email: ")
        self.cEadd = QtGui.QLineEdit(eaddress, self)
        twitLabel = QtGui.QLabel("Twitter: ")
        self.cTwit = QtGui.QLineEdit(twit, self)
        fbLabel = QtGui.QLabel("Facebook: ")
        self.cFb = QtGui.QLineEdit(fb, self)

        self.cOK = QtGui.QPushButton("OK", self)
        self.cCancel = QtGui.QPushButton("Cancel",self)


        bWidget = QtGui.QWidget()
        bLayout = QtGui.QHBoxLayout()
        bWidget.setLayout(bLayout)

        bLayout.addWidget(self.cOK)
        bLayout.addWidget(self.cCancel)

        fLayout.addRow("&Name: ",self.cName)
        fLayout.addRow("&Email: ", self.cEadd)
        fLayout.addRow("&Twitter: ", self.cTwit)
        fLayout.addRow("&Facebook: ", self.cFb)

        mLayout.addWidget(fWidget)
        mLayout.addWidget(bWidget)

        self.connect(self.cOK,QtCore.SIGNAL("clicked()"),self.OKpressed)
        self.connect(self.cCancel,QtCore.SIGNAL("clicked()"),self.CANCELpressed)


        self.show()

    def OKpressed(self):
        """
        """
        self.mainGraph.AddNode()

    def CANCELpressed(self):
        """
        """
        self.close()



class EmailWidget(QtGui.QWidget):
    """
    Main message widget
    """
    def __init__(self,email_message,userdata, parent=None):
        """
		This will break the data form of an email message into components handled by the appropriate widgets
		"""
        self.USERDATA = userdata
        self.email_message = email_message
        QtGui.QWidget.__init__(self,parent)
        MyLayout = QtGui.QGridLayout()
        body = email_message.get('body')[0][1]
        self.display = TextViewer(body)
        MyLayout.setColumnMinimumWidth(1,500)
        MyLayout.addWidget(self.display,1,1)
        self.body_index = 0
        self.setLayout(MyLayout)
        self.reply = QtGui.QPushButton("Reply",self)
        self.connect(self.reply,QtCore.SIGNAL("clicked()"),self.Reply)
        self.layout().addWidget(self.reply,2,1)

        self.saveall = QtGui.QPushButton("Save All Attachments",self)
        self.connect(self.saveall,QtCore.SIGNAL("clicked()"),self.SaveAll)
        self.layout().addWidget(self.saveall,2,2)

        self.aList = attachmentList()
        self.layout().addWidget(self.aList,1,2)
        self.aList.RefreshList(email_message.get('attachments'))

    def sendBody(self):
        """

        """
        bodies = self.email_message.get('body')
        self.body_index += 1
        if self.body_index >= len(bodies):
            self.body_index = 0
        return bodies[self.body_index][1]

    def SaveAll(self):
        """
        """
        filename = QtGui.QFileDialog.getExistingDirectory(None, "Save As", "%s"%(DEFAULT_ATTACHMENTS))
        for item in self.email_message.get('attachments'):
            outfile = '%s/%s'%(filename,item[0])
            i = 1
            while os.path.exists(outfile):
                postfix = outfile.split('.')
                outfile = "%s(%s).%s"%('.'.join(postfix[:-1]),i,postfix[-1])
                i += 1
            outfile = open(outfile,'wb')
            outfile.write(utils.BinaryDecode(item[3],item[2]))
            outfile.close()

    def Reply(self):
        """
        """
        self.editor = MessageEditor(self.USERDATA)
        self.editor.ReplyTo(self.email_message,self.body_index)
        self.editor.show()

class TextViewer(QtGui.QTextBrowser):
    """

    """
    def __init__(self,main, parent=None):
        """
        """
        QtGui.QTextBrowser.__init__(self,parent)
        self.setHtml(main.replace("\n","<br/>"))

        self.nb = QtGui.QAction(self)
        self.nb.setShortcut('Ctrl+N')
        self.addAction(self.nb)
        self.connect(self.nb, QtCore.SIGNAL('triggered()'),self.nextbody)

    def nextbody(self):
        """
        """
        content = (self.parent().sendBody()).replace('\n','<br/>')
        self.setHtml(content.encode('utf-8'))


class AttachmentList(QtGui.QListWidget):
    """

    """
    def __init__(self,parent=None):
        """
        """
        QtGui.QListWidget.__init__(self,parent)
        self.connect(self,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),self.OpenAttachment)
        self.attachments = {}

    def RefreshList(self,newatt):
        """
        """
        self.clear()
        self.attachments = {}
        for item in newatt:
            self.addItem(item[0])
            self.attachments[item[0]] = utils.BinaryDecode(item[3],item[2])

    def OpenAttachment(self,listitem):
        """
        """
        itext = listitem.text()
        print itext
        data = self.attachments.get(str(itext))
        if str(itext.split('.')[-1]).lower() in IMAGES:
            self.DisplayImage(itext,data)
        else:
            filename = QtGui.QFileDialog.getSaveFileName(None,"Save As", "%s/%s"%(DEFAULT_ATTACHMENTS,itext))
            if len(filename)>0:
                outfile = open(filename,'wb')
                outfile.write(data)
                outfile.close()

    def DisplayImage(self,filename,imagedata):
        """
        """
        self.Image = QtGui.QLabel(None)
        newPixmap = QtGui.QPixmap()
        newPixmap.loadFromData(imagedata,str(filename.split('.')[-1]).upper())
        self.Image.setPixmap(newPixmap)
        self.Image.show()


class MailboxList(QtGui.QListWidget):
    """
    Create a list that holds the email folders
    """

    def __init__(self,mailboxes,parent=None):
        QtGui.QListWidget.__init__(self,parent)
        self.datalist = list(mailboxes)
        self.addItems(self.datalist)
        self.connect(self,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),self.itemholler)
        self.setDragDropMode(QtGui.QAbstractItemView.DropOnly)

    def dragMoveEvent(self, event):
        self.setCurrentIndex(self.indexAt(event.pos()))

    def dropEvent(self, event):
        self.emit(QtCore.SIGNAL("dropped()"))

    def itemholler(self,item):
        self.emit(QtCore.SIGNAL("ShowBox( QString )"),item.text())
    
class MessageList(QtGui.QListWidget):
    """
    Create a list the holds them messages for the selected mailbox
    """

    def __init__(self,parent=None):
        QtGui.QListWidget.__init__(self,parent)
        self.connect(self,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                    self.OpenLetter)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.Drag = QtGui.QDrag(self)
        
    def RefreshList(self,newlist):
        self.clear()
        self.addItems(list(newlist))

    def OpenLetter(self,item):
        self.emit(QtCore.SIGNAL("ShowMessage(QString)"),item.text())
        print "message"

    def getSelected(self):
        if self.currentItem():
            return str(self.currentItem().text()).split('\t')[0]
        else:
            return None

class ContactList(QtGui.QListWidget):
    """
    Create a list to hold all the contacts (might not stick around)
    """

    def __init__(self,parent=None):
        QtGui.QListWidget.__init__(self,parent)
        self.connect(self,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),self.OpenLetter)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.Drag = QtGui.QDrag(self)

    def RefreshList(self,newlist):
        self.clear()
        self.addItems(list(newlist))

    def OpenLetter(self,item):
        self.emit(QtCore.SIGNAL("ShowMessage(QString)"),item.text())
        print item.text() + " selected"
        #open the contact in a new window and email message

    def getSelected(self):
        if self.currentItem():
            return str(self.currentItem().text()).split('\t')[0]
        else:
            return None

class attachmentList(QtGui.QListWidget):
    """
    Create a list of attachments to any given email message
    """

    def __init__(self,parent=None):
        QtGui.QListWidget.__init__(self,parent)
        self.connect(self,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),self.OpenLetter)

    def RefreshList(self,newlist):
        self.clear()
        self.addItems(list(newlist))

    def OpenLetter(self,item):
        self.emit(QtCore.SIGNAL("ShowMessage(QString)"),item.text())
        print "message"
        
        
class DictionaryCompleter(QtGui.QCompleter):
    """Predefined QCompleter"""
    def __init__(self, wordArr, parent=None):
        """Create a new dictionary completer"""
        QtGui.QCompleter.__init__(self, wordArr, parent)
        
class CompletionTextEdit(QtGui.QTextEdit):
    """Custom QTextEdit that supports completion"""
    def __init__(self, parent=None):
        """Create a new CompletionTextEdit"""
        super(CompletionTextEdit, self).__init__(parent)

        self.completer = None
        self.previousKey = None

        self.resize(300, 25)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.setStyleSheet("""
        QTextEdit:active {
            background-color: rgb(50,50,50);
            background-image: url(%s);
            background-attachment: scroll;
            border: 2px solid #222222;
            /*border-color: red;*/
        }
        """ % (utils.get_resources_path() + 'background.png'))

    def showAtMouse(self):
        """Show this text edit at the current mouse position"""
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y()+ self.height()*0.5)
        self.show()

    def setCompleter(self, inCompleter):
        """Set the completer of the text edit
        @param (QCompleter)"""
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not inCompleter: return

        inCompleter.setWidget(self)
        inCompleter.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        inCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = inCompleter
        self.completer.activated.connect(self.insertCompletion)
        
    def insertCompletion(self, completion):
        """Insert the current completion into the text widget"""
        tc = self.textCursor()

        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        # Insert rest of the word
        tc.insertText(completion[len(self.completer.completionPrefix()):])
        self.setTextCursor(tc)

    def focusInEvent(self, event):
        """Set the widget of the completer when got focus"""
        if self.completer: self.completer.setWidget(self);
        QtGui.QTextEdit.focusInEvent(self, event)

    def textUnderCursor(self):
        """Get the text under the cursor"""
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        """Callback when the user presses a button"""
        # If enter is pressed, execute the current text
        # If control/shift + enter is pressed, add newline and make the line edit bigger
        if event.key() == QtCore.Qt.Key_Return:
            if (self.previousKey == QtCore.Qt.Key_Control or self.previousKey == QtCore.Qt.Key_Shift):
                tc = self.textCursor()
                tc.insertText('\n')
                self.setTextCursor(tc)
                self.resize(300, self.height()+13)
                return
            else:
                self.executeText()
                self.close()
                return

        self.previousKey = event.key() # Save the pressed key

        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.Key_Backtab):
                event.ignore()
                self.completer.popup().hide()
                return

        QtGui.QTextEdit.keyPressEvent(self, event)

        eow = ("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=") #end of word

        if (len(event.text()) == 0 or event.text()[-1] in eow):
            self.completer.popup().hide()
            return

        completionPrefix = self.textUnderCursor()
        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(
                self.completer.completionModel().index(0,0))
        
        cr = self.cursorRect()
        cr.setWidth(200)

        # Complete! Pop it up..
        self.completer.complete(cr)
        
    def mousePressEvent(self, event):
        """Callback when the user clickes in the window
        Close the window"""
        self.close()

    def focusOutEvent(self, event):
        """Callback when the window looses focus
        Close the window"""
        self.close()

    def isPath(self, text):
        """Check if string is a path
        @param text (string)
        @return (boolean)"""
        if text.startswith('//depot') or os.path.exists(text):
            return True
        else: return False



    def executeText(self):
        """Execute the text from the text edit"""
        # Convert to plain text
        txt = '%s' % self.toPlainText()
        if len(txt) == 0: return

        # If it's a file, open it
        if self.isPath(txt): 
            self.openFile(txt)
            return
        
        # If the first caracter is _ consider the the text as python code, 
        # otherwise check if it is a keyword
        """
        if txt[0] != pythonCodePrefix:
            try:
                txt = dict((k.lower(), v) for k,v in mayaCommandsDict.iteritems())[txt.lower()]
            except KeyError: pass
            try:
                txt = dict((k.lower(), v) for k,v in companyCommandsDict.iteritems())[txt.lower()]
            except KeyError: pass
            try:
                txt = dict((k.lower(), v) for k,v in userCommandsDict.iteritems())[txt.lower()]  
            except KeyError: pass
        else: # Python code
            txt = txt[1:]
        """
        # Execute the text    
        exec(str(txt))

        # Hide the popup
        self.completer.popup().hide()
