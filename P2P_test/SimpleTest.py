from PClient import PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B join the network
    A = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="A")
    B = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="B")
    # A register a file and B download it
    fid = A.register("../test_files/alice.txt")
    data1 = B.download(fid)
    print("data1 =", data1)
    # A cancel the register of the file
    A.close()
    # C join the network and download the file from B
    C = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="C")
    data2 = C.download(fid)
    print("data1 =", data1)
    print("data2 =", data2)
    if data1 == data2:
        print("Success!")
        print(data1)
    else:
        raise RuntimeError

    B.close()
    C.close()
