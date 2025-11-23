def say_hi():
    print("大家好，我是渣渣辉")
    return None

result = say_hi()
print(result)
print(type(result))

# None 默认是False
if not result:
    print("hello")

age = None



#多返回值
def funA():
    return 1,2,3
#将返回值自动解包为元组
x,y,z = funA()
print(x,y,z)

x = funA();
print(x,type(x))
