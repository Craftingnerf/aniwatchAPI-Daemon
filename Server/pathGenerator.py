import math, os

class defaultPathCreator:
    def __init__(self):

        pass

    # utility functions
    # cleans the strings so they are able to be written to the filesystem
    def cleanStr(self, string):
        invalid_chars = "<>:\"/\\|?*;" #invalid chars *generally*
        for char in invalid_chars: 
            string = string.replace(char, "") # loop thru all invalid chars and replace them with _'s in the stirng
        string.strip() # remove trailing " "'s
        string = string.replace(" ", "_")
        return string
    
    # gets a string for episodes (i.e. episode 0032 of One Piece)
    def numFormatter(self, num, maxNum):
        return format(num, f"0{math.floor(math.log10(maxNum)+1)}d")

    # built in os.path.join so I dont have to import it on every compatability script
    def osPathJoin(self, itemA, itemB):
        return os.path.join(itemA, itemB)
    
    def osPathExists(self, item):
        return os.path.exists(item)

    # class type functions

    # if we want extra data (such as series posters for Jellyfin)
    def downloadExtra(self, path, animeData, _BUS):
        pass

    # generate the basic path for everything
    def generatePath(self, path, animeData):
        animeName = animeData["anime"]["info"]["name"]
        genPath = self.osPathJoin(path, self.cleanStr(animeName.replace(" ", "_"))).replace("\\","/")
        return genPath
    
    # generate the episode names (some media servers may want it formatted in a certian way)
    def epNameParser(self, epData, animeData, type, maxEps):
        animeName = animeData["anime"]["info"]["name"]
        return f"{self.numFormatter(epData["number"], maxEps)}-{self.cleanStr(epData["title"].replace(" ", "_"))}-{self.cleanStr(animeName.replace(" ", "_"))}-{type.upper()}"
    
    # generate the poster names (some media servers might only accept files of certian names)
    def getPosterName(self, animeData, poster):
        animeName = animeData["anime"]["info"]["name"]
        return f"#-{self.cleanStr(animeName.replace(" ", "_"))}-Poster.{poster.split(".")[-1]}"
    
    # generate the description and overall info filename (see comment bracket of self.getPosterName)
    def getDescriptionName(self, animeData):
        return f"$-{self.cleanStr(animeData["anime"]["info"]["name"].replace(" ", "_"))}-Info.txt"
    
    def getMetadata(self, path, animeData, _BUS):
        pass

    def genEpMetadata(self, path, epData):
        pass
