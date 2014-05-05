"""
@newField description: Description

@author: Matt Murray
@description: This is a demo plugin to be used as a template for creating your
                own plugins. All common functions live in this __init__.py
                file and any other modules would live in this folder/package
                but be imported here as well so all functions are abstracted
                into one funnel.
"""

import sys    
import logging
import inspect

PLUGIN_NAME ="demo"

def run():
    """
    execute the plugin
    """
    logging.info("Heey this plugin {0} loaded ".format(PLUGIN_NAME))
    

def foo():
    """
    a test function
    """
    print("another function to do something")
    
def bar():
    """
    another test function
    """
    print("bar ran")

commands = {
            "run": run,
            "foo": foo,
            "bar": bar}
    
    