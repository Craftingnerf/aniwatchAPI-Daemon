import requests, json

class API:
    def __init__(self, baseURL):
        self.url = baseURL

    def getMain(self):
        out = requests.get(f"{self.url}/api/v2/hianime/home").json()
        return out
    
    def getAnimeInfo(self, animeID):
        out = requests.get(f"{self.url}/api/v2/hianime/anime/{animeID}").json()
        return out

    def searchAnime(self, query, page=None, type=None, status=None, rated=None, score=None, season=None, language=None, start_date=None, end_date=None, sort=None, genres=None):
        request = f"{self.url}/api/v2/hianime/search?q={query}"
        if page != None:        
            request += f"&page={page}"
        if type != None:        
            request += f"&type={type}"
        if status != None:        
            request += f"&status={status}"
        if rated != None:        
            request += f"&rated={rated}"
        if start_date != None:
            request += f"&start_date={start_date}"
        if end_date != None:
            request += f"&end_date={end_date}"
        if score != None:
            request += f"&score={score}"
        if genres != None:
            f"&genres={genres}"
        if sort != None:
            f"&sort={sort}"
        if season != None:
            f"&season={season}"
        if language != None:
            f"&language={language}"
            
        out = requests.get(request).json()
        return out    
    
    def getSearchSuggestions(self, query):
        request = f"{self.url}/api/v2/hianime/search/suggestion?q={query}"
        out = requests.get(request).json()
    
    
    def getProducerAnimes(self, name, page=None):
        request = f"{self.url}/api/v2/hianime/producer/{name}"
        if page != None:        
            request += f"?page={page}"
        
        out = requests.get(request).json()
        return out
    

    def getGenreAnimes(self, name, page=None):
        request = f"{self.url}/api/v2/hianime/genre/{name}"
        if page != None:        
            request += f"?page={page}"
        
        out = requests.get(request).json()
        return out
    
# categories -> "most-favorite", "most-popular", "subbed-anime", "dubbed-anime", "recently-updated", "recently-added", "top-upcoming", "top-airing", "movie", "special", "ova", "ona", "tv", "completed"        
    def getCategoryAnimes(self, category, page=None):
        request = f"{self.url}/api/v2/hianime/category/{category}"
        if page != None:        
            request += f"?page={page}"
        
        out = requests.get(request).json()
        return out



    def getEstimatedSched(self, date): # yyyy-mm-dd
        out = requests.get(f"{self.url}/api/v2/hianime/schedule?date={date}").json()
        return out
    
    def getAnimeEps(self, animeID):
        out = requests.get(f"{self.url}/api/v2/hianime/anime/{animeID}/episodes").json()
        return out
    
    def getEpServers(self, epID):
        out = requests.get(f"{self.url}/api/v2/hianime/episode/servers?animeEpisodeId={epID}").json()
        return out
    
    def getEpStreaming(self, epID, server=None, category=None):
        request = f"{self.url}/api/v2/hianime/episode/sources?animeEpisodeId={epID}"
        if server != None:
            request += f"&server={server}"
        if category != None:
            request += f"&category={category}"
        
        out = requests.get(request).json()
        return out

    
