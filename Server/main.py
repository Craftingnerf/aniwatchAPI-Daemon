import ServerThread, CommandThread, DownloadThread, ThreadCommBus, PrintBus, configLoader
import json

defaultConfig = {
    "API": "None",
    "Path": "C:\\HiAnimeDaemon",
    "Server": "hd-1",
    "Type": "sub",
    "Language": "English",
    "Fontsize": 24,
    "Verboose": False,
    "Port" : 9909
}

_BUS = ThreadCommBus.BUS()
config = None
if configLoader.doesConfigExist("HiAnimeDaemon.conf") and config == None:
    print("found config")
    config = configLoader.LoadConfig("HiAnimeDaemon.conf")
else:
    print("didnt find config!")
    print("Creating config file")
    configLoader.StoreConfig(defaultConfig, "HiAnimeDaemon.conf")
    config = defaultConfig
    if config==None:
        exit()

# print(json.dumps(config, indent=4))

verboose = config["Verboose"]
printBus = PrintBus.PrintBus(_BUS, verboose)
server = ServerThread.CommandServer(_BUS, verboose)
commands = CommandThread.CommandProcessor(_BUS, config)
downloads = DownloadThread.DownloadManager(_BUS, verboose)

try:
    printBus.startPrintBus(0)
    server.startThread(1, config["Port"])
    commands.startThread(2)
    downloads.startThreads(3,4)
    while True: 
        pass
except KeyboardInterrupt:
    # close all threads
    _BUS.PrintBus.put("(MAIN) : Keyboard interrupt intercepted!")
    _BUS.PrintBus.put("(MAIN) : Shutting down the server!")
    downloads.stopThreads()
    commands.stopThread()
    server.shutdownServ()
    printBus.stopPrintThread()
    while not _BUS.PrintBus.empty():
        print(_BUS.PrintBus.get())
    exit()
except Exception as e:
    print(e)
    print("(MAIN): FFMPEG needs to be a path variable")
    print("(MAIN): Python libraries required :")
    print("(MAIN): \trequests")
    exit()