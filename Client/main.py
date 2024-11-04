import APIRequester, configLoader
import json, socket, sys

helplist = {
    "help" : "Prints this help message",
    "main" : "Prints the main scrape of Hianime",
    "searchAnime" : "Searches for animes",
    "searchCategories" : "Searches for animes by Category",
    "searchProducer" : "Searches for animes by Producer",
    "searchGenre" : "Searches for animes by Genre",
    "animeInfo" : "Displays information about the specifed anime",
    "animeEps" : "Displays the episode information",
    "getEpStreaming" : "Gets streaming links for a show (useful if the default captions (both config, and API) dont get the langauge you want)",
    "downloadDescription" : "Downloads the description of the anime",
    "downloadPoster" : "Downloads the anime's poster",
    "downloadEpisode" : "Downloads specified episodes",
    "downloadSeason" : "Downloads all episodes",
    "downloadAll" : "Downloads all related information (description, poster, episodes)",
    "exit" : "Closes the enviornment",
    "":"",
    "Config Overrides (Not a command)" : "Allows you to override the default config of the daemon server (works on all download commands)"
}
argList = {
    "help" : "None",
    "main" : "None",
    "searchAnime" : "Search term",
    "searchCategories" : "Search term",
    "searchProducer" : "Search term",
    "searchGenre" : "Search term",
    "animeInfo" : "anime ID",
    "animeEps" : "anime ID",
    "getEpStreaming" : "--anime (animeID) -e (EpisodeNumber) --category (sub/dub/raw)",
    "downloadDescription" : "--anime (anime ID) -p (number) (OPTIONAL) --ip (server IP)",
    "downloadPoster" : "--anime (anime ID) -p (number) (OPTIONAL) --ip (server IP)",
    "downloadEpisode" : "--anime (anime ID) -p (number) -e (episode number) (OPTIONAL) --ip (server IP)",
    "downloadSeason" : "--anime (anime ID) -p (number) (OPTIONAL) --ip (server IP)",
    "downloadAll" : "--anime (anime ID) -p (number) (OPTIONAL) --ip (server IP)",
    "exit" : "None",
    "":"",
    "Config Overrides (Not a command)" : " --path (filepath) --language (eg \"English\") --server (eg \"hd-1\") --fontsize (number) --category (sub/dub/raw)"
}
defaultConfig = {
    "Host": socket.gethostname(),
    "Port" : 9909,
    "API": "***REMOVED***"
}


config = None
if configLoader.doesConfigExist("HiAnimeClient.conf") and config == None:
    print("found config")
    config = configLoader.LoadConfig("HiAnimeClient.conf")
else:
    print("didnt find config!")
    print("Creating config file")
    configLoader.StoreConfig(defaultConfig, "HiAnimeClient.conf")
    config = defaultConfig
    if config==None:
        exit()

_API = APIRequester.API(config["API"])


def parseArgs(args):
    anime, server, port, epNum = None,None,None,None
    path, lang, serv, font, cate = None,None,None,None,None
    if args.__contains__("--anime"):
        anime = args[args.index("--anime")+1]
    else:
        print("ERROR: Anime not found (--anime)")
        return
    if args.__contains__("-p"):
        port = int(args[args.index("-p")+1])
    else:
        port = config["Port"]
    if args.__contains__("--ip"):
        server = args[args.index("--ip")+1]
    else:
        server = config["Host"]

    if args.__contains__("-e"):
        epNum = int(args[args.index("-e")+1])

    if args.__contains__("--path"):
        path = args[args.index("--path")+1]

    if args.__contains__("--language"):
        lang = args[args.index("--language")+1]

    if args.__contains__("--server"):
        serv = args[args.index("--server")+1]

    if args.__contains__("--fontsize"):
        font = args[args.index("--fontsize")+1]

    if args.__contains__("--category"):
        cate = args[args.index("--category")+1]

    return anime, server, port, epNum, path, lang, serv, font, cate

def getMaxLen(listStr, key):
    currentMax = 0
    # print(json.dumps(listStr, indent=4))
    for str in listStr:
        if len(str[key]) > currentMax:
            currentMax = len(str[key])
    return currentMax


def help(args):
    cmdMax = 0
    infoMax = 0
    argMax = 0
    for command in helplist:
        if len(command) > cmdMax:
            cmdMax = len(command)
        if len(helplist[command]) > infoMax:
            infoMax = len(helplist[command])
        if len(argList[command]) > argMax:
            argMax = len(argList[command])
    for command in helplist:
        print(f"%-{cmdMax}s | %-{infoMax}s | %-{argMax}s" % (command, helplist[command], argList[command]))

def main(args):
    data = _API.getMain()
    if not data["success"]:
        return
    data = data["data"]
    # print(json.dumps(data, indent=4))
    for key in list(data.keys()):
        print(key)
        # print(json.dumps(data[key], indent=4))
        
        # if the obj is a dictionary, we need to go a level deeper (would set this up as a funciton but...)
        if type(data[key]) == dict:
            # 2nd level keys
            for key2 in list(data[key].keys()):
                # key = new header
                print(f"\t{key2}")

                # loop through all objs in the dictionary (assuming its a list)
                for obj in data[key][key2]:
                    if type(obj) != dict:
                        # if it isnt a dictionary, just output the values
                        print(f"\t\t{obj}")
                    # if the obj is a dictionary
                    else:
                        # get the max's for the names
                        nameMax = getMaxLen(data[key][key2], "name")
                        idMax = getMaxLen(data[key][key2], "id")
                        # print it (nicely)
                        print(f"\t\t%-{nameMax}s | %-{idMax}s" % (obj["name"], obj["id"]))
        else:
            for obj in data[key]:
                if type(obj) != dict:
                    # if it isnt a dictionary, just output the values
                    print(f"\t{obj}")
                # if the obj is a dictionary
                else:
                    # get the max's for the names
                    nameMax = getMaxLen(data[key], "name")
                    idMax = getMaxLen(data[key], "id")
                    # print it (nicely)
                    print(f"\t%-{nameMax}s | %-{idMax}s" % (obj["name"], obj["id"]))
                    

def stop(args):
    exit()

def printSearch(anime):
    print(f"{anime["name"]} | {anime["id"]}")
    print(f"    Japanese name : {anime["jname"]}")
    print(f"    Type : {anime["type"]}")
    print(f"    Rating : {anime["rating"]}")
    print(f"    Episodes: ")
    print(f"        SUB: {anime["episodes"]["sub"]}")
    print(f"        DUB: {anime["episodes"]["dub"]}")
    print("")

def searchDataHandeler(data):
    for anime in data["animes"]:
        printSearch(anime)
    while data["hasNextPage"]:
        
        if data["hasNextPage"]:
            y = input("Show next page? (enter Y to continue, any other key passes)").lower()[0]
        if y == "y":
            pass
        else:
            break
        
        data = _API.searchAnime(" ".join(args), data["currentPage"]+1)
        for anime in data["animes"]:
            printSearch(anime)

def searchAnime(args):
    print(f"Searching for {" ".join(args)}...")
    data = _API.searchAnime(" ".join(args))
    
    # print(json.dumps(data, indent=4))
    if not data["success"]:
        return
    data = data["data"]

    # print(json.dumps(data, indent=4))

    searchDataHandeler(data)

def searchCat(args):
    print(f"Searching for {" ".join(args)}...")
    data = _API.getCategoryAnimes(" ".join(args))
    
    # print(json.dumps(data, indent=4))
    if not data["success"]:
        return
    data = data["data"]

    searchDataHandeler(data)

def searchProd(args):
    print(f"Searching for {" ".join(args)}...")
    data = _API.getProducerAnimes(" ".join(args))
    
    # print(json.dumps(data, indent=4))
    if not data["success"]:
        return
    data = data["data"]

    searchDataHandeler(data)

def searchGenre(args):
    print(f"Searching for {" ".join(args)}...")
    data = _API.getGenreAnimes(" ".join(args))

    # print(json.dumps(data, indent=4))
    if not data["success"]:
        return
    data = data["data"]

    searchDataHandeler(data)

    

def animeInfo(args):
    print(f"Looking up info for {args}")
    for arg in args:
        data = _API.getAnimeInfo(arg)
        if not data["success"]:
            continue
        data = data["data"]
        # print(json.dumps(data, indent=4))

        print(f"{data["anime"]["info"]["name"]} | {arg}")
        print(f"\tDescription: {data["anime"]["info"]["description"]}")
        print(f"\tRating: {data["anime"]["info"]["stats"]["rating"]}")
        print(f"\tEpisodes: ")
        print(f"\t\tSUB: {data["anime"]["info"]["stats"]["episodes"]["sub"]}")
        print(f"\t\tDUB: {data["anime"]["info"]["stats"]["episodes"]["dub"]}")
        print(f"\tAired : {data["anime"]["moreInfo"]["status"]} : {data["anime"]["moreInfo"]["premiered"]}" )
        print(f"\tGenres : ")
        for genre in data["anime"]["moreInfo"]["genres"]:
            print(f"\t\t{genre}")
        moreInfo = data["anime"]["moreInfo"]
        if list(moreInfo.keys()).__contains__("studios"):
            if type(moreInfo["studios"]) == list:
                print(f"\tStudio:")
                for studio in moreInfo["studios"]:
                    print(f"\t\t{studio}")
            else:
                print(f"\tStudio: {moreInfo["studios"]}")

        if list(moreInfo.keys()).__contains__("producers"):
            if type(moreInfo["producers"]) == list:
                print(f"\tProducers:")
                for producer in moreInfo["producers"]:
                    print(f"\t\t{producer}")
            else:
                print(f"\tProducers: {moreInfo["producers"]}")
        if list(data.keys()).__contains__("seasons") and len(data["seasons"]) > 0:
            print("\tSeasons:")
            for season in data["seasons"]:
                print(f"\t\t{season["name"]} | {season["id"]}")

def animeEps(args):
    print(f"Looking up info for {args}")
    for arg in args:
        data = _API.getAnimeEps(arg)
        if not data["success"]:
            return
        data = data["data"]
        # print(json.dumps(data, indent=4))
        for episode in data["episodes"]:
            print(f"\t{episode["title"]} | {episode["episodeId"]}")

def epStream(args):
    # get variables
    anime, server, port, epNum, path, lang, serv, font, cate = parseArgs(args)

    # make sure we have the variables needed
    if epNum == None:
        print("Cant find unknwon episode (-e)")
        return
    if cate == None:
        print("Dont have a category for the anime (--category)")
        return

    # get eps and make sure the ep is within range
    eps = _API.getAnimeEps(anime)
    if not eps["success"]:
        return
    eps = eps["data"]
    eps = eps["episodes"]
    if epNum < 1 or epNum > len(eps):
        print("Episode out of range!")
        return

    # get the streaming link for the ep, and start printing info
    episode = eps[epNum-1]
    print("\n")
    print(f"{episode["title"]} ({episode["number"]})")
    print(f"Filler?: {episode["isFiller"]}")
    streaming = _API.getEpStreaming(episode["episodeId"], category=cate)

    if not streaming["success"]:
        return
    streaming = streaming["data"]

    # print(json.dumps(streaming, indent=4))

    print("Captions: ")
    first = False
    for caption in streaming["tracks"]:
        if caption["kind"] != "captions":
            continue
        msg = f"File:\t{caption["file"]}"
        if first:
            print("-"*len(msg))
        first = True
        print(msg)
        print(f"Label:\t{caption["label"]}")
    print("")
    print(f"Intro:")
    print(f"Start:\t{streaming["intro"]["start"]}")
    print(f"End:\t{streaming["intro"]["end"]}")
    print("")
    print(f"Outro:")
    print(f"Start:\t{streaming["outro"]["start"]}")
    print(f"End:\t{streaming["outro"]["end"]}")
    print("")

    print(f"Video Links:")
    first = False
    for video in streaming["sources"]:
        msg = f"URL:\t{video["url"]}"
        if first:
            print("-"*len(msg))
        first = True
        print(msg)
        print(f"Type:\t{video["type"]}")



def sendMsgToServ(msg, port, ip=socket.gethostname()):
    print(f"sending message to : {ip}")
    # create socket and connect to the server
    client = socket.socket()
    client.connect((ip, port))
    # chop up the message into 1024 byte mesages
    byteMsg = bytes(json.dumps(msg), 'utf-8')
    msgLst = [byteMsg[i:i+1024] for i in range(0, len(byteMsg)-1, 1024)]
    for bMsg in msgLst:
        print("Sending packet of 1024B")
        print(f"Sending {bMsg}")
        client.sendall(bMsg) # send the message as bytes
    client.close()

def downDesc(args):
    anime, server, port, epNum, path, lang, serv, font, cate = parseArgs(args)
    # parse the msg
    msg = {"cmd": "downloadAnimeInfo", "animeId": anime}
    if server != None:
        sendMsgToServ(msg, port, server)
    else:
        sendMsgToServ(msg, port)

def downPoster(args):
    anime, server, port, epNum, path, lang, serv, font, cate = parseArgs(args)

    # parse the msg
    msg = {"cmd": "downloadPoster", "animeId": anime}

    if server != None:
        sendMsgToServ(msg, port, server)
    else:
        sendMsgToServ(msg, port)

def downEp(args):
    anime, server, port, epNum, path, lang, serv, font, cate = parseArgs(args)
    
    if epNum == None:
        print("Cant download unknwon episode (-e)")
        return

    # parse the msg
    msg = {"cmd": "downloadEpisode", "animeId": anime, "episodeNumber" : epNum}
    
    # get the optional config overrides
    if path != None:
        msg["path"] = path
    if lang != None:
        msg["language"] = lang
    if serv != None:
        msg["server"] = serv
    if font != None:
        msg["fontsize"] = font
    if cate != None:
        msg["type"] = cate

    if server != None:
        sendMsgToServ(msg, port, server)
    else:
        sendMsgToServ(msg, port)

def downSeason(args):
    anime, server, port, epNum, path, lang, serv, font, cate = parseArgs(args)

    # parse the msg
    msg = {"cmd": "downloadSeason", "animeId": anime}
    
    # get the optional config overrides
    if path != None:
        msg["path"] = path
    if lang != None:
        msg["language"] = lang
    if serv != None:
        msg["server"] = serv
    if font != None:
        msg["fontsize"] = font
    if cate != None:
        msg["type"] = cate

    if server != None:
        sendMsgToServ(msg, port, server)
    else:
        sendMsgToServ(msg, port)

def downAll(args):
    anime, server, port, epNum, path, lang, serv, font, cate = parseArgs(args)

    # parse the msg
    msg = {"cmd": "downloadAll", "animeId": anime}

    # get the optional config overrides
    if path != None:
        msg["path"] = path
    if lang != None:
        msg["language"] = lang
    if serv != None:
        msg["server"] = serv
    if font != None:
        msg["fontsize"] = font
    if cate != None:
        msg["type"] = cate


    if server != None:
        sendMsgToServ(msg, port, server)
    else:
        sendMsgToServ(msg, port)

commands = {
    "help" : help,
    "main" : main,
    "exit" : stop,
    "searchAnime" : searchAnime,
    "searchCategories" : searchCat,
    "searchProducer" : searchProd,
    "searchGenre" : searchGenre,
    "animeInfo" : animeInfo,
    "animeEps" : animeEps,
    "getEpStreaming":  epStream,
    "downloadDescription" : downDesc,
    "downloadPoster" : downPoster,
    "downloadEpisode" : downEp,
    "downloadSeason" : downSeason,
    "downloadAll" : downAll,
}
try:
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        args = sys.argv[2:]
        print(f"{cmd} {" ".join(args)}")
        commands[cmd](args)
        exit()
    else:
        pass
except Exception as e:
    print(e)
    pass


while True:
    try:
        cmd = input("Enter a command : ").split(" ")
        args = cmd[1:]
        cmd = cmd[0]
        commands[cmd](args)
    except Exception as e:
        print(e)
        help(args)