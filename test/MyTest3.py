import time
from threading import Thread

from PClient import PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B,C,D,E join the network
    A = PClient(tracker_address, upload_rate=200000, download_rate=50000, name="A")
    B = PClient(tracker_address, upload_rate=50000, download_rate=100000, name="B")
    C = PClient(tracker_address, upload_rate=100000, download_rate=50000, name="C")
    D = PClient(tracker_address, upload_rate=70000, download_rate=40000, name="D")
    E = PClient(tracker_address, upload_rate=200000, download_rate=700000, name="E")
    # A register a file and B download it
    fid = A.register("../test_files/alice.txt")
    threads = []
    files = {}


    # function for download and save
    def download(node, index):
        files[index] = node.download(fid)
        # print(node.name,"fooe,",files[index])
        # print(node.name,"fooe",index)

    B.register("../test_files/alice.txt")
    C.register("../test_files/alice.txt")
    D.register("../test_files/alice.txt")
    E.register("../test_files/alice.txt")

    with open("../test_files/alice.txt", "rb") as bg:
        bs = bg.read()

    F = PClient(tracker_address, upload_rate=50000, download_rate=100000, name="F")
    G = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="G")
    # F, G join the network
    clients = [F, G]
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
    for t in threads:
        t.start()

    # A exits
    # time.sleep(8)
    # A.cancel(fid)
    #
    # B exits
    time.sleep(6)
    C.close()

    # D exits
    time.sleep(8)
    D.close()

    for t in threads:
        t.join()
    for i in files:
        if files[i] != bs:
            raise Exception("Downloaded file is different with the original one")
            # print("different!")
    print("SUCCESS")

    A.close()
    B.close()
    E.close()
    F.close()
    G.close()

    threads.clear()
