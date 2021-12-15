from socketserver import BaseRequestHandler, ThreadingUDPServer
from Proxy import Proxy
from threading import Thread


class SimpleTracker:
    def __init__(self, upload_rate=10000, download_rate=10000, port=10086):
        self.proxy = Proxy(upload_rate, download_rate, port)
        print("Tracker bind to", self.proxy.port)
        self.files = {}
        self.tthread = Thread(target=self.listen)
        self.active = True

    def __send__(self, data: bytes, dst: (str, int)):
        """
        Do not modify this function!!!
        You must send all your packet by this function!!!
        :param data: The data to be send
        :param dst: The address of the destination
        """
        self.proxy.sendto(data, dst)

    def __recv__(self, timeout=None) -> (bytes, (str, int)):
        """
        Do not modify this function!!!
        You must receive all data from this function!!!
        :param timeout: if its value has been set, it can raise a TimeoutError;
                        else it will keep waiting until receive a packet from others
        :return: a tuple x with packet data in x[0] and the source address(ip, port) in x[1]
        """
        return self.proxy.recvfrom(timeout)

    def response(self, data: str, address: (str, int)):
        self.__send__(data.encode(), address)

    def start(self):
        self.tthread.start()

    def listen(self):
        while self.active:
            print("start receiving")
            msg, frm = self.__recv__()
            print("receive something!")
            msg, client = msg.decode(), "(\"%s\", %d)" % frm  # client is a string

            if msg.startswith("REGISTER:"):
                # Client can use this to REGISTER a file and record it on the tracker
                fid = msg[10:]
                if fid not in self.files:
                    self.files[fid] = []
                self.files[fid].append(client)
                print("Tracker registered: " + fid + " of " + client)
                self.response("Success", frm)

            elif msg.startswith("QUERY:"):
                # Client can use this to check who has the specific file with the given fid
                fid = msg[7:]
                result = []
                for c in self.files[fid]:
                    result.append(c)
                print("tracker responds list: " + "[%s]" % (", ".join(result)))
                self.response("LIST: " + "[%s]" % (", ".join(result)), frm)

            elif msg.startswith("CANCEL:"):
                # Client can use this file to cancel the share of a file
                fid = msg[8:]
                if client in self.files[fid]:
                    self.files[fid].remove(client)
                self.response("Success", frm)

            elif msg.startswith("CLOSE"):
                # Client can use this to delete everything related to it
                for i in self.files:
                    if client in self.files[i]:
                        self.files[i].remove(client)


if __name__ == '__main__':
    tracker = SimpleTracker(port=10086)
    tracker.start()
