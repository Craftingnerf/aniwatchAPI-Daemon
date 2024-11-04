use:
A
python main.py
// opens up the environment
// easier to use
// slow job queueing

B
python main.py <command> <args>
// runs the command given and exits
// fast job queueing
// not user friendly


Saves a default config in "HiAnimeClient.conf" stored in the same directory as main.py *I think

has the following commands:
help
main
searchAnime
searchProducer
searchGenre
animeInfo
animeEps
downloadDescription
downloadPoster
downloadEpisode
downloadSeason
downloadAll

the download commands require a download server to be online
the default config will set the default server to be the same device as the client on port 9909
config can be changed in the directory listed above

for any of the video downloads (ep, season, all) FFMPEG must be in the server's PATH variable
these scripts are designed for windows (uses \\'s for paths) but can be modified for Linux (see the FileCreator.py script)
