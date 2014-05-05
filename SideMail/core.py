'''
Created on May 3, 2014

@author: Matt
@summary: This module holds all the core functions and classes for sidemail
'''

import imp,os,sys
import imaplib
import email
import re
import userdata
import utils

import logging

#==============================================================================#
# PLUGIN CONTENT
#==============================================================================#

class PluginLoader():
    """
    This class handles loading of any external plugins that would extend
    the functionality of the core application
    """
    
    def __init__(self):
        """
        init the class
        """
        fileroot = os.path.dirname(os.path.abspath(__file__))
        logging.info(fileroot)
        self.pluginsFolder = os.path.join(os.path.join(fileroot, '..'), 'plugins')
        self.mainModule = "__init__"
        self.loadedPlugins = []
        
        #load current plugins
        self.plugins = self.get_plugins()
        self.launch_plugins()
        
    def get_plugins(self):
        """
        @param None: none
        @return: a list of possible plugins to load
        """
        self.plugins = []
        possiblePlugins = os.listdir(self.pluginsFolder)
        
        #search through plugins folders looking for hopefuls
        for p in possiblePlugins:
            location = os.path.join(self.pluginsFolder, p)
            if not os.path.isdir(location) or not "{0}.py".format(self.mainModule) in os.listdir(location):
                continue
            info = imp.find_module(self.mainModule, [location])
            self.plugins.append({"name": p, "info": info})
            
        return self.plugins
    
    def launch_plugins(self):
        """
        find all plugins and load them
        
        """
        for p in self.plugins:
            logging.info("loading plugin {0}".format(p["name"]))
            plug = self.load_plugin(p)
            self.loadedPlugins.append(plug)
            plug.run()
    
    def test_command(self, command):
        """
        test running a command in loaded plugins
        """
        logging.info("sent command: {0} to all loaded plugins".format(command))
        for p in self.loadedPlugins:
            #test running command for each plugin
            if command in p.commands.keys():
                p.commands[command]()
    
    def load_plugin(self, plug):
        """
        load the plugin
        
        @param plug: the name of the plugin to load
        @type plug: object | {name: name, info:info}
        """
        return imp.load_module(self.mainModule, *plug["info"])
            



#==============================================================================#
# CORE EMAIL/IMAP CONTENT
#==============================================================================#

class ImapReader():

    def __init__(self, userdata):
        logging.info("user is: {0} and pass is: {1} server is {2}".format(userdata['user'],
                                                                          userdata['password'],
                                                                          userdata['server']))
        self.M = imaplib.IMAP4_SSL(host=userdata['server'])
        self.M.login(userdata['user'], userdata['password'])
        ret,self.boxes = self.M.lsub()
        self.MessDict = {}
        self.MBOX = ""

    def SelectBox(self, mname):
        self.M.select(mname)
        self.MBOX = mname

    def GetMessages(self):
        ret_dict = {}
        typ, data = self.M.search(None, 'ALL')
        for num in data[0].split():
            typ, data = self.M.fetch(num, '(RFC822)')
            ret_dict[num]=ParseMail(data[0][1])
        return ret_dict

    def EndSession(self):
        self.M.close()
        self.M.logout()

    def DeleteMessage(self, num):
        print "deleting number %s from mailbox %s"%(num,self.MBOX)
        self.M.copy((num),'Deleted')
        ok, error = self.M.store(num, 'FLAGS', '(\Deleted)')
        self.M.expunge()

    def MoveMessage(self, num, newbox):
        print "moving number %s to mailbox %s"%(num,newbox)
        self.M.copy((num),newbox)
        ok, error = self.M.store(num, 'FLAGS', '(\Deleted)')
        self.M.expunge()
        print ok

    def BuildContactList(self, udata):
        """
        check to see if the local file has been created for contacts
        if not then read the messages from the users mails and parse the recieved addresses
        compile a list of all the addresses and use that as the base contacts list
        """

        c = userdata.UserContacts("read")
        if len(c["contacts"]) > 0:
            return c

        email_list=[]

        print self.M.list()
        #folders: [Gmail]/Trash, [Gmail]/Starred, [Gmail]/Spam, [Gmail]/Sent Mail, [Gmail]/Important, [Gmail]/Drafts
        #[Gmail]/All Mail, [Gmail], INBOX
        s = self.M.select('[Gmail]/All Mail') #sent

        result, data = self.M.uid('SEARCH', None, 'ALL')
        ids = data[0]
        id_list = ids.split()
        for i in id_list:
            typ, data = self.M.fetch(i,'(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    sender = msg['from'].split()[-1]
                    address = re.sub(r'[<>]','',sender)
                    # Ignore any occurences of own email address and add to list
                    if not re.search(r'' + re.escape(udata['user']),address) and not address in email_list:
                        email_list.append(address)
                        print address

        #save the email-list to the user contact data
        print "Contacts Downloaded!"
        c = {"contacts": email_list}
        udata.UserContacts("write",c)
        return c


    
def ParseMail(stringMess):
    """
    This ain't pretty, I will migrate all imap/email routines to another file and then have that d/load and clean up the imap directory of my internet account.  Then all of my emails on this computer will be stored in sqlite databases. To change where I get my email from I will just have to change the message center.
     Hopefully this data model will be consistent.  
    This function will recieve a message and return a one element dictionary
    {subject:subject,to:To,from:sender,date:date,body:main content,attachments:[(filename,type,Data)]
    """
    BODY_MIME = ['text/html','text/plain']
    mailmess = email.message_from_string(stringMess)
    mess_dict = {'subject':mailmess.get('subject'),
            'to':mailmess.get('To'),
            'from':mailmess.get('From'),
            'date':mailmess.get('Date')}
    attachments = []
    bodies =[]
    utils.GetPayloads(bodies,attachments,mailmess)
    mess_dict['body'] = bodies
    mess_dict['attachments']=attachments
    return mess_dict


    
    
    
#==============================================================================#
# OTHER CONTENT
#==============================================================================#
    
