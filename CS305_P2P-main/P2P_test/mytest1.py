from PClient import PClient
from threading import Thread

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    A = PClient(tracker_address, upload_rate=100, download_rate=100000, name="A")
    B = PClient(tracker_address, upload_rate=100000, download_rate=1000, name="B")
    C = PClient(tracker_address, upload_rate=100000, download_rate=50000, name="C")
    D = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="D")

    fid = A.register("../test_files/alice.txt")

    thread1 = Thread(target=B.download, args=fid)
    thread2 = Thread(target=C.download, args=fid)
    thread3 = Thread(target=D.download, args=fid)

    thread1.start()
    thread2.start()
    thread3.start()

