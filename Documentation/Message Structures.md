
In my program there are several message structures

the basic one is from the client to the server

## Client to Server message
Available commands : downloadPoster, pass, downloadEpisode, downloadSeason, downloadAnimeInfo, downloadAll

{
	"cmd" : (command from list above) (String),
	"animeId": "animeID" (String),
		(IF NEEDED)
	"episodeNumber": "epNum" (integer),
		(config overrides)
	"type":  (see available categories) (String)
    "fontsize" : "Fontsize" (integer),
    "server": "serverName" (see available servers) // anything other than hd-1 will break it
    "language" : (subtitle language)
    "path" : (string) // new path to use
}


(available categories) (sub/dub/raw) (raw is generally un-categorized sub'd, and may have hardcoded subtitles)
(available server) (generally hd-1, hd-2, streamsb, streamtape) (varies on the show)

The server relays the message directly to the Command Processor which parses and handles the command to be passed to the download thread


The next message to look at would be the command processor thread to the download thread
## Command Processor to Download message
Available types : Image, Video, Description
{
    "Type" : (Type from available types) (String)
    "Path" : (string) (absolute filepath for the output (doesnt include filename))
    "filename": (string) (name for the file)
    // for images
    "url" : (string) (url to the image)
    // description
    "text": (list of strings) (text to be contained in the info.txt)
    // video
    "video" : "url", (url to the video file)
    "category": (sub/dub/raw)
    // the following need sub
    "captions" : "url", (url to the captions file (usually a .vtt))
    "font" :  "Fontsize" (integer)
}

