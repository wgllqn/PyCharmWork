#只存储字符   不可修改
str1 = "I Love You"
print(str1[0])
print(str1[-5])
#不可修改
# str1[0] = 'H'

#可以重新赋值
str1 = "   Hello World !     |||"
print(str1)
#查找下标
print(str1.index("H"))
#字符串替换   不是修改本身  而是生成一个新的
str2 = str1.replace("H","I")
print(str1)   #不能修改
print(str2)   #可以重新赋值

#分割  得到新的列表
str3 = str1.split(" ")
print(str3)

#去除前后空格
str4 = str1.strip()
print(str4)
#去除前后指定字符
str5 = str1.strip("|")
print(str5)
str6 = str1.replace("|","")
print(str6)

#统计个数
str7 = str1.count("l")
print(str7)

#统计长度
print(len(str1))



index = 0
while index < len(str1):
    str8 = str1[index]
    print(str8, end="")
    index += 1

for item in str1:
    print(item, end="")