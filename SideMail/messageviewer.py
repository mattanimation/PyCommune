#!/usr/bin/env python

from PyQt4 import QtGui,QtCore,QtWebKit
import sys,os
import core
import email
from messedit import MessageEditor

DEFAULT_ATTACHMENTS = "./attachements"
IMAGES = ["jpg","png","gif","jpeg","bmp"]

class emailWidget(QtGui.QWidget):
	def __init__(self,email_message,userdata, parent=None):
		"""This will break the data form of an email message into components handled by the appropriate widgets"""
		self.USERDATA = userdata
		self.email_message = email_message
		QtGui.QWidget.__init__(self,parent)
		MyLayout = QtGui.QGridLayout()
		body = email_message.get('body')[0][1]
		self.display = textViewer(body)
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
		bodies = self.email_message.get('body')
		self.body_index += 1
		if self.body_index >= len(bodies):
			self.body_index = 0
		return bodies[self.body_index][1]
		
	def SaveAll(self):
		filename = QtGui.QFileDialog.getExistingDirectory(None,
			"Save As", "%s"%(DEFAULT_ATTACHMENTS))
		for item in self.email_message.get('attachments'):
			outfile = '%s/%s'%(filename,item[0])
			i = 1
			while os.path.exists(outfile):
				postfix = outfile.split('.')
				outfile = "%s(%s).%s"%('.'.join(postfix[:-1]),i,postfix[-1])
				i += 1
			outfile = open(outfile,'wb')
			outfile.write(core.BinaryDecode(item[3],item[2]))
			outfile.close()
		
	def Reply(self):
		self.editor = MessageEditor(self.USERDATA)
		self.editor.ReplyTo(self.email_message,self.body_index)
		self.editor.show()
		
class textViewer(QtGui.QTextBrowser):
	def __init__(self,main, parent=None):
		QtGui.QTextBrowser.__init__(self,parent)
		self.setHtml(main.replace("\n","<br/>"))
		
		self.nb = QtGui.QAction(self)
		self.nb.setShortcut('Ctrl+N')
		self.addAction(self.nb)
		self.connect(self.nb, QtCore.SIGNAL('triggered()'),self.nextbody)
	
	def nextbody(self):
		content = (self.parent().sendBody()).replace('\n','<br/>')
		self.setHtml(content.encode('utf-8'))

class attachmentList(QtGui.QListWidget):

	def __init__(self,parent=None):
		QtGui.QListWidget.__init__(self,parent)
		self.connect(self,QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),self.OpenAttachment)
		self.attachments = {}
	def RefreshList(self,newatt):
		self.clear()
		self.attachments = {}
		for item in newatt:
			self.addItem(item[0])
			self.attachments[item[0]] = core.BinaryDecode(item[3],item[2])
		
	def OpenAttachment(self,listitem):
		itext = listitem.text()
		print itext
		data = self.attachments.get(str(itext))
		if str(itext.split('.')[-1]).lower() in IMAGES:
			self.DisplayImage(itext,data)
		else: 
			filename = QtGui.QFileDialog.getSaveFileName(None,
				"Save As", "%s/%s"%(DEFAULT_ATTACHMENTS,itext))
			if len(filename)>0:
				outfile = open(filename,'wb')
				outfile.write(data)
				outfile.close()
			
	def DisplayImage(self,filename,imagedata):
		self.Image = QtGui.QLabel(None)
		newPixmap = QtGui.QPixmap()
		newPixmap.loadFromData(imagedata,str(filename.split('.')[-1]).upper())
		self.Image.setPixmap(newPixmap)
		self.Image.show()
		