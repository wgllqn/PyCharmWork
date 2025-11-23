
def funA(name,age,gender):
    print(name,age,gender);

#位置参数  必须按照顺序
funA("张三",12,"男")

#关键字传参  形参 = 实参
funA(age = 12, name = "小美",gender = "女")
#混用  位置参数必须在关键字参数左侧
funA("小李",gender = "男", age = 16)
#报错 位置参数必须在关键字参数左侧
# funA(name = "小李",gender = "男", "15")


#缺省参数 也叫默认参数
def funB(name,age,gender = "女"):
    print(name,age,gender);

#不提供以默认值为主
funB("小王",15)
#传了以传的为主
funB("小强",18,"男")

#报错 默认值参数  必须在无默认值参数右侧
# def funB(name,age = 12 , gender):
#     print(name,age,gender);




#不定长参数  都使用元组接收
def funC(name,*args):
    print(name,args);
    for arg in args:
        print(arg);

funC("数据列表",2,3,4,5)
#以顺序为主
funC(2,3,4,5,"数据列表")
#报错  不定长参数 以顺序为准 关键字参数位置必须正确
# funC(2,3,4,5,name = "数据列表")
#报错 位置参数必须在关键字参数左侧
# funC(name = 2,3,4,5)

# count 需要通过关键字传入  否则 默认全被不定长参数接收
def funD(name,*args,count):
    print(name,args,count);
    for arg in args:
        print(arg);

funD("数据列表",2,3,4,5,6, count=5)
funD("数据列表",2,3,4,5,6,5)
