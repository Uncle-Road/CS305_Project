from PClient import PClient

tracker_address = ("127.0.0.1", 10086)

if __name__ == '__main__':
    # A,B,C join the network
    A = PClient(tracker_address, upload_rate=100000, download_rate=100000, name='A')
    B = PClient(tracker_address, upload_rate=100000, download_rate=100000, name='B')

    # A register a file and B register a file
    fid = A.register("../test_files/alice.txt")
    fid2 = B.register("../test_files/test.txt")

    C = PClient(tracker_address, upload_rate=100000, download_rate=100000, name="C")
    # C download both two file
    data1 = C.download(fid)
    data2 = C.download(fid2)

    print(C.registered_fid)

    # A,B cancel the register of the file
    A.close()
    B.close()

    # judge
    with open("../test_files/alice.txt", "rb") as bg:
        bs = bg.read()
        if  data1 != bs:
            raise Exception("Downloaded file is different with the original one")

    with open("../test_files/test.txt", "rb") as bg:
        bs = bg.read()
        if data2 != bs:
            raise Exception("Downloaded file is different with the original one")

    print("Success!")
    C.close()
