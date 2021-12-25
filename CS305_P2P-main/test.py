import re
# test = {"A":[("A",True),("b",True)]}
# for c in test["A"]:
#     if c[1] is True:
#         print(c)

# str = ","
# seq = ["a", "b", "c"]# 字符串序列
# print(str.join( seq ))


# result = ["A","B","C","D"]
# print("LIST: " + "[%s]" % (", ".join(result)))


# print(re.search("www","lkklkwww.sdsd.www").span())

test = {"fid":[("A",True),("B",True)]}
print(test["fid"][1][0])