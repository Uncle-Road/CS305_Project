import re
from Proxy import Proxy
from threading import Thread


class Tracker:
    def __init__(self, upload_rate=10000, download_rate=10000, port=10086):
        self.proxy = Proxy(upload_rate, download_rate, port)
        print("Tracker bind to", self.proxy.port)
        self.files = {}  # ["fid":[('("127.0.0.1", 35555)', True),('("127.0.0.1", 41201)', True)]]
        self.tthread = Thread(target=self.listen)
        self.active = True
        self.files_now_available = {}

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
                print("Now is the start with, I am in register now")
                # Client can use this to REGISTER a file and record it on the tracker
                fid = msg[10:]
                if fid not in self.files:
                    self.files[fid] = []
                # self.files[fid].append(client)
                self.files[fid].append((client, True))  # True 代表可以使用没人占着
                print(self.files)
                print("Tracker registered: " + fid + " of " + client)
                self.response("Success", frm)

            elif msg.startswith("QUERY:"):
                # Client can use this to check who has the specific file with the given fid
                fid = msg[7:]
                result = []
                # for c in self.files[fid]: #改变了数据结构,现在C为字典 test = {"fid":[("A",True),("B",True)]}
                #     result.append(c)
                for c in range(0, len(self.files[fid])):
                    print(self.files[fid][c][1])
                    if self.files[fid][c][1] is True:
                        result.append(self.files[fid][c][0])  # ["("127.0.0.1",12)"]
                        # c = (c[0], False)
                        self.files[fid][c] = (self.files[fid][c][0], False)
                        break
                print(self.files)
                print("tracker responds list: " + "[%s]" % (", ".join(result)))
                self.response("LIST: " + "[%s]" % (", ".join(result)), frm)  # LIST: [A, B, C, D],frm

            elif msg.startswith("CANCEL:"):
                # Client can use this file to cancel the share of a file
                fid = msg[8:]
                if client in self.files[fid]:
                    self.files[fid].remove(client)
                self.response("Success", frm)

            elif msg == "CLOSE":
                # Client can use this to delete everything related to it
                print("Close", client)
                for key, value in self.files.items():
                    new_list = []
                    for i in value:
                        print("check the difference", i[0], client)
                        if i[0] != client:
                            new_list.append(i)
                    self.files[key] = new_list
                print("After close, now the files becomes",
                      self.files)  # now the files becomes {'../test_files/alice.txt': [('("127.0.0.1", 47201)', True), ('("127.0.0.1", 26488)', True)]}


            elif msg.startswith("Free"):
                msg = msg[6:]
                special_notion = re.search("-.", msg).span()
                fid = msg[0:special_notion[0]]
                change_true = msg[special_notion[1]:]  # 要free的IP和PORT
                print("I am in Free now", fid, change_true)
                # for c in self.files[fid]:
                #     if c[0] is change_true and c[1] is False:
                #         c = (c[0], True)
                #     elif c[0] is change_true and c[1] is True:
                #         raise Exception("Something wrong, this value should be false")
                for c in range(0, len(self.files[fid])):
                    print("I am in For now not in if", self.files[fid][c][0], change_true,self.files[fid][c][1])
                    # if self.files[fid][c][0] is change_true and self.files[fid][c][1] is False:
                    print(self.files[fid][c][0].partition("\"")[2].partition("\"")[0],change_true.partition("(")[2].partition(",")[0],self.files[fid][c][0].partition(" ")[2].partition(")")[0],change_true.partition(",")[2].partition(")")[0],self.files[fid][c][1])
                    if self.files[fid][c][0].partition("\"")[2].partition("\"")[0] == change_true.partition("(")[2].partition(",")[0] and self.files[fid][c][0].partition(" ")[2].partition(")")[0] == change_true.partition(",")[2].partition(")")[0] and self.files[fid][c][1] is False:
                        print("I am inside For now", self.files[fid][c], "will change to", (self.files[fid][c][0], True), type(self.files[fid][c]),type((self.files[fid][c][0], True)))
                        self.files[fid][c] = (self.files[fid][c][0], True) #不能用change_true
                    elif self.files[fid][c][0] is change_true and self.files[fid][c][1] is True:
                        raise Exception("Something wrong, this value should be false")


if __name__ == '__main__':
    tracker = Tracker(port=10086)
    tracker.start()
