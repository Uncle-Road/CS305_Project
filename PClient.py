#-*- coding : utf-8-*-
# coding:unicode_escape
from Proxy import Proxy
import hashlib
import ast
import threading
import time


target_address = []


class PClient:

    def __init__(self, tracker_addr=(str, int), proxy=None, port=None, upload_rate=0, download_rate=0,
                 packet_size=20000, name=None):
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = Proxy(upload_rate, download_rate, port)  # Do not modify this line!
        self.tracker = tracker_addr
        self.name = name
        """
        Start your additional code below!
        """
        self.target_address_get = 0
        self.target_address = []
        self.already_downloaded = 0
        self.file_length = 0
        self.downloaded_file = [b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'']
        self.active = False

        self.thread = threading.Thread(target=self.alwaysListen, args=[])
        self.thread.start()
        self.packet_size = packet_size


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

        # md5 = hashlib.md5()
        # md5.update(file_path)
        # fid = md5.hexdigest()  # fid 变成hash码
        fid = file_path
        with open(fid, 'rb') as f:  # f = open(../tes,'rb')
            data = f.read()
        packets = [data[i * self.packet_size: (i + 1) * self.packet_size]
                   for i in range(len(data) // self.packet_size + 1)]

        msg = "REGISTER" + " " + fid + " " + str(len(packets))
        msg = msg.encode()  # string发送之前要encode
        self.__send__(msg, ("127.0.0.1", 10086))
        time.sleep(0.25)

        print(self.name, "register finish")
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
        # print(self.name, "download start")

        msg = "QUERY: " + fid
        msg = msg.encode()
        self.__send__(msg, self.tracker)
        time.sleep(0.3)

        print(self.name, "here1")
        # print("target_address_get =", target_address_get)
        threads = []
        if self.target_address_get != 0:
            address_num = len(self.target_address)
            for i in range(address_num - 1):
                threads.append(threading.Thread(target=self.alwaysListen, args=[]))
            for i in range(0, address_num):
                request = "REQUEST" + " " + str(address_num) + " " + str(i) + " " + fid
                request = request.encode()
                if i < address_num - 1:
                    threads[i].start()
                self.__send__(request, self.target_address[i])
                # self.active = True
                # while self.active:
                #     time.sleep(0.1)
            target_address_get = 0

        print(self.name, "here2")

        while self.already_downloaded < self.file_length:
            time.sleep(0.1)

        print(self.name, self.already_downloaded)

        print(self.name, "here3")

        # for t in threads:
        #     print(self.name, "wtf")
        #     t.join()

        print(self.name, "here4")

        data = b''
        for part in self.downloaded_file:
            data += part

        self.already_downloaded = 0
        self.file_length = 0

        # data = data.encode()
        print(self.name, "download finish")

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
        msg = "CLOSE"
        msg = msg.encode()
        self.__send__(msg, self.tracker)
        # time.sleep(1)
        print(self.name, "close")
        """
        End of your code
        """

        self.proxy.close()

    # TODO: listen要适用于所有函数，还要加东西。
    def listen(self):

        msg, frm = self.__recv__()

        # msg = msg.decode()

        if msg.split()[0] == b"REQUEST":  # PClient收到请求文件的报文 REQUEST address_num my_num fid
            msg = msg.decode()
            address_num = int(msg.split()[1])
            my_num = int(msg.split()[2])
            fid = msg.split()[3]

            with open(fid, 'rb') as f:  # f = open(../tes,'rb')
                data = f.read()
            packets = [data[i * self.packet_size: (i + 1) * self.packet_size]
                       for i in range(len(data) // self.packet_size + 1)]

            l = int(len(packets) / address_num)
            my_length = int(len(packets) / address_num)
            if my_num + 1 == address_num:
                my_length = int(len(packets) / address_num) + len(packets) - int(len(packets) / address_num) * address_num

            # msg = "GIVE" + " " + str(my_length) + " " + str(my_num)
            # msg = msg.encode()
            # self.__send__(msg, frm)

            print(self.name, "send packet length is:", str(my_length))
            # time.sleep(1)

            start = my_num * l

            for i in range(int(start), int(start) + int(my_length)):
                msg = b"RECEIVE" + b"/ljj/" + packets[i] + b"/ljj/" + str(my_num).encode() + b"/ljj/" + str(my_length).encode()
                self.__send__(msg, frm)

            # print(self.name, "send file")
        # elif msg.split()[0] == "GIVE":
        #     length = round(float(msg.split()[1]))
        #     pos = int(msg.split()[2])
        #
        #     for idx in range(length):
        #         data_fragment, frm = self.__recv__()
        #         self.downloaded_file[pos] += data_fragment
        #         self.already_downloaded += 1
        #         print("%s receive %d" % (self.name, idx))
            # self.active = False
        elif msg.split(b"/ljj/")[0] == b"RECEIVE":
            # print(self.name, "receive from", frm)
            data_fragment = msg.split(b"/ljj/")[1]
            pos = int(msg.split(b"/ljj/")[2])
            self.downloaded_file[pos] += data_fragment
            self.already_downloaded += 1

        elif msg.split(b":")[0] == b"LIST":
            msg = msg.decode()
            self.file_length = int(msg.split(":")[1])
            lst = msg.split(":")[2]
            who_have = ast.literal_eval(lst)  # it is a list of tuples. eg: [('abc', 1), ('bcd', 2)]
            print(self.name, "knows who have it:", who_have)
            print()
            self.target_address = who_have  # it is a list of tuples. eg: [('abc', 1), ('bcd', 2)]
            self.target_address_get = 1

    def alwaysListen(self):
        while True:
            self.listen()


if __name__ == '__main__':
    pass
