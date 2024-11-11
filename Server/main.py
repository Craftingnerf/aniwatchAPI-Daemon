import ServerThread, CommandThread, DownloadThread, ThreadCommBus, PrintBus, configLoader
import json

defaultConfig = {
    "API": "None",
    "Path": "C:\\HiAnimeDaemon",
    "Server": "hd-1",
    "Type": "sub",
    "Language": "English",
    "Fontsize": 24,
    "Verbose": False,
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

print(json.dumps(config, indent=4))
# update config variable name from "verboose" to "verbose"
if list(config.keys()).__contains__("Verboose"):
    config["Verbose"] = config["Verboose"]
    config.pop("Verboose")
    configLoader.StoreConfig(defaultConfig, "HiAnimeDaemon.conf")



verbose = config["Verbose"]
printBus = PrintBus.PrintBus(_BUS, verbose)
server = ServerThread.CommandServer(_BUS, verbose)
commands = CommandThread.CommandProcessor(_BUS, config)
downloads = DownloadThread.DownloadManager(_BUS, verbose)


try:
    # start the threads
    printBus.startPrintBus(0)
    server.startThread(1, config["Port"])
    commands.startThread(2)
    downloads.startThreads(3,4)

    while _BUS.killBus.empty(): 
        # pass b/c the program doesnt need to shutdown
        pass

    # the program needs to shutdown due to a killcode being sent
    _BUS.PrintBus.put("(MAIN) : Killcode found!")
    _BUS.PrintBus.put("(MAIN) : Shutting down the server!")

    # stop all the threads
    downloads.stopThreads()
    commands.stopThread()
    server.shutdownServ()
    printBus.stopPrintThread()

    # do the job of the print bus (b/c its shutting down)
    while not _BUS.PrintBus.empty():
        print(_BUS.PrintBus.get())
    # exit the program cleanly
    exit()

except KeyboardInterrupt:
    # program needs to shutdown due to user CTRL+C'ing
    _BUS.PrintBus.put("(MAIN) : Keyboard interrupt intercepted!")
    _BUS.PrintBus.put("(MAIN) : Shutting down the server!")

    # stop all the threads
    downloads.stopThreads()
    commands.stopThread()
    server.shutdownServ()
    printBus.stopPrintThread()

    # do the job of the print bus (b/c its shutting down)
    while not _BUS.PrintBus.empty():
        print(_BUS.PrintBus.get())
    # exit the program cleanly
    exit()

except Exception as e:
    # the program has ran into an error
    _BUS.PrintBus.put("(MAIN) : Shutting down the server!")
    # stop all the threads
    downloads.stopThreads()
    commands.stopThread()
    server.shutdownServ()
    printBus.stopPrintThread()

    # do the job of the print bus (b/c its shutting down)
    while not _BUS.PrintBus.empty():
        print(_BUS.PrintBus.get())

    # debug information
    print(e)
    print("(MAIN): FFMPEG needs to be a path variable")
    print("(MAIN): Python libraries required :")
    print("(MAIN): \trequests")

    # exit the program cleanly
    exit()