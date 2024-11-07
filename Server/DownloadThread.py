import threading, os, time
import FileCreator, ThreadCommBus, configLoader
from collections import deque

# Structure for download jobs
# {
#     "Type" : (string) -- (Image, Video, Description) 
#     "Path" : (string) -- absolute filepath for the output (doesnt include filename)
#     "filename": (string)
#     // for images
#     "url" : (string)
#
#     // description
#     "text": (list of strings)
#
#     // video
#     "video" : "url",
#     "category": (sub/dub)
#     // the following need sub
#     "captions" : ["url1", "url2"],
#     "font" : <fontsize> (number)
#     "burn" : false (optional TRUE) -- burns in the first URL in the captions list
# }

color = "\033[34m"
colorReset = "\033[00m"

class DownloadManager:
    def __init__(self, bus, vb = False):
        self._BUS = bus
        self.headerA = "(DOWNLOAD MGR): "
        self.headerB = "(DOWNLOADER): "
        self.verboose = vb
        self.miscDeque = deque()
        self.videoDeque = deque()
        self.loadDeques()
        FileCreator.verboose = vb
        FileCreator._BUS = bus
        
    def Print(self, msg, id = False, verb = False):
        if not id:
            header = self.headerA
        else:
            header = self.headerB
        if verb and self.verboose:
            self._BUS.PrintBus.put(f"(Verboose) {color}{header}{msg}{colorReset}")
        elif verb == False:
            self._BUS.PrintBus.put(f"{color}{header}{msg}{colorReset}")

    # threading functions
    def startThreads(self, idA, idB):
        self.threadA = threading.Thread(target=self.downloadMgr) # set the thread to start in the downloadMgr (infinate loop)
        self.headerA = f"Thread({idA}) {self.headerA}" # update the header

        self.threadB = threading.Thread(target=self.downloader) # set the thread to start in the downloadMgr (infinate loop)
        self.headerB = f"Thread({idB}) {self.headerB}" # update the header

        self.Print("Starting threads")
        self.threadA.start() # start the thread 
        self.threadB.start()
        return self.threadA, self.threadB
        
    def stopThreads(self):
        if self._BUS.killBus.empty():
            self._BUS.killBus.put(1)
        self.Print("Stopping thread (after its done)")

        self.Print("Sending stop in the Queue", True)
        self._BUS.downChannel.put({"cmd": "pass"})

        self.Print("Waiting for thread to finish", True)
        self.threadA.join()
        self.headerA = "(DOWNLOAD MGR): "
        self.Print("Thread closed")
        self.threadB.join()
        self.headerB = "(DOWNLOADER): "
        self.Print("Thread closed", True)

    # caching functions
    def saveDeque(self):
        commands = []
        for item in self.miscDeque:
            commands.append(item)
        for item in self.videoDeque:
            commands.append(item)
        cmdTable = {}
        cmdTable["cmd"] = commands
        configLoader.StoreConfig(cmdTable, "Commands.file")
    
    def loadDeques(self):
        if not configLoader.doesConfigExist("Commands.file"):
            return
        commands = configLoader.LoadConfig("Commands.file")
        commands = commands["cmd"]
        for item in commands:
            if item["Type"].lower() == "video":
                self.videoDeque.append(item)
            elif item["Type"].lower() == "image" or item["Type"].lower() == "description":
                self.miscDeque.append(item)

    # download functions
    def downloadMgr(self):
        while self._BUS.killBus.empty():
            cmd = self._BUS.downChannel.get()
            if not list(cmd.keys()).__contains__("Type"):
                continue
            if cmd["Type"].lower() == "video":
                self.videoDeque.append(cmd)
            elif cmd["Type"].lower() == "image":
                self.miscDeque.append(cmd)
            elif cmd["Type"].lower() == "description":
                self.miscDeque.append(cmd)
            else:
                self.Print("Invalid command type!")
            self.saveDeque()

    def downloader(self):
        while self._BUS.killBus.empty():
            if len(self.miscDeque) > 0 or len(self.videoDeque) > 0:
                # start parsing download commands
                cmd = None
                misc = False
                if cmd == None and len(self.miscDeque) > 0:
                    cmd = self.miscDeque[0]
                    misc = True
                elif cmd == None and len(self.videoDeque) > 0:
                    cmd = self.videoDeque[0]
                if cmd["Type"].lower() == "video":
                    # command is for a video type
                    self.videoDownloadProc(cmd)
                elif cmd["Type"].lower() == "image":
                    # command is for a image type
                    self.Print(f"Downloading poster {cmd["filename"]}", True, True)
                    FileCreator.downloadPoster(cmd["Path"], cmd["url"], cmd["filename"])
                    self.miscDeque.popleft()
                elif cmd["Type"].lower() == "description":
                    # command is for a description type
                    self.Print(f"Downloading info {cmd["filename"]}", True, True)
                    FileCreator.createDescriptionFile(cmd["Path"], cmd["text"], cmd["filename"])
                    self.miscDeque.popleft()
                else:
                    self.Print("Invalid command type!", True)
                    if misc:
                        self.miscDeque.popleft()
                    else:
                        self.videoDeque.popleft()
                if self._BUS.killBus.empty():
                    self.saveDeque()
                self.Print("Finished downloading something", True)
                pass
            else:
                time.sleep(1)
        
    def videoDownloadProc(self, cmd):
        if list(cmd.keys()).__contains__("captions") and cmd["category"].lower() != "dub":
            self.Print(f"Downloading video {cmd["filename"]}", True, True)
            # self.Print(f"Would have downloaded video, with subtitles")
            if list(cmd.keys()).__contains__("burn"):
                if cmd["burn"]:
                    FileCreator.ffmpegGenDEP(cmd["video"], cmd["captions"][0], cmd["Path"], cmd["filename"], cmd["font"])
                else:
                    FileCreator.ffmpegGen(cmd["video"], cmd["captions"], cmd["Path"], cmd["filename"], cmd["font"])
            else:
                FileCreator.ffmpegGen(cmd["video"], cmd["captions"], cmd["Path"], cmd["filename"], cmd["font"])
            self.videoDeque.popleft()
        else:
            self.Print(f"Downloading video {cmd["filename"]}", True, True)
            # self.Print(f"Would have downloaded video, without subtitles")
            FileCreator.ffmpegGenNoCaptions(cmd["video"], cmd["Path"], cmd["filename"])
            self.videoDeque.popleft()


    def printDeque(self):
        lst = []
        for item in self.miscDeque:
            lst.append(f"{self.miscDeque.index(item)}: {item["filename"]} | {item["Type"]}")
        for item in self.videoDeque:
            lst.append(f"{self.videoDeque.index(item)}: {item["filename"]} | {item["Type"]}")
        self.Print(", ".join(lst), verb=True)