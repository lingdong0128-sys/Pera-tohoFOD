import os
#未完成
# 设定目标文件夹名称
target_folder = 'csv/characters'
# 设定要添加的内容
append_text = '基础,钱,0'

def add_line_to_csv(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误：找不到文件夹 '{folder_path}'")
        return

    count = 0
    # 遍历文件夹及所有子目录
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                
                try:
                    # 以追加模式打开文件 (encoding='utf-8' 根据你的文件实际编码调整，通常是 utf-8 或 gb18030)
                    with open(file_path, 'r+', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 如果文件末尾没有换行符，先加一个换行符，防止拼接在最后一行数据后面
                        prefix = ""
                        if content and not content.endswith('\n'):
                            prefix = "\n"
                        
                        # 移动指针到文件末尾进行写入
                        f.seek(0, 2) 
                        f.write(f"{prefix}{append_text}\n")
                        
                    print(f"已处理: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"无法处理文件 {file_path}: {e}")

    print(f"\n完成！共修改了 {count} 个 CSV 文件。")

if __name__ == '__main__':
    add_line_to_csv(target_folder)