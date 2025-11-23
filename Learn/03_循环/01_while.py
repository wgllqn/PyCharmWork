#有循环因子  自行控制循环条件

#对小美表白10
# i = 0
# while i < 10:
#     i +=1
#     print("小美 %d次" % i)

## 99乘法表   外层循环控制行数 和换行    内层控制行内每列自增
row = 1
while row <= 9:
    col = 1
    while col <= row:
        print(f"{col}*{row}={col * row}",end="\t")
        col += 1
    row += 1
    print()
