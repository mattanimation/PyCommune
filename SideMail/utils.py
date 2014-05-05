'''
Created on May 3, 2014

@author: Matt
@summary: This Module holds all the utility functions and classes for sidemail
'''

from PyQt4 import QtGui
import ConfigParser
import os,sys, base64


#==============================================================================#
# System RELATED
#==============================================================================#
def createConfig(path):
    """
    Create a config file
    """
    config = ConfigParser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "Name", "Matt")
    config.set("Settings", "Image","derp.png")

    with open(path, "wb") as config_file:
        config.write(config_file)


def crudConfig(path):
    """
    Create, read, update, delete config
    """
    if not os.path.exists(path):
        createConfig(path)

    config = ConfigParser.ConfigParser()
    config.read(path)

    #read some values
    name = config.get("Settings", "Name")
    image = config.get("Settings", "Image")

    #change a value in the config
    config.set("Settings", "Name", "Derp")

    #delete value from config
    config.remove_option("Settings", "Image")

    #write over config file
    with open(path, "wb") as config_file:
        config.write(config_file)
        
        
def get_root_url():
    """
    return the base path to these modules
    """
    return os.path.dirname(os.path.abspath('__file__'))

def GetPayloads(body, att, mmess):
    """
    this function is going to decide if something is a payload or a list of payloads.
    It will call itself recursively and it will modify body and att in place.
    """
    cpay = mmess.get_payload()
    if type(cpay) is list:
        for item in cpay:
            GetPayloads(body, att, item)
    else:
        tencode = mmess.get('Content-Transfer-Encoding','printed-quotable')
        params = dict(mmess.get_params([('text/plain','')]))
        mtype = mmess.get_content_type()
        if params.has_key('name'):
            att.append((params.get('name'),mtype,cpay,tencode))
        else:
            body.append((mtype,UCode(cpay,params.get('charset','utf-8'))))

def UCode(mystring, mycode):
    try:
        ret_string = unicode(mystring,mycode,'ignore')
    except:
        print 'user encoding failed'
        ret_string = unicode(mystring,'utf-8','ignore')
    return ret_string

def BinaryDecode(enc, data):
    """
    This is mainly going to run the base64.dencodestring() routine, but I am writing it here
    so that I don't have to deal with it there.  And so that all of my email routines are right here
    """
    if enc=='base64':
        try:
            return base64.decodestring(data)
        except:
            return u"file is not base64, claims to be:%s\n%s"%(enc,data)
    else:
        return data
        
#==============================================================================#
# UI RELATED
#==============================================================================#
def get_stylesheet():
    """
    Load the stylesheet for the application
    
    @return dat: the contents of the stylesheet
    """
    f=open(os.path.join(get_root_url(),'SideMail\\Resources\\sidemail.stylesheet'), 'r')
    dat = f.read()
    f.close()
    return dat

def get_resources_path():
    """
    @return pth: the string path of the users image file
    """
    return os.path.join(get_root_url(),'SideMail/Resources')

def get_user_image_path():
    """
    @return pth: the string path of the users image file
    """
    return os.path.join(get_resources_path(),'me.png')

def generic_msg(msg, msg_type, dialog=False):
    """
    generic_msg is a helper function to alert the user to either an
    information dialog or an info dialog
    
    @type msg: str
    @param msg: The message to be displayed
    @type msg_type: str
    @param msg_type: The message type. Valid types are info, warning and error
    @type dialog: bool
    @param dialog: Display a dialog or not. Default is False
     
    """
    # set as lower case in case the type has a caps letter in it
    msg_type = str.lower(msg_type)
    if msg_type == 'error' or msg_type == 'warning':
        sys.stderr.write('%s\n' % msg)
    else:
        sys.stdout.write('%s\n' % msg)
    
    res = None
    if dialog:
        if msg_type == 'error':
            res = QtGui.QMessageBox.critical(None, 'Error', str(msg))
        elif msg_type == 'warning':
            res = QtGui.QMessageBox.warning(None, 'Warning', str(msg))
        elif msg_type == 'info':
            res = QtGui.QMessageBox.information(None, 'Information', str(msg))
        elif msg_type == 'quest':
            res = QtGui.QMessageBox.question(None, 'Question', str(msg))
    return res
