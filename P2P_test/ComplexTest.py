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

    clients = [B, C, D, E]
    # A register a file and B download it
    fid = A.register("../test_files/bg.png")
    threads = []
    files = {}


    # function for download and save
    def download(node, index):
        files[index] = node.download(fid)
        # print(node.name, "foe:",files[index])


    time_start = time.time_ns()
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
    # start download in parallel
    for t in threads:
        t.start()
    # wait for finish
    for t in threads:
        t.join()
    # check the downloaded files
    with open("../test_files/bg.png", 'rb') as bg:
        bs = bg.read()
        # print("bs: ", bs)'
        print("read files")
        for i in files:
            # print(type(files[i].decode))
            # print("look here!!!!!!!", files[i])
            # f = open("foo{}.txt".format(str(i)),'w')
            # f.write(str(files[i]))
            # f.close()
            if files[i] == bs:
                print(i, "success")
            if files[i] != bs:
                # raise Exception("Downloaded file is different with the original one")
                print(i, "fail")
                # print(files[i])
                pass

    print("finish!!!!!!!")
    # B, C, D, E has completed the download of file
    threads.clear()
    F = PClient(tracker_address, upload_rate=50000, download_rate=100000, name="F")
    G = PClient(tracker_address, upload_rate=100000, download_rate=60000, name="G")
    # F, G join the network
    clients = [F, G]
    for i, client in enumerate(clients):
        threads.append(Thread(target=download, args=(client, i)))
        # download(client, i)
    for t in threads:
        t.start()

    # A exits
    # time.sleep(20)
    # A.cancel(fid)
    #
    # # B exits
    # time.sleep(10)
    # B.close()
    #
    # # D exits
    # time.sleep(30)
    # D.close()
    for t in threads:
        t.join()
    for i in files:
        if files[i] != bs:
            raise Exception("Downloaded file is different with the original one")
            # print("different!")
    print("SUCCESS")

    A.close()
    C.close()
    E.close()
    F.close()
    G.close()
    print((time.time_ns() - time_start) * 1e-9)
