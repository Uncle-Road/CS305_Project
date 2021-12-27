from PClient import PClient
from threading import Thread

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    A = PClient(tracker_address, upload_rate=1000000, download_rate=100000, name="A")
    B = PClient(tracker_address, upload_rate=100000, download_rate=10000000, name="B")
    C = PClient(tracker_address, upload_rate=100000, download_rate=500000000, name="C")
    D = PClient(tracker_address, upload_rate=100000, download_rate=1000000000, name="D")

    fid = A.register("../test_files/alice.txt")
    threads = []
    files = {}
    def download(node, index):
        files[index] = node.download(fid)
        # print(node.name, "foe:",files[ind
    clients = [B, C, D]
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
    for t in threads:
        t.start()
    # wait for finish
    for t in threads:
        t.join()
