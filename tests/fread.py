import os

def get_folder_size(folder_path):
    total_size = 0
    # 遍历文件夹下的每个文件和文件夹
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            # 累加文件的大小
            total_size += os.path.getsize(file_path)
    return total_size

def print_subfolder_sizes(parent_folder):
    # 列出所有一级文件夹
    for item in os.listdir(parent_folder):
        item_path = os.path.join(parent_folder, item)
        if os.path.isdir(item_path):  # 仅处理文件夹
            folder_size = get_folder_size(item_path)
    
            print(f"文件夹: {item}, 大小: {folder_size / (1024 * 1024):.2f} MB")
def print_subfolder_sizes_sorted(parent_folder):
    folder_sizes = []
    
    # 列出所有一级文件夹
    for item in os.listdir(parent_folder):
        item_path = os.path.join(parent_folder, item)
        if os.path.isdir(item_path):  # 仅处理文件夹
            folder_size = get_folder_size(item_path)
            # 将文件夹名和文件夹大小以元组的形式存入列表
            folder_sizes.append((item, folder_size))
    
    # 按大小倒序排序
    sorted_folders = sorted(folder_sizes, key=lambda x: x[1], reverse=True)
    
    # 打印结果
    for folder, size in sorted_folders:
        print(f"文件夹: {folder}, 大小: {size / (1024 * 1024):.2f} MB")

# 示例使用
parent_folder = 'C:/Users/30381_/AppData/Local'
print_subfolder_sizes_sorted(parent_folder)