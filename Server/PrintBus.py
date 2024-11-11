import threading
import ThreadCommBus

class PrintBus:
    def __init__(self, bus=ThreadCommBus.BUS, vb=False):
        self._BUS = bus
        self.header = "(PRINT): "
        self.verbose = vb

    def startPrintBus(self, id):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.header = f"Thread({id}) {self.header}" # update the header
        self.Print("Print thread started!")
        return self.thread
        
    def Print(self, msg, verb = False):
        if verb and self.verbose:
            self._BUS.PrintBus.put(f"(Verbose) {self.header}{msg}")
        elif verb == False:
            self._BUS.PrintBus.put(f"{self.header}{msg}")

    def run(self):
        while self._BUS.killBus.empty():
            msg = self._BUS.PrintBus.get()
            print(msg)
    
    def stopPrintThread(self):
        if self._BUS.killBus.empty():
            self._BUS.killBus.put(1)
        self.Print("Print thread shutting down")
        self.thread.join()