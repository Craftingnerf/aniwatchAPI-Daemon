import pathGenerator



# # #  # # #
### INFO ###
# # #  # # #
# 
# Started using jellyfin and thought that I should add
# built in compatability so its a near drop in replacement folder
# 


# # # # # # # # #
### STRUCTURE ###
# # # # # # # # #
#
# I'm going to change the main command thread to
# call a function from another object (something like self.compatability.getEpPath)
# and have that pass in the anime data
# from there I can parse the correct path (if it has seasons listed) 
# it should default fall back to its own path creator
import json

class JellyFinPathCreator(pathGenerator.defaultPathCreator):
    def __init__(self):
        self.name = "Jellyfin"
        pass

    def getInts(self, string):
        ints = "0123456789-"
        for char in string:
            # loop through all the chars in the string
            # check if they arnt in the ints string (char array)
            # and remove the chars
            if not ints.__contains__(char):
                string = string.replace(char, "")
        string.strip() # remove trailing " "'s
        string = string.replace(" ", "_")
        return string


    def getSeasonIndex(self, animeData):
        if len(animeData["seasons"]) > 0:
            for i in range(len(animeData["seasons"])):
                season = animeData["seasons"][i]
                if season["isCurrent"]:
                    return i+1
        else:
            return 1

    def getSeriesName(self, animeData):
        if len(animeData["seasons"]) > 0:
            for season in animeData["seasons"]:
                return season["name"]
        else:
            return animeData["anime"]["info"]["name"]

    def getSeriesPoster(self, animeData):
        if len(animeData["seasons"]) > 0:
            for season in animeData["seasons"]:
                if season["title"] == "Season 1":
                    return season["poster"]
        else:
            return animeData["anime"]["info"]["poster"]

    #
    # stuff required for the metadata
    #
    def generateGenreTag(self, animeData):
        lines = []
        genres = animeData["anime"]["moreInfo"]["genres"]
        for genre in genres:
            lines.append(f"<genre>{genre}</genre>")
        return lines
    
    def generateTitleTag(self, animeData):
        lines = []
        name = animeData["anime"]["info"]["name"]
        lines.append(f"<title>{name}</title>")
        return lines
    
    def generateSeasonNumber(self, animeData):
        lines = []
        seasonNum = self.getSeasonIndex(animeData)
        lines.append(f"<seasonnumber>{seasonNum}</seasonnumber>")
        return lines

    def generateDescription(self, animeData):
        lines = []
        description = animeData["anime"]["info"]["description"]
        lines.append(f"<plot>{description}</plot>")
        return lines


    def generateShowMetadata(self, animeData):
        lines = []
        lines.append("<tvshow>")

        lines.append(f"<title>{self.getSeriesName(animeData)}</title>")

        lines += self.generateGenreTag(animeData)

        lines.append("</tvshow>")
        return lines

    def generateSeasonMetadata(self, animeData):
        lines = []
        lines.append("<season>")

        lines += self.generateDescription(animeData)
        lines += self.generateTitleTag(animeData)
        
        lines += self.generateGenreTag(animeData)

        lines += self.generateSeasonNumber(animeData)

        lines.append("</season>")

        return lines

    #
    # downloads the cover poster that jellyfin wants
    #
    def downloadExtra(self, path, animeData, _BUS):
        genPath = self.osPathJoin(path, self.getSeriesName(animeData).replace(" ", "_"))
        poster = self.getSeriesPoster(animeData)
        posterName = f"poster.{poster.split(".")[-1]}"

        msg = { "Type" : "Image", "Path": genPath, "url" : poster, "filename": posterName}

        _BUS.downChannel.put(msg)
    

    def getMetadata(self, path, animeData, _BUS):
        # get the path (should be the header directory of all the seasons)
        genPath = self.osPathJoin(path, self.getSeriesName(animeData).replace(" ", "_"))

        # if the show already has metadata we shouldnt need to overwrite it
        showMetadataPath = self.osPathJoin(genPath, "tvshow.nfo")
        if not self.osPathExists(showMetadataPath):
            # if it does get the metadata and send the download cmd
            showMetadata = self.generateShowMetadata(animeData)
            msg = {"Type" : "Description", "Path" : genPath}
            msg["text"] = showMetadata
            msg["filename"] = "tvshow.nfo"

            _BUS.downChannel.put(msg)
        
        # generate the season metadata
        seasonMetadata = self.generateSeasonMetadata(animeData)
        # generate and send the download cmd
        msg = {"Type" : "Description", "Path" : self.generatePath(path, animeData)}
        msg["text"] = seasonMetadata
        msg["filename"] = "season.nfo"

        _BUS.downChannel.put(msg)


    def generatePath(self, path, animeData):
        genPath = self.osPathJoin(path, self.getSeriesName(animeData).replace(" ", "_"))
        folderName = f"Season_{self.getSeasonIndex(animeData)}"
        genPath = self.osPathJoin(genPath, folderName)

        return genPath.replace("\\","/")
    
    # generate the poster names (some media servers might only accept files of certian names)
    def getPosterName(self, animeData, poster):
        return f"cover.{poster.split(".")[-1]}"
    
    def epNameParser(self, epData, animeData, type, maxEps):
        # jellyfin formatting
        # showname-epName-S00E00.mp4
        
        animeName = animeData["anime"]["info"]["name"]

        return f"{self.cleanStr(animeName.replace(" ", "_"))}-{self.cleanStr(epData["title"].replace(" ", "_"))}-{type.upper()}-E{self.numFormatter(epData["number"], maxEps)}"
