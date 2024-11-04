import os, json
_ConfigPath = os.path.dirname(os.path.abspath(__file__)) # get the current filepath, this is where I'd generally store the config

def StoreConfig(config, configName):
    conf = open(os.path.join(_ConfigPath, configName), "w") 
    json.dump(config, conf, indent=4)
    conf.close()

def LoadConfig(configName):
    conf = open(os.path.join(_ConfigPath, configName), "r")
    config = json.load(conf)
    conf.close()
    return config

def doesConfigExist(configName):
    return os.path.exists(os.path.join(_ConfigPath, configName))