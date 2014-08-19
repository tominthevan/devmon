'''
Created on Aug 29, 2013

@author: tom

'''
import sys,pprint

class ConfigObject(object):
    subclasses= []
    @classmethod
    def add(cls,config,key):
        if "Type" in config[key]:
            myclass = getattr(sys.modules[cls.__module__],config[key]["Type"])
        else:
            myclass = cls        
        if cls not in ConfigObject.subclasses:
            ConfigObject.subclasses.append(cls)
        if key not in cls.instances:
            cls.instances[key]=myclass(config, key)
        return cls.instances[key]
    
    @classmethod
    def discard_instances(cls):
        cls.instances = {}


    @classmethod
    def discard_all_instances(cls):
        for myclass in ConfigObject.subclasses:
            myclass.discard_instances()
        subclasses = []
