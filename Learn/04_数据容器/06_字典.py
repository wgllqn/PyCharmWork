#key:value对  可修改
#key 不能重复 key不可以是字典  一般使用字符串和数字
# value可以任意类型   可以通过key找到对应value
#空字典
dict1 = {}
dict2 = dict()
print(dict1,type(dict1))
print(dict2,type(dict2))
#
dict3 = {"哈哈":1,2:2,"一班":['张三','王五'],4:("你好",2,66),5:{"ddd","frf","okl"},6:6}
print(dict3)
#没有下标
# print(dict3[0])
#可以通过key获取value
print(dict3["一班"])
#key不可以重复  不会报错   后一个key会覆盖相同的前一个key
dict4 = {"哈哈":1,2:2,"一班":['张三','王五'],4:("你好",2,66),5:{"ddd","frf","okl"},"二班":{"李四":98,"六二":99},666:666,666:66676}
print(dict4)
print(dict4["二班"])
#新增和修改元素
dict4["add"] = 7432
dict4["哈哈"] = 345
print(dict4)
#删除某个key 并返回对应的value
print("删除",dict4.pop(4))
print(dict4)
#清空
dict4.clear()
dict4 = {}
print(dict4)

#获取所有的keys
dict5 = {"哈哈":1,2:2,"一班":['张三','王五'],4:("你好",2,66),5:{"ddd","frf","okl"},"二班":{"李四":98,"六二":99},666:666,666:66676}
print(dict5.keys())  #可以被遍历

#遍历字典1
keys1 = dict5.keys()
for key in keys1:
    print(f"key{key}:{dict5[key]}")
print("-"*10)
#遍历字典2
for key in dict5:
    print(f"key{key}:{dict5[key]}")






