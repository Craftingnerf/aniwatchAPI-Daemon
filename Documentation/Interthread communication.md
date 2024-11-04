
## how does it work?

All communication happens over what I call the ThreadCommBus (thats the filename)

It has several "channels", (Server channel, download channel, Print bus, Kill bus).

The server channel, (servChannel in the code), is the channel between the server thread and the command processing thread

The download channel, (downChannel in the code), is the channel between the command processing thread and the download processing thread.

The Print bus manages the output of the program as all threads write to it (even the main thread)

The kill bus is used at program exit, when the user needs to kill all threads


For the channels they send messages through formatted JSON (I know not the best) look at [[Message Structures]]
