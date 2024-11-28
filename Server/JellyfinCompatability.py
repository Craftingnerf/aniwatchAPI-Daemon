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


class JellyFinPathCreator(pathGenerator.defaultPathCreator):
    def __init__(self):
        pass


    def getSeason(self, animeData):
        if len(animeData["seasons"]) > 0:
            for season in animeData["seasons"]:
                if season["isCurrent"]:
                    return season["title"].replace(" ", "_")
        else:
            return "Season_1"

    def getSeriesName(self, animeData):
        if len(animeData["seasons"]) > 0:
            for season in animeData["seasons"]:
                if season["title"] == "Season 1":
                    return season["name"].replace(" ", "_")
        else:
            return animeData["anime"]["info"]["name"].replace(" ", "_")

    def getSeriesPoster(self, animeData):
        if len(animeData["seasons"]) > 0:
            for season in animeData["seasons"]:
                if season["title"] == "Season 1":
                    return season["poster"]
        else:
            return animeData["anime"]["info"]["poster"]


    #
    # downloads the cover poster that jellyfin wants
    #
    def downloadExtra(self, path, animeData, _BUS):
        genPath = self.osPathJoin(path, self.getSeriesName(animeData))
        poster = self.getSeriesPoster(animeData)
        posterName = f"poster.{poster.split(".")[-1]}"

        msg = { "Type" : "Image", "Path": genPath, "url" : poster, "filename": posterName}

        _BUS.downChannel.put(msg)

    def generatePath(self, path, animeData):
        genPath = self.osPathJoin(path, self.getSeriesName(animeData))
        genPath = self.osPathJoin(genPath, self.getSeason(animeData))

        return genPath.replace("\\","/")
    
    # generate the poster names (some media servers might only accept files of certian names)
    def getPosterName(self, animeData, poster):
        return f"cover.{poster.split(".")[-1]}"

