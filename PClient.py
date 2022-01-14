# -*- coding : utf-8-*-
# coding:unicode_escape
from Proxy import Proxy
import ast
import threading
import time
import re


class PClient:

    def __init__(self, tracker_addr=(str, int), proxy=None, port=None, upload_rate=0, download_rate=0,
                 packet_size=20000, name=None):
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = Proxy(upload_rate, download_rate, port)  # Do not modify this line!
        self.tracker = tracker_addr
        self.name = name
        self.target_address_get = 0
        self.target_address = ()
        """
        Start your additional code below!
        """
        self.downloaded_file = b"empty"
        self.active = False
        self.packet_size = packet_size
        self.registered_fid = set()
        self.fid_length = {} #存有的fid的length给tracker发
        self.already_download = 0
        self.special_use_close = ""
        self.listening = True
        self.thread = threading.Thread(target=self.alwaysListen, args=[])
        self.thread.start()

    def __send__(self, data: bytes, dst: (str, int)):
        """
        Do not modify this function!!!
        You must send all your packet by this function!!!
        :param data: The data to be sent
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

    def register(self, file_path: str):
        """
        Share a file in P2P network
        :param file_path: The path to be shared, such as "./alice.txt"
        :return: fid, which is a unique identification of the shared file and can be used by other PClients to
                 download this file, such as a hash code of it
        """

        """
        Start your code below!
        """
        print(self.name, "register start")
        fid = file_path
        already_in_self_fid_length = False  # false就是没有这个文件的length，要存
        for key,value in self.fid_length.items():
            if key == fid:
                already_in_self_fid_length = True
                break
        if not already_in_self_fid_length:
            with open(fid, 'rb') as f:  # f = open(../tes,'rb')
                data = f.read()
            packets = [data[i * self.packet_size: (i + 1) * self.packet_size]
                       for i in range(len(data) // self.packet_size + 1)]
            self.fid_length[fid] = len(packets)
        if fid in self.registered_fid:
            return fid
        else:
            self.registered_fid.add(fid)
            msg = "REGISTER: " + fid
            msg = msg.encode()  # string发送之前要encode
            self.__send__(msg, ("127.0.0.1", 10086))
            time.sleep(0.3)
            # print(self.name, "register finish")
            """
            End of your code
            """
            return fid

    def download(self, fid) -> bytes:
        """
        Download a file from P2P network using its unique identification
        :param fid: the unique identification of the expected file, should be the same type of the return value of share()
        :return: the whole received file in bytes
        """

        """
        Start your code below!
        """

        msg = "QUERY: " + fid
        msg = msg.encode()
        self.__send__(msg, self.tracker)
        # time.sleep(0.25)

        while self.target_address_get == 0:
            msg = "QUERY: " + fid
            msg = msg.encode()
            self.__send__(msg, self.tracker)
            time.sleep(0.25)

        if self.target_address_get == 1:
            request = "REQUEST: " + fid
            request = request.encode()
            self.__send__(request, self.target_address)
            self.active = True
            while self.active:
                time.sleep(0.1)
            self.target_address_get = 0

        data = self.downloaded_file

        # data = data.encode()
        print(self.name, "download finish")
        # print()
        self.register(fid)
        """
        End of your code
        """
        return data

    def cancel(self, fid):
        """
        Stop sharing a specific file, others should be unable to get this file from this client anymore
        :param fid: the unique identification of the file to be canceled register on the Tracker
        :return: You can design as your need
        """
        self.registered_fid.remove(fid)
        msg = "CANCEL: " + fid
        msg = msg.encode()
        self.__send__(msg, self.tracker)
        print(self.name, "cancel")
        """
        End of your code
        """

    def close(self):
        """
        Completely stop the client, this client will be unable to share or download files anymore
        :return: You can design as your need
        """
        # print(self.name, "ready to close")
        self.registered_fid.clear()
        msg = "CLOSE"
        msg = msg.encode()

        self.__send__(msg, self.tracker)

        # print(self.name, self.proxy.send_queue.qsize())
        while not self.proxy.send_queue.empty():
            time.sleep(0.5)
            # print(self.name, self.proxy.send_queue.qsize())

        print(self.name, "close")
        """
        End of your code
        """
        self.listening = False
        # print(self.name, "listening is", self.listening)
        self.proxy.close()

    def listen(self):

        # print(self.name, "listen start")
        try:
            msg, frm = self.__recv__(10)
        except Exception:
            return
        self.special_use_close = frm  # special use only use for instance close that shut down uncompleted transfer

        # print(self.name, "listen over")

        msg = msg.decode()

        if msg.startswith("REQUEST:"):  # PClient收到请求文件的fid
            fid = msg[9:]

            with open(fid, 'rb') as f:  # f = open(../tes,'rb')
                data = f.read()
            packets = [data[i * self.packet_size: (i + 1) * self.packet_size]
                       for i in range(len(data) // self.packet_size + 1)]
            self.__send__(("GIVE: " + fid + "-.-." + str(len(packets))).encode(), frm)
            print(self.name, "send packet length is:", len(packets))
            # time.sleep(0.25)

            self.__transmitting = True
            for packet in packets:
                self.__send__(packet, frm)
            # print("3", self.__transmitting)
            self.__transmitting = False

        elif msg.startswith("GIVE:"):  # 给这个PClient的文件
            special_notion = re.search("-.-.", msg).span()  # 正确
            fid = msg[6:special_notion[0]]
            msg = msg[special_notion[1]:]#文件总长度
            # global downloaded_file  # 改全局变量一定要加global关键字
            self.downloaded_file = b""
            for idx in range(int(msg)):
                start =time.time()
                # if(time.time()-start>1)
                data_fragment, frm = self.__recv__()
                self.downloaded_file += data_fragment
                if idx % 100 == 0:
                    print("%s receive %d" % (self.name, idx))

            msg = "OK"
            msg = msg.encode()
            self.__send__(msg, frm)
            self.already_download = 1
            self.active = False
            self.__send__(("Free: " + fid + "-." + "("+str(frm[0])+","+str(frm[1])+")").encode(), ("127.0.0.1", 10086)) #send 需要encode()
            print("already send Free", fid, frm)
        elif msg.startswith("LIST:"):
            lst = msg[6:]
            who_have = ast.literal_eval(lst)  # it is a list of tuples. eg:  ('127.0.0.1', 38235)
            if len(who_have) != 0:
                print(self.name, "knows who have it:", who_have)
            if len(who_have) != 0:
                self.target_address = who_have[0]
                self.target_address_get = 1
            # else:
                # print("No server available for",self.name)

    def alwaysListen(self):
        while self.listening:
            # print(self.name, "invoke listen")
            self.listen()
        # print(self.name, "close listening")


if __name__ == '__main__':
    pass
