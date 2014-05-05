from PyQt4 import QtGui,QtCore
import sys
import smtplib,time,base64
import utils
from userdata import UserData
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import email.iterators as iterators

class MessageEditor(QtGui.QWidget):

    def __init__(self,userdata, receiver="", parent=None):
        """
        @param userdat - dict - the main user data
        @param reciever - string - optional auto fill email address of reciever
        """
        QtGui.QWidget.__init__(self,parent)
        self.USERDATA = userdata
        mylayout = QtGui.QVBoxLayout()
        self.setGeometry(50,50,600,300)
        add = ""
        if self.USERDATA:
            add = self.USERDATA['email_address']
        self.From = TextField("From: ", add,self)
        self.To = TextField("To: ", receiver, self)
        self.Cc = TextField("CC: ", "", self)
        self.Bcc = TextField("BCC: ", "", self)
        self.Subject = TextField("Subject:","",self)
        self.Body = QtGui.QTextEdit()
        self.Send = QtGui.QPushButton("send")
        self.connect(self.Send,QtCore.SIGNAL("clicked()"),self.SendLetter)
        self.Multi = 0
        self.Attacher = AttachWidget()
        mylayout.addWidget(self.From)
        mylayout.addWidget(self.To)
        mylayout.addWidget(self.Cc)
        mylayout.addWidget(self.Bcc)
        mylayout.addWidget(self.Subject)
        mylayout.addWidget(self.Body)
        mylayout.addWidget(self.Attacher)
        mylayout.addWidget(self.Send)
        self.setStyleSheet(utils.get_stylesheet())
        self.setLayout(mylayout)

    def SendLetter(self):
        """
        send the info and attachments from the message window
        """
        self.ConstructMessage()
        recipient = self.To.getText()
        ccs = self.Cc.getText()
        bccs = self.Bcc.getText()
        emails = "{0}, {1}, {2}".format(recipient, ccs, bccs)
        sender = self.From.getText()

        letterMachine = smtplib.SMTP()
        check = 0
        try:
            letterMachine.connect(self.USERDATA['server'],'587')
            letterMachine.starttls()
            letterMachine.ehlo()
            letterMachine.login(self.USERDATA['user'],self.USERDATA['password'])
            letterMachine.sendmail(sender, emails, self.email.as_string())
            letterMachine.quit()
        except:
            check = 1
            output = "error: %s\n type %s \n location %s \n Message Not Sent"%sys.exc_info()
            QtGui.QMessageBox.warning(self,"Send Letter Error",output)
        if check==0:
            self.close()

    def ConstructMessage(self):
        """
        take the info from the message and format it and attach data
        """
        self.email = MIMEMultipart()
        sendDate = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        self.email['Date'] = sendDate
        self.email['To'] = self.To.getText()
        self.email['cc'] = self.Cc.getText()
        self.email['bcc'] = self.Bcc.getText()
        self.email['From'] = self.From.getText()
        self.email['Subject'] = self.Subject.getText()
        doc = self.Body.document()
        content = MIMEText(str(doc.toPlainText()))
        self.email.attach(content)
        for item in self.Attacher.attachments:
            self.AddAttachment(str(item))

    def AddAttachment(self, filename):
        """
        attach file to the email message
        """
        attachment = MIMEApplication(open('%s'%filename).read())
        attachment['name']=filename
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        self.email.attach(attachment)

    def ReplyTo(self, oldmessage ,bi):
        """
        Construct a new message but populate the new window with content from another message
        """
        DIVIDER1 = "\n\n\n<====================ORIGINAL MESSAGE==========================>\n"
        Heading = "From: %s\n"%oldmessage.get('from')
        Heading += "Date: %s\n"%oldmessage.get('date')
        self.Body.setText(DIVIDER1 + Heading + oldmessage.get('body')[bi][1])
        past_reciepts = oldmessage.get('to').split(',')
        if len(past_reciepts)>1:
            print "multiple recipients"
        self.To.setText(oldmessage.get('from'))
        self.Cc.setText(oldmessage.get('cc'))
        self.Bcc.setText(oldmessage.get('bcc'))
        self.From.setText(self.USERDATA['email_address'])
        self.Subject.setText("re: " + oldmessage.get('subject',''))
        self.Body.moveCursor(QtGui.QTextCursor.Start)

class TextField(QtGui.QWidget):

    def __init__(self,label,value,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setLayout(QtGui.QHBoxLayout())
        self.label = QtGui.QLabel(label,self)
        self.label.setFixedWidth(100)
        self.layout().addWidget(self.label)
        self.line = QtGui.QLineEdit(self)
        self.line.setText(value)
        self.layout().addWidget(self.line)
        self.setFixedHeight(50)

    def getText(self):
        return str(self.line.text())

    def setText(self,val):
        self.line.setText(val)

class AttachWidget(QtGui.QWidget):

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        mylayout = QtGui.QHBoxLayout()
        self.attachments = []
        self.removeButtons = []
        self.AttButton = QtGui.QPushButton("attach file",self)
        mylayout.addWidget(self.AttButton)
        mylayout.addStretch()
        self.setLayout(mylayout)
        self.connect(self.AttButton,QtCore.SIGNAL('clicked()'),self.AttachFile)

    def AttachFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(None,"Select Attachment")
        self.attachments.append(filename)
        self.removeButtons.append(QtGui.QPushButton(filename,self))
        self.layout().insertWidget(1,self.removeButtons[-1])

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    userdata, check = UserData()
    if not userdata:
        userdata = {"server":"", "user":"", "password":"", "email_address":""}
    widget = MessageEditor(userdata)
    widget.show()

    sys.exit(app.exec_())