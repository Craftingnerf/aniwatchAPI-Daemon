import ServerThread, CommandThread, DownloadThread, ThreadCommBus, PrintBus, configLoader
import json, sys, os

defaultConfig = {
    "API": "None",
    "Path": "C:\\HiAnimeDaemon",
    "compatability" : "default",
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

if not list(config.keys()).__contains__("compatability"):
    print("(MAIN) : Adding compatability to config")
    config["compatability"] = defaultConfig["compatability"]
    configLoader.StoreConfig(defaultConfig, "HiAnimeDaemon.conf")


verbose = config["Verbose"]
printBus = PrintBus.PrintBus(_BUS, verbose)
server = ServerThread.CommandServer(_BUS, verbose)
commands = CommandThread.CommandProcessor(_BUS, config)
downloads = DownloadThread.DownloadManager(_BUS, verbose)

usingLogFile = False
logFile = None
try:
    # check to see if there is any arguements
    # beyond the starting arg of main.py
    if len(sys.argv) > 1:
        print("(MAIN) : Attempting to add a logfile, based on arguments")
        args = sys.argv[1:]
        import datetime
        # we only want one output file
        # narrow down which argument is a file
        for obj in args:
            if not os.path.isdir(obj):
                print("(MAIN) : File location found!\n(MAIN) : Creating a file!")
                date = datetime.datetime.now()
                old_stdout = sys.stdout
                # set the file argument to the log file
                logFile = open(obj, "w")
                usingLogFile = True
                sys.stdout = logFile

except Exception as e:
    print(f"Encountered an error:\n{e}\nMay not be an issue if no args were passed to the script")
    pass

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
        
    # close the log file
    if usingLogFile and logFile != None:
        logFile.close()
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

    # close the log file
    if usingLogFile and logFile != None:
        logFile.close()
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

    # close the log file
    if usingLogFile and logFile != None:
        logFile.close()
    # exit the program cleanly
    exit()