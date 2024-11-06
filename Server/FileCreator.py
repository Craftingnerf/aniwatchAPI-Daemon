import subprocess, os, requests, time, ThreadCommBus

_BUS = ThreadCommBus.BUS()
header = "(File Creator): "
verboose = False



color = "\033[32m"
colorReset = "\033[00m"

def Print(message, verb=False):
    if verb and verboose == True:
        _BUS.PrintBus.put(f"(Verboose) {color}{header}{message}{colorReset}")
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

# 
# Older code
# copied from my "ffmpegGenerator.py"
# I made this when I made my old HiAnimeCLI client
# 

def ffmpegClean(string):
    invalidChars = "`\'\"(){}[]"
    for char in invalidChars:
        string = string.replace(char, "")
    return string


def convertWebVttToSrt(tempFilepath):
    Print("Converting temp file to srt subtitles", True)
    outFile = ".".join(tempFilepath.split(".")[:-1])
    outFile = f'{outFile}.srt'
    outFile = outFile.replace("\'", "")
    args = [
        '-i',
        tempFilepath,
        '-y',
        outFile
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

def ffmpegGen(video, captions, filePath, epName, fontSize):
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
    Print("deleting temp file", True)
    os.remove(srtFile)

def ffmpegGenNoCaptions(video, filePath, epName):
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