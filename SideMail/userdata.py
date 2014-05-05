#!/usr/bin/env python
from PyQt4 import QtGui,QtCore
import sys,os, json
import logging

class UserLoader(QtGui.QDialog):

    def __init__(self,parent=None,server=None,user=None,password=None,email_address=None,f=QtCore.Qt.WA_DeleteOnClose):

        QtGui.QDialog.__init__(self,parent)
        self.setWindowTitle("Get Login Info")
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel("Server(imap.gmail.com): ",self),0,0)
        self.iServer = QtGui.QLineEdit(self)
        if server:
            self.iServer.setText(server)
        layout.addWidget(self.iServer,0,1)
        layout.addWidget(QtGui.QLabel("User: ",self),1,0)
        self.iLogin = QtGui.QLineEdit(self)
        if user: self.iLogin.setText(user)

        layout.addWidget(self.iLogin,1,1)
        layout.addWidget(QtGui.QLabel("Email Address: ",self),3,0)
        self.iAddress = QtGui.QLineEdit(self)
        layout.addWidget(self.iAddress,3,1)

        if email_address: self.iAddress.setText(email_address)

        layout.addWidget(QtGui.QLabel("Password: ",self),2,0)
        self.iPassword = QtGui.QLineEdit(self)
        self.iPassword.setEchoMode(QtGui.QLineEdit.Password)

        if password: self.iPassword.setText(password)

        layout.addWidget(self.iPassword,2,1)
        self.Check = QtGui.QPushButton("Check Mail",self)
        layout.addWidget(self.Check,4,0)

        self.connect(self.Check,QtCore.SIGNAL("clicked()"),self.Complete)
        self.setLayout(layout)

    def getText(self):
        self.setModal(True)
        retcode = self.exec_()
        return {'server':str(self.iServer.text()),
				'user':str(self.iLogin.text()),
				'email_address':str(self.iAddress.text()),
				'password':str(self.iPassword.text())},retcode

    def Complete(self):
        if not self.iServer.text() == "":
            self.done(0)
        else:
            QtGui.QMessageBox.warning(self,
                                      "Ooops!",
                                      "You need to at least set a servername",
                                      QtGui.QMessageBox.Ok)

    def closeEvent(self,e):
        self.done(1)

def GetUserData():
    path = os.path.expanduser("~")
    fname = os.path.join(path,'.imapqt')
    try:
        data = ReadUser(fname)
        return data
    except:
        print "couldn't get user data"
        UserData()

def UserData(parent=None):
    """
    read or write the userdata to a file
    and load to input window
    @param: parent - None
    """
    path = os.path.expanduser("~")
    fname = os.path.join(path,'.imapqt')
    try:
        data = ReadUser(fname)
    except:
        data = {}
    text,ret = UserLoader.getText(UserLoader(**data))
    if ret == 0:
        try:
            WriteUser(fname,text)
        except:
            print "could not write file"
        return text,ret

def UserContacts(do, ddict={}):
    """
    @param: do - string - read or write
    @param: ddict - dict - the data dict {"contacts":[]}
    """
    path = os.path.expanduser("~")
    fname = os.path.join(path,'.imapqtcontacts')

    if do =="read":
        data = {"contacts":[]}
        try:
            data = ReadUser(fname)
        except:
            data = {"contacts":[]}
        return data
    if do == "write":
        try:
            WriteUser(fname,ddict)
        except:
            print "could not write file"


def ReadUser(fname):
    """
    open and read in user data as json dict
    @param: fname - string, filename
    """
    with open(fname, 'r') as jf:
        jData = json.load(jf)
    return jData

def WriteUser(fname, ddict):
    """
    @param: fname - string, filename
    @param: ddict - dict, userdata
    """
    with open(fname, 'w') as jf:
        jf.write(json.dumps(ddict))
    return 0

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    UserData()
    sys.exit(app.exec_())
