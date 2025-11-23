#   有序  允许重复  不可修改  可混装
from operator import index

tuple1 = (1)
print(type(tuple1))
#一个元素的元组必须带逗号
tuple2 = (1,)
print(type(tuple2))
#空元组
tuple3 = ()
print(type(tuple3))

tuple4 = (1,2,3,4,5,"kkk",34.5,1)
print(type(tuple4))
print(tuple4)
print(tuple4[1])
print(tuple4[-1])
#获取下标
print(tuple4.index(1))
#获取出现的个数
print(tuple4.count("kkk"))
#获取长度
print(len(tuple4))


list1 = [1,2,3,4,5]
tuple5 = (1,2,3,list1)
print(tuple5)
list1.append(6)
print(tuple5)

#元组不可以改
# tuple5[1] = 1

list1 = [9,10]    #这里元组存的是新的list1的引用      这样赋值相当于list1指向了新的引用   而元组中存的是旧的元组引用
print(tuple5)    #元组不会修改
print(list1)     #列表被重新赋值新的引用
# tuple5[3] = [7,8]  #新的引用


print("-"*20)
index = 0
while index < len(tuple5):
    element = tuple5[index]
    if isinstance(element, list):
        for list_item in element:
            print(list_item)
    else:
        print(element)
    index += 1


for item in tuple5:
    if isinstance(item, list):
        for list_item in item:
            print(list_item)
    else:
        print(item)

