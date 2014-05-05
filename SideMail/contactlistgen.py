'''
Created on May 3, 2014

@author: Matt
'''

import os
import json

def derp():
    """
    load contact list and re-format the data
    """
    usr = os.path.expanduser("~")
    pth = os.path.join(usr, '.imapqtcontacts')
    
    f = open(pth, 'r')
    dat = json.loads(f.read())
    f.close()
    
    print dat
    
    newDat = {"contacts":[]}
    for c in dat["contacts"]:
        newDat["contacts"].append({"name": "",
                                   "email":c,
                                   "weight":0,
                                   "social":{"twitter":"",
                                             "facebook":"",
                                             "googleplus":""}
                                   })
    
    print(newDat)
    
    #save new data
    nPth = os.path.join(usr, '.sidemailcontacts')
    f = open(nPth, 'w')
    f.write(json.dumps(newDat))
    f.close()
    
    

if __name__ == '__main__':
    derp()