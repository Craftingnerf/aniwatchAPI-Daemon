import subprocess, os, requests, time, ThreadCommBus, json

_BUS = ThreadCommBus.BUS()
header = "(File Creator): "
verbose = False



color = "\033[32m"
colorReset = "\033[00m"

def Print(message, verb=False):
    if verb and verbose == True:
        _BUS.PrintBus.put(f"(Verbose) {color}{header}{message}{colorReset}")
    elif verb == False:
        _BUS.PrintBus.put(f"{color}{header}{message}{colorReset}")

Print("File creator loaded")

def downloadPoster(path, poster, name):
    createPath(path)
    outputFile = os.path.join(path, name).replace("\\","/") # get the full path to where we want the poster
    # request the URL, and save the data
    resp = requests.get(poster)
    if resp.status_code != 200:
        Print("Failed to download image!")
        return

    file = open(outputFile, "wb")
    file.write(resp.content)
    file.close()    
    return 


def createPath(path):
    Print(f"Ensuring path '{path}' exitsts!", True)
    Print(f"Type of path : {type(path)}", True)
    Print(f"Exists? {os.path.exists(path)}", True)
    if not os.path.exists(path): # check if the path exists, and if it does we're done
        path = path.replace("\\", "/")
        bPath = path.split("/")[0]+"/" # split the path (using \'s b/c I'm on windows)
        # print(bPath) # print the base of the path, should be C:\
        Print("Making dir", True)
        Print(bPath, True)
        for path2 in path.split("/")[1:]: # loop through all the indexes of the split path
            Print(os.path.join(bPath,path2), True) # print the new path for debug purposes
            if not os.path.exists(os.path.join(bPath,path2)): # that path doesnt exist make the new folder
                os.mkdir(os.path.normpath(os.path.join(bPath,path2)))
                Print(f"Created Folder at {os.path.join(bPath,path2)}") # debug for the user
            bPath = os.path.join(bPath,path2).replace("\\","/") # update the path we're working with
    # this function is effectivly a recursive mkdir function
    Print(f"'{path}' has been created!", True)

def createDescriptionFile(path, lines, filename):
    createPath(path)
    # get the path for the discription
    animePath = os.path.join(path, filename).replace("\\","/")
    # open and write to (in bytes) the anime info
    file = open(animePath, "wb") 
    Print(f"Writing anime description to : {animePath}") 
    # loop through all lines provided by the animeInfo obj
    for line in  lines: 
        line+="\n"
        # write the lines to the file
        file.write(line.encode("utf-8")) 
    # close the file b/c we're done with it
    file.close() 
    Print("Finished writing lines", True)
    return


# # # # # # # # # # # # # # # #
# Download subittles from url #
# # # # # # # # # # # # # # # #
def downloadSubtitles(filePath, epName, captions):
    subtitles = []
    Print("Caption Downloader Started")
    for caption in captions:
        captionFile = caption["file"].split("/")[-1] # get the end of the path string (/path/to/file.type)
        captionFile = captionFile.split(".")[0] # isolate the name (we dont want the type)
        fileName = f"{epName}-{captionFile}"
        outputFile = os.path.join(filePath, f"{fileName}.srt").replace("\\", "/")
        args = [
            "-y", # overwrite existing files
            f"-i {caption["file"]}", # file to download
            "-c:s srt", # subtitle codec converts to srt
            f"\"{outputFile}\"" # output file
        ]
        subtitles.append(outputFile)
        cmd = f"ffmpeg {" ".join(args)}"
        subprocess.run(cmd, shell=True) 
        Print(cmd, True)
    return subtitles

# # # # # # #  # # # # # # # #
# Downloads video from a url #
# # # # # # #  # # # # # # # #
def downloadVideo(video, filePath, epName):
    epName = ffmpegClean(epName)
    createPath(filePath) # make sure the filepath exists
    outputFile = os.path.join(filePath, f"{epName}-NoSubs.mp4").replace("\\","/")
    Print("FFMPEG Video Downloader Started")

    args = [
        "-y", # overwrite existing copies
        f"-i \"{video}\"", # download from the video url
        "-c copy", # copy the input stream (dont re-encode it)
        f"\"{outputFile}\"" # where to put the result
    ]

    # "compile" the command
    cmd = "ffmpeg " + " ".join(args)
    # run the command
    subprocess.run(cmd, shell=True) 
    Print(cmd, True)

    return outputFile


# # # # # # # # # #  # # # # # # # # # #
# Get map and input data from captions #
# # # # # # # # # #  # # # # # # # # # #
def getSubitleData(caption, i):
    captionFile = caption["file"].replace("\\", "/").split("/")[-1] # get the end of the path string (/path/to/file.type)
    captionFile = captionFile.split(".")[0] # isolate the name (we dont want the type)

    output = ["", "", ""]
    # get the stream url for the caption
    output[0] = f"-i \"{caption["file"]}\"" 

    # map the subtitle to the track
    output[1] = f"-map \"{i+1}\""

    # get the metadata
    output[2] = f"-metadata:s:s:{i} language=\"{captionFile}\" -metadata:s:s:{i} title=\"{caption["label"]}\"" 

    return output


# # # # # # # #  # # # # # # # # # 
# Adds subtitles to a video file #
# # # # # # # #  # # # # # # # # # 
def addSubtitlesToVideo(epName, filePath, captions):
    videoFile = os.path.join(filePath,f"{epName}.mp4").replace("\\","/")
    file = os.path.join(filePath, f"{epName}-NoSubs.mp4").replace("\\","/")
    # rename the raw video file to a different name to add the subs
    
    args = [
        "-y", # overwrite existing files 
        f"-i \"{file}\"" # video input
    ]
    maps = [
        "-map 0" # map the video
    ]

    metadata = []
    for i in range(len(captions)):
        data = getSubitleData(captions[i], i)
        args.append(data[0]) # add the inputs
        maps.append(data[1]) # add the maps 
        metadata.append(data[2]) # add the metadata

    args += maps
    args += metadata

    args += [
        "-c:s mov_text", # subtitle codec
        "-preset veryfast", # speeds up subtitle encoding/addition at the cost of a larger file size
        f"\"{videoFile}\"" # output file
    ]

    # compile and run the command
    cmd = f"ffmpeg {" ".join(args)}"
    subprocess.run(cmd, shell=True) 
    Print(cmd, True)
    
    Print("Removing old video file")
    os.remove(file)
    return videoFile


# # # # # # # # # # # # # # # # # # # # # #
# My own method for safely renaming files #
# # # # # # # # # # # # # # # # # # # # # #
def rename(original, replacement):
    # get the name and extention of the replacement file (seperate)
    repName = replacement.split(".")[0]
    repExt = replacement.split(".")[1]
    repNameMod = repName

    # protects from some errors
    Print("Waiting 1 seccond for file to be free", True)
    time.sleep(1)

    counter = 0
    # check if the replacement file exists
    while (os.path.exists(f"{repNameMod}.{repExt}")):
        Print(f"File \"{repNameMod}.{repExt}\" exists!, changing name", True)
        # if the replacement file exists modify the replacment name and check again
        counter+=1
        repNameMod = f"{repName}-{counter}"
    
    # inform the user of the new file name (if verbose is enabled)
    if counter > 0:
        Print(f"Original file exists, name changed to : \"{repNameMod}.{repExt}\"", True)
    
    replacementFile = f"{repName}.{repExt}"
    
    # rename the file now that we know we have a unique name
    os.rename(original, replacementFile)
    return
    

# # # # # # # # # # #  # # # # # # # # # # #
# Downloads video with the captions slower #
# # # # # # # # # # #  # # # # # # # # # # #
def ffmpegGen(video, captions, filePath, epName):
    epName = ffmpegClean(epName)
    createPath(filePath) # make sure the filepath exists

    videoFile = downloadVideo(video, filePath, epName) # download the video

    subtitleFile = addSubtitlesToVideo(epName, filePath, captions) # add captions to the video


# # # # # # # # # # # # #  # # # # # # # # # # # # #
# Downloads video without the captions 100x faster #
# # # # # # # # # # # # #  # # # # # # # # # # # # #
def ffmpegGenNoCaptions(video, filePath, epName):
    epName = ffmpegClean(epName)
    createPath(filePath) # make sure the filepath exists
    filename = os.path.join(filePath,f"{epName}.mp4").replace("\\","/")

    videoFile = downloadVideo(video, filePath, epName) # download the video
    # rename the file (removes the "-NoSubs" bit on a file, which isnt needed for DUB or some RAW)
    rename(videoFile, filename)


def ffmpegClean(string):
    invalidChars = "`\'\"(){}[]"
    for char in invalidChars:
        string = string.replace(char, "")
    return string

# 
# Older code
# copied from my "ffmpegGenerator.py"
# I made this when I made my old HiAnimeCLI client (not on github)
# 

def convertWebVttToSrt(tempFilepath):
    Print("Converting temp file to srt subtitles", True)
    outFile = ".".join(tempFilepath.split(".")[:-1])
    outFile = f'{outFile}.srt'
    outFile = outFile.replace("\'", "")
    args = [
        f'-i {tempFilepath}', # designates a filepath
        '-y', # automatically replaces existing files
        outFile # output file
    ]
    cmd = f"ffmpeg {" ".join(args)}"
    subprocess.run(cmd, shell=True)
    return outFile


def fetchURL(url):
    resp = requests.get(url) # get the subtitles from the URL
    if resp.status_code == 200:
        return resp.text # return the text if found
    else:
        raise Exception(f"Failed to fetch subtitles from URL")

def saveTempFile(data, fileIn, num):
    tmpFilePath = os.path.join(fileIn, str(num)).replace("\\","/")+"-Captions.vtt"
    tmpFile = open(tmpFilePath, "w", encoding="utf-8")
    tmpFile.write(data)
    tmpFile.close()
    
    return tmpFilePath

# leagacy (or depracated) download function
# will see minimal updates (along with the rest of the codebase unless I run into a bug)
# burns the subtitles into the video (and has problems with linux for no reason)
def ffmpegGenDEP(video, captions, filePath, epName, fontSize):
    epName = ffmpegClean(epName)
    createPath(filePath) # make sure the filepath exists
    outputFile = os.path.join(filePath,f"{epName}").replace("\\","/") # the output file should be "<epNum>-<epName>.mp4"
    Print("FFMPEG Video Downloader Started")
    
    subtitleCont = fetchURL(captions).strip()
    tmpFilePath = saveTempFile(subtitleCont, filePath, epName) # save the subtitles to a .vtt file
    srtFile = convertWebVttToSrt(tmpFilePath) # convert the file to a .srt
    os.remove(tmpFilePath)
    Print(f"Temporary subtitle file created at: '{srtFile}'", True)
    args = [
        '-protocol_whitelist',
        'file,http,https,tcp,tls,crypto',
        "-y", # -y allows automatic file overwriting, -n automatically skips if there is a file with the same name
        '-i',
        "\""+video+"\"",
        '-vf',
        f'\"subtitles=\'{srtFile.replace("\\","\\\\").replace(":", "\\:")}\':force_style=\'fontsize={str(fontSize)}\'\"', # 
        '-c:a',
        'copy',
        '-c:v',
        'libx264',
        '-crf',
        '23',
        '-preset',
        'veryfast',
        '-s',
        '1920x1080',
        "\""+outputFile+'.mp4'+"\""
    ]
    time.sleep(.5)
    cmd = "ffmpeg " + " ".join(args) # concatinates the command
    subprocess.run(cmd, shell=True) # runs the command
    Print(cmd, True) # prints the command for debug purposes (and potentially later use)
    
    # Delete the temporary subtitle file
    # this is the bit that has linux problems
    # commenting out the os.remove() will solve the issue (its needed for first playback for whatever reason)
    Print("deleting temp file", True)
    os.remove(srtFile)

def ffmpegGenNoCaptionsDEP(video, filePath, epName):
    epName = ffmpegClean(epName)
    
    createPath(filePath)
    Print("FFMPEG Video Downloader Started")
    
    outputFile = os.path.join(filePath,f"{epName}").replace("\\","/")
    outFile = outputFile+'.mp4'
    
    Print(outFile, True)
    args = [
        '-protocol_whitelist',
            'file,http,https,tcp,tls,crypto',
            "-y", # -y allows automatic file overwriting, -n automatically skips if there is a file with the same name
            '-i',
            video,
            '-c:a',
            'copy',
            '-c:v',
            'libx264',
            '-crf',
            '23',
            '-preset',
            'veryfast',
            '-s',
            '1920x1080',
            "\""+outFile+"\""
    ]
    cmd = "ffmpeg " + " ".join(args)
    
    subprocess.run(cmd, shell=True)
    Print(cmd, True)