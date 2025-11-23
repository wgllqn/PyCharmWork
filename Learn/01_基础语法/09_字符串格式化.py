
name = "荒"
numbers = 2.5
parent_name = "柳树"
#s不能为大写  占位符和参数必须一致  类型必须一致
print("姓名"+ name + "独断万古"+str(numbers)+"年")
print("姓名%s" % name)
print("姓名%s,独断万古%s年,杀到无人称尊,师傅%s" % (name,numbers,parent_name))
print("姓名%s,独断万古%s年,杀到无人称尊,师傅%s" % (name,numbers,parent_name))
print("姓名%s,独断万古%d年,杀到无人称尊,师傅%s" % (name,numbers,parent_name))
print("姓名%s,独断万古%f年,杀到无人称尊,师傅%s" % (name,numbers,parent_name))

"""
m.n  m是宽度   m小于数据本身不生效   大于数据长度前面补空格    n是控制小数位
对于字符串类型.n不生效   对于整型 .n不生效   对于浮点型  .n会四舍五入
"""
money = 100
name = "韩立"
wages = 88.889
age = 100002.678
message = "大家好,我是%3.2s,年龄%8.9d,我的钱包是%.2f元,工资%.2f元,发完工资之后合计%9.3f元" % (name,age,money,wages,money+wages)
print(message)


name =500
country = "美国"
money = 100.257
#10.2f  控制宽度和精度   10.2e科学计数法  10.2f  整数不能有小数     g智能切换   自动省略小数末尾0
message = f"我是纳斯达克标普{name:10d},我是{country}的，我的市值{money:10.6f}W"
message1 = f"我是纳斯达克标普{name:10d},我是{country}的，我的市值{money:10.6e}W"
message2 = f"我是纳斯达克标普{name:10d},我是{country}的，我的市值{money:10.6g}W"

print(message)
print(message1)
print(message2)




print("结果%d" %(1*1))
print(f"结果{1*1}")
print("结果%s" % type(1))

