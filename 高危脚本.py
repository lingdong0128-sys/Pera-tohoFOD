import os
import sys

# ================= 配置区域 =================
MAPPING_FILE = '变量名-中文.txt'  # 你的映射文件路径
# 不需要遍历的文件夹
IGNORE_DIRS = {'.git', '__pycache__', 'venv', '.idea', '.vscode', '_internal', 'build', 'dist'}
# 不需要遍历的文件
IGNORE_FILES = {MAPPING_FILE, os.path.basename(__file__)}
# 允许修改内容的文件后缀 (只修改文本代码，不修改图片内容以免损坏)
TEXT_EXTENSIONS = {
    '.py', '.csv', '.json', '.txt', '.md', '.erb', 
    '.xml', '.yaml', '.ini', '.bat', '.sh'
}
# ===========================================

def load_mapping(mapping_file):
    """读取映射文件，返回按键长度降序排列的字典"""
    mapping = {}
    if not os.path.exists(mapping_file):
        print(f"❌ 错误：找不到映射文件 '{mapping_file}'")
        return None

    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '-' not in line:
                    continue
                
                parts = line.split('-', 1)
                old_text = parts[0].strip()
                new_text = parts[1].strip()
                
                if old_text and old_text != new_text:
                    mapping[old_text] = new_text
    except Exception as e:
        print(f"❌ 读取映射文件失败: {e}")
        return None
    
    # 关键：按旧名称的长度降序排列
    # 防止短词替换了长词的一部分（例如防止先替换了"Name"，导致"NameList"变成"名字List"）
    return dict(sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True))

def is_text_file(filename):
    """判断是否为文本文件"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in TEXT_EXTENSIONS

def process_content(file_path, replacements):
    """步骤1：替换文件内容"""
    if not is_text_file(file_path):
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for old, new in replacements.items():
            if old in new_content:
                new_content = new_content.replace(old, new)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except UnicodeDecodeError:
        print(f"⚠️  [跳过内容] 非UTF-8编码: {file_path}")
    except Exception as e:
        print(f"❌ [读取出错] {file_path}: {e}")
    
    return False

def process_filename(root, filename, replacements):
    """步骤2：重命名文件"""
    new_filename = filename
    for old, new in replacements.items():
        if old in new_filename:
            new_filename = new_filename.replace(old, new)
    
    if new_filename != filename:
        old_path = os.path.join(root, filename)
        new_path = os.path.join(root, new_filename)
        
        # 防止覆盖已存在的文件
        if os.path.exists(new_path):
            print(f"⚠️  [重命名跳过] 目标文件已存在: {new_filename}")
            return False
            
        try:
            os.rename(old_path, new_path)
            return new_filename # 返回新名字供记录
        except Exception as e:
            print(f"❌ [重命名失败] {filename} -> {new_filename}: {e}")
    
    return None

def main():
    print("⚡ Pera 批量替换与重命名工具")
    print("⚠️  警告：此操作不可逆！")
    print(f"⚠️  将读取 {MAPPING_FILE} 并对当前目录所有文件进行：")
    print("    1. 内容替换")
    print("    2. 文件名替换")
    
    confirm = input("\n请输入 'y' 确认已备份并开始执行: ")
    if confirm.lower() != 'y':
        print("操作已取消。")
        return

    replacements = load_mapping(MAPPING_FILE)
    if not replacements:
        return

    print(f"\n加载了 {len(replacements)} 条替换规则，开始处理...\n")

    content_change_count = 0
    rename_count = 0

    # os.walk 遍历
    # topdown=False 意味着先遍历子目录，这对于重命名文件夹更安全（虽然本脚本只重命名文件）
    for root, dirs, files in os.walk('.', topdown=False):
        # 过滤忽略的目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in files:
            if filename in IGNORE_FILES:
                continue

            file_path = os.path.join(root, filename)

            # 1. 先替换内容 (使用旧文件名打开)
            if process_content(file_path, replacements):
                print(f"📝 [内容修改] {file_path}")
                content_change_count += 1

            # 2. 再重命名文件
            new_name = process_filename(root, filename, replacements)
            if new_name:
                print(f"♻️  [文件重命名] {filename} -> {new_name}")
                rename_count += 1

    print("-" * 40)
    print(f"✅ 处理完成！")
    print(f"📝 修改内容的文件数: {content_change_count}")
    print(f"♻️  重命名的文件数: {rename_count}")

if __name__ == "__main__":
    main()