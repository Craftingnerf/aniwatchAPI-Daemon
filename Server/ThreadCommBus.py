# has several queues for communicating between threads
import queue

class BUS:
    def __init__(self):
        self.servChannel = queue.Queue()
        self.downChannel = queue.Queue()
        self.PrintBus = queue.Queue()
        self.killBus = queue.Queue()
    
