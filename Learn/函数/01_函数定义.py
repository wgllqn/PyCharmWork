#组织好的  可重复使用   实现特定功能
# name = "你好"
# length = len(name)
# print(length)
from Demos.RegRestoreKey import my_sid

#
# length = 0
# name = "hgjgha"
# for i in name:
#     length += 1
# print(length)


#定义一个自己的函数
def my_length(data):
    length = 0
    for i in data:
        length += 1
    return length
print(my_length("jihkh"))