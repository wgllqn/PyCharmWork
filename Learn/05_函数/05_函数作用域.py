money = 10000
def fun_menu():
    print(f"{name}你好请输入你要办理的业务:")
    print("1.查询余额")
    print("2.取钱")
    print("3.存钱")
    print("4.退出")
    return int(input())

def sub_money():
    sub = int(input("请输入你要取的金额"))
    global money
    if money < sub:
        print(f"你的余额不足{sub}元")
    else:
        money -= sub
    search_money()

def add_money():
    add = int(input("请输入你要存的金额"))
    global money
    money += add
    search_money()


def search_money():
    print(f"你的余额是{money}")

name = input("请输入你的姓名")
while True:
    ye_wu  = fun_menu()
    if ye_wu == 1:
        search_money()
    elif ye_wu == 2:
         sub_money()
    elif ye_wu == 3:
        add_money()
    else:
        print("欢迎下次光临！")
        break





