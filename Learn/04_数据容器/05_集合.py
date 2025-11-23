# 不可重复   无序  可混合   可以修改  可修改
#空集合
set1 = set()
set2 = {1,2,3,4,5,6}
print(set1,type(set1))
print(set2,type(set2))
set3 = {1,1,1,2,'abc',"ABC",45,True,666,666,555,1}
print(set3)
#无法使用下标访问
# print(set3[2])
#添加元素
set3.add("ADD")
print(set3)
#指定删除
set3.remove("ADD")
print(set3)
#随机删除并返回
print(set3.pop())
print(set3)
#清空
set3.clear()
print(set3)
#求两个集合差集  得到新集合  原有集合不变
set4 = {1,2,3,4,5,6}
set5 = {1,2,3,4,5,6,7,8,9,10}
#set4里面set5里面没有的
set6 = set4.difference(set5)
print(set4)
print(set5)
print("set4里面有set5里面没有的",set6)
set7 = set5.difference(set4)
print("set5里面有set4里面没有的",set7)


#两个集合差集消除  会修改原有集合的值
print(set4)
print(set5)
# set4.difference_update(set5)
# print("在set4里面删除和set5相同的元素")
# print(set4)
# print(set5)
set5.difference_update(set4)
print("在set5里面删除和set4相同的元素")
print(set4)
print(set5)

#合并新集合  原有集合不变
set8 = {1,2,3,4,5,6,7,8,9,10}
set9 = {1,2,3,4,5,6,7,8,9,10,11}
set10 = set8.union(set9)
print(set10)
#统计元素数量
print(len(set10))


#只能使用for  循环不能使用while循环    没有顺序输出
for item in set10:
    print(item)
