# needs to do the following:
# 
# wait for items in a queue (ThreadCommBus)
# parse the commands given (look at old HiAnime client) (specifically the download requests)
# Make the requests
# Send them to another Queue (Download quuee)
import json, threading, time, math, os
import ThreadCommBus, configLoader, APIRequester, PrintBus, JellyfinCompatability
import pathGenerator, JellyfinCompatability


color = "\033[33m"
colorReset = "\033[00m"

class CommandProcessor:
    # init and general use functions
    def __init__(self, bus=ThreadCommBus.BUS, config=None):
        self.commandList = { # list of commands mapped to functions to be called later
            "downloadPoster" : self.downloadPoster,
            "pass": self.tick, # def pass() wasnt an option
            "downloadEpisode" : self.downloadEpisode,
            "downloadSeason" : self.downloadSeason,
            "downloadAnimeInfo" : self.downloadAnimeInfo,
            "downloadAll" : self.downloadAll,
            "genMetadata" : self.genMetadata,
            "shutdown" : self.stop
        }
        self._BUS = bus
        self.header = "(CMD PROC): "

        self.server = config["Server"]
        self.type = config["Type"]
        self.outputPath = config["Path"]
        self.fontSize = config["Fontsize"]
        self.lang = config["Language"]
        self.API = APIRequester.API(config["API"])
        self.verbose = config["Verbose"]
        self.pathMaker = compatabilityMap[config["compatability"]]()
    
    def Print(self, msg, verb = False):
        if verb and self.verbose:
            self._BUS.PrintBus.put(f"(Verboose) {color}{self.header}{msg}{colorReset}")
        elif verb == False:
            self._BUS.PrintBus.put(f"{color}{self.header}{msg}{colorReset}")
    
    def blacklistedChars(self, string):
        invalid_chars = "\'`\",." #invalid chars *generally*
        for char in invalid_chars: 
            string = string.replace(char, "") # loop thru all invalid chars and replace them with _'s in the stirng
        string.strip() # remove trailing " "'s
        string = string.replace(" ", "_")
        return string


    def numFormatter(self, num, maxNum):
        return format(num, f"0{math.floor(math.log10(maxNum)+1)}d")
    
    def getServerRollback(self, episodeID, type=None, server=None):
        # figure out which server will work (Sub can roll over to RAW, Dub cannot roll over to anything)
        if type == None:
            type=self.type
        if server == None:
            server = self.server
        epServers = self.API.getEpServers(episodeID)
        
        if not epServers["success"]:
            return
        epServers = epServers["data"]

        # check to see if there is less than 1 server (no servers)
        if len(epServers[self.type.lower()]) < 1:
            if self.type.lower() == "sub" and len(epServers["raw"]) > 0: # check to see if the type wanted is SUB and RAW has a server
                self.Print("Found now SUB servers, but found RAW servers", True)
                self.Print("Switching to RAW server (Usually SUB)", True)
                self.Print(f"{episodeID} - Failed to find a SUB server! Switching to RAW.")
                data = self.API.getEpStreaming(episodeID, server, "raw")
                if not data["success"]:
                    return
                data = data["data"]
                return data # return the RAW servers stream b/c thats better than nothing
            else:
                self.Print("Couldnt find servers for specified type!", True)
                self.Print(f"{episodeID} - Failed to find a server!")
                return "ERROR, SERVER NOT FOUND!" # couldnt find a server so tell the user
        else:
            data = self.API.getEpStreaming(episodeID, server, type)
            if not data["success"]:
                return
            data = data["data"]
            return data # return the servers stream that was asked for
        
    def getConfigOverrides(self, data):
        # get any config overrides
        if list(data.keys()).__contains__("type"):
            type = data["type"] # sub/dub
        else:
            type=self.type
        if list(data.keys()).__contains__("server"):
            server = data["server"] # hd-1
        else:
            server=self.server
        if list(data.keys()).__contains__("fontsize"):
            fontSize = data["fontsize"] # 24
        else:
            fontSize=self.fontSize
        if list(data.keys()).__contains__("language"):
            lang = data["language"] # English
        else:
            lang=self.lang
        if list(data.keys()).__contains__("path"):
            path = data["path"] # default path
        else:
            path=self.outputPath
        if list(data.keys()).__contains__("burn"):
            burn = data["burn"]
        else:
            burn = False
        return [type, server, fontSize, lang, path, burn]


    def createDownloadVideoMessage(self, path, video, filename, category, captions=None, font=None, burn=None):
        msg = { "Type" : "Video", "Path" : path}
        msg["video"] = video
        msg["category"] = category
        msg["filename"] = self.blacklistedChars(filename)
        if captions != None:
            msg["captions"] = captions
        if font != None:
            msg["font"] = font
        if burn != None:
            msg["burn"] = burn
        return msg

    def getCaptions(self, tracks, Lang=None):
        default = None
        if Lang == None:
            Lang = self.lang # make sure we have the specified language
        for track in tracks: # loop through all subtitle tracks
            if track["kind"] != "captions":
                continue
            if list(track.keys()).__contains__("default"):
                if track["default"]:
                    default = track
            if track["label"].lower() == Lang.lower(): # find the track that matches the language
                return track # return it
        self.Print("Couldnt find requested Captions!", True)
        if default != None:
            self.Print(f"Defaulting to the \"default\" captions ({default["label"]})")
        else:
            self.Print("Didnt find any applicable captions!")
        return default


    # threading functions
    def startThread(self, id):
        self.thread = threading.Thread(target=self.commandParser) # set the thread to start in the commandParser (infinate loop)
        self.threadID = id # save the id I guess 
        self.header = f"Thread({id}) {self.header}" # update the header

        self.Print("Starting thread")
        self.thread.start() # start the thread 
        return self.thread
        
    def stopThread(self):
        if self._BUS.killBus.empty():
            self._BUS.killBus.put(1)
        
        self.Print("Stopping thread (after its done)")

        self.Print("Sending stop in the Queue", True)
        self._BUS.servChannel.put({"cmd": "pass"})

        self.Print("Waiting for thread to finish", True)
        self.thread.join()
        self.header = "(CMD PROC): "
        self.Print("Thread closed")

    # Command Functions
    def commandParser(self):
        while self._BUS.killBus.empty(): # want this to run until a command is found (or disabled)
            
                self.Print("waiting for command", True)
                data = self._BUS.servChannel.get() # waits for a command to appear in the queue
                if data:
                    self.Print("Found command", True)
                    command = data["cmd"] # pulls the command from the request
                    if list(self.commandList.keys()).__contains__(command):
                        self.commandList[command](data) # sends the command to the function (based on the "cmd" arg)
                    else:
                        self.Print(f"Invalid command sent! \"{command}\"")
            
    def tick(self, data):
        self.Print("Passing", True) # pass command for breaking out of the loop
        return
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Tells the server to shutdown via the kill bus #
    # # # # # # # # # # # # # # # # # # # # # # # # #
    def stop(self, data):
        self.Print("Recieved message to shutdown")
        self._BUS.killBus.put(1)
        self.Print("Killcode sent!", True)
        return


    def downloadVideo(self, data, episode, episodes, animeData):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)

        animeName = animeData["anime"]["info"]["name"]
        path = self.pathMaker.generatePath(path, animeData)

        self.Print(f"Queueing download for {episode["title"]} (Episode {episode["number"]})")

        # get the streaming links (pass if its borked) and isolate the streaming link
        episodeStreaming = self.getServerRollback(episode["episodeId"], type=category, server=server)
        if type(episodeStreaming) != dict:
            return
        video = episodeStreaming["sources"][0]["url"]
        self.Print(f"Found streaming links", True)

        # parse the filename
        fileName = self.pathMaker.epNameParser(episode, animeData, category, len(episodes))
        self.Print(f"Parsed the episode title ({fileName})", True)

        if category == "dub": 
            # we dont need captions if the video is DUB'd
            msg = self.createDownloadVideoMessage(path, video, fileName, category)
        else:
            # find the captions specified and create the message
            captions = []
            if burn:
                captions = [self.getCaptions(episodeStreaming["tracks"], lang)]
            else:
                for track in episodeStreaming["tracks"]:
                    self.Print(f"Caption data {track}", True)
                    if track["kind"] == "captions":
                        data = {"file" : track["file"], "label" : track["label"]}
                        captions.append(data)
            if captions == None:
                self.Print("No captions found!")
                self.Print("Downloading video without captions")
                msg = self.createDownloadVideoMessage(path, video, fileName, category)
            else:
                msg = self.createDownloadVideoMessage(path, video, fileName, category, captions, fontSize, burn=burn)
        
        self.Print("Sending message to the download bus", True)
        # send the message to the download channel
        self._BUS.downChannel.put(msg)
        self.Print(f"Finished queueing {episode["title"]} (Episode {episode["number"]})")

    def downloadPoster(self, data):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)
        
        animeId = data["animeId"]
        # parse and fetch the animeId's info
        self.Print(f"Downloading poster for {animeId}")
        self.Print(f"Fetching {animeId}'s info", True)
        # gets the anime info
        animeData = self.API.getAnimeInfo(animeId) 
        if not animeData["success"]:
            return
        animeData = animeData["data"]

        animeName = animeData["anime"]["info"]["name"]
        # pulls the poster URL from the JSON
        poster = animeData["anime"]["info"]["poster"] 
        path = self.pathMaker.generatePath(path, animeData)

        self.Print(f"{animeId}'s info fetched", True)
        self.Print(f"Poster found at {poster}", True)

        fileName = self.pathMaker.getPosterName(animeName, poster)
        self.Print("Adding download task", True)
        # create the download message
        msg = { "Type" : "Image", "Path": path, "url" : poster, "filename": fileName}

        self._BUS.downChannel.put(msg)

    def downloadEpisode(self, data):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)

        # cache the animeID from the data
        animeId = data["animeId"] 
        # get the episodes from the anime
        episodes = self.API.getAnimeEps(animeId)
        if not episodes["success"]:
            return  
        episodes = episodes["data"]
        #parse through the episodes and get the ep requested
        episodes = episodes["episodes"]
        episode = episodes[data["episodeNumber"]-1]

        # get anime info and parse the name
        animeInfo = self.API.getAnimeInfo(animeId)
        if not animeInfo["success"]:
            return
        animeInfo = animeInfo["data"]

        animeName = animeInfo["anime"]["info"]["name"]
        self.Print(f"Queueing downloading {animeName}, Episode {episode["title"]} (Episode {episode["number"]})")
        
        self.downloadVideo(data, episode, episodes, animeInfo)
        
    def downloadSeason(self, data):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)

        # Get the anime name and info
        animeId = data["animeId"]

        animeInfo = self.API.getAnimeInfo(animeId)
        if not animeInfo["success"]:
            return
        animeInfo = animeInfo["data"]

        animeName = animeInfo["anime"]["info"]["name"]
        self.Print(f"Queueing downloading {animeName}")
        # get the anime episodes and start creating download tasks
        episodes = self.API.getAnimeEps(animeId)
        if not episodes["success"]:
            return
        episodes = episodes["data"]
        
        episodes = episodes["episodes"]
        for episode in episodes:
            self.downloadVideo(data, episode, episodes, animeInfo)
            
    def parseInfo(self, animeData, episodes):
        animeInfo = animeData["anime"]
        animeId = animeInfo["info"]["id"]
        lines = []

        lines.append(f"Anime Name : {animeInfo["info"]["name"]}")
        lines.append(f"Anime Description : ")
        lines.append(f"{animeInfo["info"]["description"]}")
        lines.append("")
        
        # Rating data
        lines.append(f"Rating : {animeInfo["info"]["stats"]["rating"]}")
        lines.append("")

        # Genre data
        lines.append("Genres :")
        # loop through all listed genres and add them
        for genre in animeInfo["moreInfo"]["genres"]:
            lines.append(f"\t{genre}")
        lines.append("")

        if len(animeData["seasons"]) > 0:
            for season in animeData["seasons"]:
                if season["isCurrent"]:
                    lines.append(f"Current Season: {season["title"]}")

        # Episode data
        lines.append(f"Episode Count : {len(episodes)}")
        lines.append("Episode Titles :")
        # loop through all episodes, and add their name (title)
        for episode in episodes:
            if episode["isFiller"]:
                lines.append(f"\t{self.numFormatter(episode["number"], len(episodes))} - {episode["title"]} | (FILLER)")
            else:
                lines.append(f"\t{self.numFormatter(episode["number"], len(episodes))} - {episode["title"]}")
        lines.append("")

        # Season data
        # check to see if there are related seasons (linked anyway)
        if len(animeData["seasons"]) > 0:
            # add the header
            lines.append("Related Seasons :")

            # loop though all seasons and add them
            for season in animeData["seasons"]:
                # if the selected season is the current season, pass (b/c we dont want it)
                if season["isCurrent"]:
                    continue
                lines.append(f"\t{season["name"]}")
        lines.append("")

        # producer & studio data

        # does this data exist for this show (does it get scraped?)
        if list(animeInfo["moreInfo"].keys()).__contains__("studios"): 
            # if it does append the studio header
            lines.append(f"Studio : ")

            # check to see if its a list
            if type(animeInfo["moreInfo"]["studios"]) == list: 

                # if its a list, loop through all values and add them
                for studio in animeInfo["moreInfo"]["studios"]:
                    lines.append(f"\t{studio}")
            else:
                # if it isnt a list, its probably a string, so add it
                lines.append(f"\t{animeInfo["moreInfo"]["studios"]}")
        
        # does this data exist for this show (does it get scraped?)
        if list(animeInfo["moreInfo"].keys()).__contains__("producers"):
            # if it does append the producers header
            lines.append(f"Producers : ") 

            # check to see if its a list
            if type(animeInfo["moreInfo"]["producers"]) == list:

                # if its a list, loop through all values and add them
                for producer in animeInfo["moreInfo"]["producers"]:
                    lines.append(f"\t{producer}")
            else:
                # if it isnt a list, its probably a string, so add it
                lines.append(f"\t{animeInfo["moreInfo"]["producers"]}")
        lines.append("")
        
        # Add the technical details (IDs)
        lines.append(f"Anime ID : {animeId}")
        lines.append("")

        lines.append("Episode IDs : ")
        # loop through all episodes
        for episode in episodes:
            #check to see if its filler & add line
            if episode["isFiller"]:
                lines.append(f"\t{self.numFormatter(episode["number"], len(episodes))} - {episode["episodeId"]} | (FILLER)")
            else:
                lines.append(f"\t{self.numFormatter(episode["number"], len(episodes))} - {episode["episodeId"]}")
        lines.append("")

        # check to see if there are related seasons (linked anyway)
        if len(animeData["seasons"]) > 0:
            # add the header
            lines.append("Related Season IDs :")

            # loop though all seasons and add them
            for season in animeData["seasons"]:
                # if the selected season is the current season, pass (b/c we dont want it)
                if season["isCurrent"]:
                    continue
                lines.append(f"\t{season["id"]}")
        lines.append("")

        return lines

    def downloadAnimeInfo(self, data):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)
        
        # Get the anime name and info
        animeId = data["animeId"]
        animeData = self.API.getAnimeInfo(animeId)
        if not animeData["success"]:
            return
        animeData = animeData["data"]

        # get the anime episodes (for the names)
        episodes = self.API.getAnimeEps(animeId)
        if not episodes["success"]:
            return
        episodes = episodes["data"]
        episodes = episodes["episodes"]

        lines = self.parseInfo(animeData, episodes)
        
        # parse the filename
        fileName = self.pathMaker.getDescriptionName(animeData)
        
        # parse the request
        msg = {"Type" : "Description", "Path" : self.pathMaker.generatePath(path, animeData)}
        msg["text"] = lines
        msg["filename"] = fileName
        # send the download request to the queue
        self._BUS.downChannel.put(msg)

    def downloadAll(self, data):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)

        self.Print("Fetching anime Info and episodes", True)
        # Get the anime name and info
        animeId = data["animeId"]
        self.Print(f"Fetching Anime info", True)
        animeData = self.API.getAnimeInfo(animeId)
        if not animeData["success"]:
            return
        animeData = animeData["data"]

        animeInfo = animeData["anime"]
        animeName = animeInfo["info"]["name"]
        self.Print(f"Queueing downloading {animeName}")
        # get the anime episodes and start creating download tasks
        self.Print(f"Fetching Anime episodes", True)
        episodes = self.API.getAnimeEps(animeId)
        if not episodes["success"]:
            return
        episodes = episodes["data"]

        episodes = episodes["episodes"]
        self.Print(f"Downloading EVERYTHING related to {animeName}", True)

        # poster section
        self.Print(f"Queueing {animeName}'s poster")

        # pulls the poster URL from the JSON
        poster = animeData["anime"]["info"]["poster"] 
        postrFileName = self.pathMaker.getPosterName(animeData, poster)

        # create the Poster download request
        self.Print(f"Parsing queue request", True)
        postrMsg = { "Type" : "Image", "Path": self.pathMaker.generatePath(path, animeData), "url" : poster, "filename" : postrFileName}
        self._BUS.downChannel.put(postrMsg)
        self.Print(f"Finished queueing {animeName}'s poster")

        # Info parser section
        self.Print(f"Queueing {animeName}'s Info (description)")
        lines = self.parseInfo(animeData, episodes)
        descFileName = self.pathMaker.getDescriptionName(animeData)

        # parse the request
        descMsg = {"Type" : "Description", "Path" : self.pathMaker.generatePath(path, animeData)}
        descMsg["text"] = lines
        descMsg["filename"] = descFileName

        # send the download request to the queue
        self._BUS.downChannel.put(descMsg)

        # generate the metadata
        self.Print(f"Downloading the metadata for {animeName} using {self.pathMaker.name} compatability", True)
        self.pathMaker.getMetadata(path, animeData, self._BUS)

        # download any extra information that the compatability script requires
        self.Print(f"Downloading extra information for {animeName} using {self.pathMaker.name} compatability", True)
        self.pathMaker.downloadExtra(path, animeData, self._BUS)
        
        # Video download section
        self.Print(f"Queueing {animeName}'s Episodes")
        for episode in episodes:
            self.downloadVideo(data, episode, episodes, animeData)


    #
    # Generates all the metadata that the current compatability selection needs
    # used for if the user has downloaded shows and needs the metadata (like I do...)
    #
    def genMetadata(self, data):
        # get the config overrides
        category, server, fontSize, lang, path, burn = self.getConfigOverrides(data)
        
        self.Print("Generating the anime metadata", True)
        
        # Get the anime name and info
        animeId = data["animeId"]
        self.Print(f"Fetching Anime info", True)
        animeData = self.API.getAnimeInfo(animeId)
        if not animeData["success"]:
            return
        animeData = animeData["data"]

        # generate the metadata
        self.pathMaker.getMetadata(path, animeData, self._BUS)


#
# Have to put this down here
# the joys of interperted languages :D
#
compatabilityMap = {#
    "default" : pathGenerator.defaultPathCreator,
    "jellyfin" : JellyfinCompatability.JellyFinPathCreator
}



_BUS = ThreadCommBus.BUS()
def testing():
    print("Starting")
    cmdProc = CommandProcessor(_BUS)
    printbus = PrintBus.PrintBus(_BUS)
    printbus.startPrintBus(1)

    cmdProc.startThread(2)
    # print("waiting for 3 secs")
    time.sleep(3)
    # print("Pushing command")
    _BUS.servChannel.put({"cmd": "downloadPoster", "animeId" : "jujutsu-kaisen-tv-534"})
    # print("waiting 3 secs")
    time.sleep(3)
    # print("shutting down the server")
    cmdProc.stopThread()
    time.sleep(1)
    # print("shutting down the print thread")
    printbus.stopPrintThread()
    time.sleep(1)
    while not _BUS.downChannel.empty():
        print(json.dumps(_BUS.downChannel.get(), indent=4))
   

#
# welcome to a 600 line monalith :D
# I need to refactor this dont I ....
#