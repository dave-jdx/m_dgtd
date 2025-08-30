import os
fname="c:/test/t.2.txt"
# print(os.path.dirname(fname))
# print(os.path.basename(fname).split(".")[0])
file_name = "example.txt"
filename, extension = os.path.splitext(os.path.basename(fname))
name_without_extension = filename[:len(filename) - len(extension)]
print(filename,extension,name_without_extension)

my_array = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

# 获取索引为1的元组的最小值和最大值
index = 1
tuple_values = [t[index] for t in my_array]  # 获取每个元组在指定索引位置的值
min_value = min(tuple_values)
max_value = max(tuple_values)

print(min_value)  # 输出 2
print(max_value)  # 输出 8

dic={1:"t1",2:"t2"}
del dic[2]
if(1 in dic):
    print(dic)