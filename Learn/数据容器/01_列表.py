#有序的   允许重复   可修改   可混装
list1 =[1,2,3,4,5,6,6,6,6,6]
list2 = ["1","2","3","4","5"]
list3 = ['1','2','3','4','5']
list4 = [1.1,2.2,3.3,4.4,5.5]
list5 = [1,2,3,'4',"5",6.7]
list6 = [list1,list2,list3,list4,list5]
print("-"*20)

# print(type(list1))
# print(list1)
# print(list2)
# print(list3)
# print(list4)
# print(list5)
# print(list6)
# #正向下标
# print(list1[0])
# print(list6[0][1])
# print(list1[0])
# print(list2[1])
# print(type(list1[0]))
# print(type(list2[1]))
# print(type(list6[1]))
# #反向下标
# print(list1[-1])
# print(list2[-2])
# print(list6[-3][-3])


print("-"*20)

list7 = [1,2,3,"jkjkj","iojshjia","666"]
#列表操作方法
#查找元素下标
print(list7.index(1))
#判断元素是否存在
print("666" in list7)
#修改指定元素下标值
list7[0]  = "111"
print(list7)
#在指定下标插入
list7.insert(2,"222")
print(list7)
list7.insert(-2,"22442")
print(list7)
list7.insert(10,"8888")
print(list7)
#在尾部追加一个
list7.append("jjj")
print(list7)
#在尾部追加一批数据  追加列表
list8 = [8,9]
list7.extend(list8)
print(list7)
#删除元素  返回删除元素 根据下标
print(list7.pop(-1))
print(list7)
#删除元素
del list7[0]
print(list7)

#删除第一个匹配项   不存在报错
list7.append("jjj")
list7.append("jjj")
list7.remove("jjj")
print(list7)
#清空列表
# list7.clear()
# list7 = []
#统计列表长度
print(len(list7))
#统计某元素在列表中出现的次数
print(list7.count("jjj"))



print("-"*20)

#遍历列表
index = 0
while index < len(list7):
    print(list7[index])
    index += 1

print("-"*20)

for i in list7:
    print(i)