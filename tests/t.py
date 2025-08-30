data = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]

# 使用 sorted 函数进行排序
sorted_data = sorted(data, key=lambda x: (x[0], x[1]))

# 打印排序后的结果
print(sorted_data)