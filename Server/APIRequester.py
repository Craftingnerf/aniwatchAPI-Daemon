import requests, json

class API:
    def __init__(self, baseURL):
        self.url = baseURL
        self.attempts = 3

    def getMain(self):
        request = f"{self.url}/api/v2/hianime/home"
        
        return self.makeRequest(request)
    
    def getAnimeInfo(self, animeID):
        request = f"{self.url}/api/v2/hianime/anime/{animeID}"

        return self.makeRequest(request)

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
        
        return self.makeRequest(request)
    
    def getSearchSuggestions(self, query):
        request = f"{self.url}/api/v2/hianime/search/suggestion?q={query}"

        return self.makeRequest(request)
    
    
    def getProducerAnimes(self, name, page=None):
        request = f"{self.url}/api/v2/hianime/producer/{name}"
        if page != None:        
            request += f"?page={page}"
        
        return self.makeRequest(request)
    

    def getGenreAnimes(self, name, page=None):
        request = f"{self.url}/api/v2/hianime/genre/{name}"
        if page != None:        
            request += f"?page={page}"
        
        return self.makeRequest(request)
    
# categories -> "most-favorite", "most-popular", "subbed-anime", "dubbed-anime", "recently-updated", "recently-added", "top-upcoming", "top-airing", "movie", "special", "ova", "ona", "tv", "completed"        
    def getCategoryAnimes(self, category, page=None):
        request = f"{self.url}/api/v2/hianime/category/{category}"
        if page != None:        
            request += f"?page={page}"
        
        return self.makeRequest(request)



    def getEstimatedSched(self, date): # yyyy-mm-dd
        request = f"{self.url}/api/v2/hianime/schedule?date={date}"

        return self.makeRequest(request)
    
    def getAnimeEps(self, animeID):
        request = f"{self.url}/api/v2/hianime/anime/{animeID}/episodes"

        return self.makeRequest(request)
    
    def getEpServers(self, epID):
        request = f"{self.url}/api/v2/hianime/episode/servers?animeEpisodeId={epID}"
        
        return self.makeRequest(request)
    
    def getEpStreaming(self, epID, server=None, category=None):
        request = f"{self.url}/api/v2/hianime/episode/sources?animeEpisodeId={epID}"
        if server != None:
            request += f"&server={server}"
        if category != None:
            request += f"&category={category}"
        
        return self.makeRequest(request)

    
    def makeRequest(self, request):
        count = 0
        while count < self.attempts:
            try:
                out = requests.get(request).json()
                if out["success"]:
                    return out
            except Exception as e:
                print(f"Error!\n{e}\n") 