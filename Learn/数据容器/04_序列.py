#切片  列表  元组  字符串  都支持切片操作
#切片：从一个序列中取出一个子序列
#操作不会影响序列本身  而是得到一个新的序列
#语法：序列[起始下标:结束下标:步长]    包含起始下标  不包含结束下标   步长默认是1   跳过的个数是步长-1
my_list = [1,2,3,4,5,6,7,8,9]
new_list = my_list[1:4]
print(new_list)
new_list1 = my_list[:]     #取所有元素
print(new_list1)
new_list2 = my_list[::2]   #步长是2  跳一个再取
print(new_list2)
new_list3 = my_list[:4:2]   #起始0  结束4  步长2 跳一个再取
print(new_list3)
new_list4 = my_list[::-1]   #步长为负数 则倒着取
print(new_list4)
new_list5 = my_list[3:1:-1]
print(new_list5)

#我想取出来3 6 9
new_list6 = my_list[::2]
print(new_list6)
