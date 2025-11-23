#
# age = 1000
# def funA():
#     num = 100
#     print(age)
#     return num
# print(funA())
# # print(num)  #num只存在FunA的作用域中  局部变量
# print(age)   #age全局变量    整个文件都可以访问
#
#


# num1 = 1000
# def funB():
#     num1 = 100
#     return num1
# print(funB())
# print(num1)

#如果想修改num1的值
def funC():
    global num1    #访问全局变量  修改全局变量
    num1 = 100
    return num1
print(funC())
print(num1)