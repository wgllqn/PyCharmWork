#轮询  遍历     对一批内容进行逐个处理
#
# for i  in "123":
#     print(i)

# count = 0
# for i in "gdhsjhaashdjhasdhjsdjajsdaajfaksderoaqa":
#     if i == "a":
#         count += 1
# print("a的个数",count)

# count = 0
# for i in range(1,10):
#     if i % 2 == 0:
#         count += 1
#         print(i)
# print("10以内2的倍数的个数",count)


#5-10 步长为2
# for i in range(5,10,2):
#     print(i, end=' ')

#循环5次
# for i in range(5):
#     print(i, end=' ')


#age 属于for内部  外部不可以访问  但是python中不会报错   不推荐使用  age属于局部变量
#右边缩进访问左边缩进 OK    左边缩进访问右边缩进不可以
# num = 100
# for num in range(1, 11):
#     print(num)
#     age = 30
#
# print(age)
# print(num)



# for num in range(100):
#     print("今天是第%d天" % num);
#     for num2 in range(10):
#         print("第%d朵花"%num2);


# for row in range(1,10):
#     for col in range(1,row+1):
#         print(f"{col}*{row}={col*row}",end="\t")
#     print()
#


#循环中断   就近原则
#1.跳过本次循环  进行下一次循环
# for i in range(10):
#     if i == 5:
#         continue
#     print(i)
#结束循环
# for i in range(10):
#     if i == 5:
#         break
#     print(i)


