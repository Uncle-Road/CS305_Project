from PClient import PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B join the network
    print("0")
    A = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="A")
    print("1")
    B = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="B")
    print("2")
    # A register a file and B download it
    fid = A.register("../test_files/alice.txt")
    print("3")
    data1 = B.download(fid)
    print("4")
    # A cancel the register of the file
    A.close()
    print("5")
    # C join the network and download the file from B
    C = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="C")
    print("6")
    data2 = C.download(fid)
    print("7")
    if data1 == data2:
        print("Success!")
    else:
        raise RuntimeError

    B.close()
    C.close()
