# aniwatchAPI-Daemon
a small daemon (kinda) and client for ghoshRitesh12's aniwatch API

Written entirely in Python b/c I'm too lazy to figure out C++ and memory management (mainly memeory management)
Some documentation found at /Documentation/!-Home (foundout that Github isnt compatable with Obsidian links)

I made the project and then decided to upload to Github (hence the sudden content popup)

For reasons I wont link my own API that I use (I dont want to get DDOS'd or Dox'd)
For setting up your own API, you will need to setup ghoshRitesh12's version 2 API (https://github.com/ghoshRitesh12/aniwatch-api)
the server will need to be defined in the config (by default its "None") (the config is made at first runtime)

The client and daemon require Python3+ (I dont know the exact version) (I'm using 3.12.2), requests, and ffmpeg to parse video

I made this project for personal reasons, and to try out threading and socket servers in python
the code is somewhat commented (just enough to be legable I hope) so you could theoretically read through it (not the client tho thats a 500 line monolith (which I should revise))
the API requester is also a good spot to look for API fetch functions (I think) although it has minimal comments (b/c its basically a getter script)

I'd reccomend checking out ghostRitesh12's API if you want more knowledge on how the API data is parsed in my scripts (lots of magic paths) (URL again (https://github.com/ghoshRitesh12/aniwatch-api))
I am in no way connected to his development group, I just used his API and repurposed it for a client/server config
