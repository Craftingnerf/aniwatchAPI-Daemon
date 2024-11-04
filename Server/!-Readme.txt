Use:
a daemon for a hianime client

internal documentation is found in comments on the code or the CLI daemonserver.txt file (command formatting)

requires the requests library to function

stores a config file containing defaults for:

API used (defaults to my home API, plz use your own or dont share it)
Output path (defaults to C:\\HiAnimeDaemon)
server to use (hd-1) (others dont work on the API to my knowledge)
download type (Sub/Dub/Raw (Raw is just unsorted subbed most of the time, so SUB will roll over if its a new show))
Language (used for subtitles) (defaults to English) (if the specified language fails, the server rolls over to the default)
Font size (used for subtitles) (defaults to 24)
Port (Port the server is hosted on) (defaults to 9909)
Verboose (basically, how many prints do you want on the terminal?, (true = yes))

