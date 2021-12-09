from Proxy import Proxy
import hashlib
import ast

class PClient:
    def __init__(self, tracker_addr: (str, int), proxy=None, port=None, upload_rate=0, download_rate=0):
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = Proxy(upload_rate, download_rate, port)  # Do not modify this line!
        self.tracker = tracker_addr
        """
        Start your additional code below!
        """

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

    def register(self, file_path: str):
        """
        Share a file in P2P network
        :param file_path: The path to be shared, such as "./alice.txt"
        :return: fid, which is a unique identification of the shared file and can be used by other PClients to
                 download this file, such as a hash code of it
        """
        fid = None
        """
        Start your code below!
        """

        md5 = hashlib.md5()
        md5.update(file_path)
        fid = md5.hexdigest()  # fid 变成hash码
        msg = "REGISTER: " + file_path
        self.proxy.sendto(msg, self.tracker)

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
        data = None
        """
        Start your code below!
        """

        msg = "QUERY: " + fid
        self.proxy.sendto(msg, self.tracker)

        response = self.proxy.recvfrom(timeout=None)
        response = response.decode()  # it is a string. eg: [("abc", 1), ("bcd", 2)]
        response = ast.literal_eval(response)  # it is a list of tuples. eg: [('abc', 1), ('bcd', 2)]
        target_address = response[0]

        # TODO: 去找上面的target_address，下载fid代表的文件
        # 怎么凭加密后的fid找到对方的文件？

        """
        End of your code
        """
        return data

    def cancel(self, fid):
        """
        Stop sharing a specific file, others should be unable to get this file from this client any more
        :param fid: the unique identification of the file to be canceled register on the Tracker
        :return: You can design as your need
        """

        msg = "CANCEL: " + fid
        self.proxy.sendto(msg, self.tracker)

        """
        End of your code
        """

    def close(self):
        """
        Completely stop the client, this client will be unable to share or download files any more
        :return: You can design as your need
        """

        # 这里已经有proxy.close了，似乎可以不写cancel操作？

        """
        End of your code
        """
        self.proxy.close()


if __name__ == '__main__':
    pass
