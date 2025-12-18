import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os


class ERBConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pera 口上搬迁助手 v3.2 (缩进优化版)")
        self.root.geometry("1200x800")

        # 变量
        self.source_file_path = ""
        self.converted_lines = []
        self.indent_level = 0
        self.current_function_name = ""
        self.func_name_original = ""

        # [修改] 增加 SELECTCASE 状态控制
        self.in_select_case = False
        self.select_variable = ""
        self.is_first_case = False  # 标记是否是第一个 CASE

        self.setup_ui()

    def setup_ui(self):
        # ... (UI 代码保持不变，省略以节省空间，直接复制之前的 UI 部分即可) ...
        # 顶部操作栏
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill=tk.X, padx=10)

        btn_load = tk.Button(frame_top, text="1. 加载 ERB 文件 (.erb)",
                             command=self.load_file, bg="#e1f5fe")
        btn_load.pack(side=tk.LEFT, padx=5)

        self.lbl_file = tk.Label(frame_top, text="未选择文件", fg="gray")
        self.lbl_file.pack(side=tk.LEFT, padx=5)

        btn_convert = tk.Button(frame_top, text="2. 开始转换",
                                command=self.start_conversion, bg="#c8e6c9")
        btn_convert.pack(side=tk.RIGHT, padx=5)

        # 中间文本区域 (左右分栏)
        frame_mid = tk.Frame(self.root)
        frame_mid.pack(fill=tk.BOTH, expand=True, padx=10)

        # 左侧：源文件预览
        frame_left = tk.Frame(frame_mid)
        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(frame_left, text="ERB 源文件预览:").pack(anchor=tk.W)
        self.txt_source = scrolledtext.ScrolledText(
            frame_left, height=30, width=50)
        self.txt_source.pack(fill=tk.BOTH, expand=True)

        # 右侧：转换结果
        frame_right = tk.Frame(frame_mid)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(frame_right, text="Python 转换结果 (可编辑):").pack(anchor=tk.W)
        self.txt_result = scrolledtext.ScrolledText(
            frame_right, height=30, width=50, bg="#fcfcfc")
        self.txt_result.pack(fill=tk.BOTH, expand=True)

        # 底部保存
        btn_save = tk.Button(self.root, text="3. 保存为 .py 事件文件",
                             command=self.save_file, bg="#fff9c4", height=2)
        btn_save.pack(fill=tk.X, padx=10, pady=10)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("ERB Files", "*.erb"), ("All Files", "*.*")])
        if filepath:
            self.source_file_path = filepath
            self.lbl_file.config(text=os.path.basename(filepath))
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self.txt_source.delete(1.0, tk.END)
                self.txt_source.insert(tk.END, content)

    def start_conversion(self):
        if not self.source_file_path:
            messagebox.showwarning("提示", "请先加载文件")
            return

        raw_content = self.txt_source.get(1.0, tk.END).split('\n')
        self.converted_lines = []
        self.indent_level = 0
        self.in_select_case = False
        self.current_function_name = ""

        # 1. 写入文件头 (Imports)
        header = [
            "from utils.era_handler import EraKojoHandler",
            "import random",
            "",
            "# [Pera Converter] 自动生成的文件",
            ""
        ]
        self.converted_lines.extend(header)

        # 2. 逐行分析
        for i, line in enumerate(raw_content):
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            # [关键逻辑] 检测函数定义 @
            if line.startswith('@'):
                self.handle_function_definition(line)
                continue

            # 如果当前没有在函数内，且不是 @ 开头，说明是悬空代码，跳过或注释
            if not self.current_function_name:
                self.add_code(f"# [跳过悬空代码] {line}", force_indent=0)
                continue

            try:
                converted = self.process_line(line)
                if converted:
                    self.add_code(converted)
            except Exception as e:
                self.add_code(f"# [ERROR] 转换出错: {line} | {e}")

        # 更新显示
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.insert(tk.END, "\n".join(self.converted_lines))
        messagebox.showinfo("完成", "转换完成，请检查右侧代码。")

    def handle_function_definition(self, line):
        """
        [修复] 处理 @函数名，使用 self 变量替代 global
        """
        # 1. 提取函数名
        func_name = line[1:].split()[0].strip()

        # 2. 如果之前有函数，先结束它，并添加 trigger
        if self.current_function_name:
            self.add_code("", force_indent=0)
            # [修复] 这里使用 self.func_name_original 获取上一个函数的原名
            self.add_code(
                f"{self.current_function_name}.event_trigger = '{self.func_name_original}'", force_indent=0)
            self.add_code("", force_indent=0)
            self.add_code("# " + "-"*40, force_indent=0)
            self.add_code("", force_indent=0)

        # [修复] 更新当前的原函数名到实例变量
        self.func_name_original = func_name

        # 3. 定义新 Python 函数
        py_func_name = f"event_{func_name}"
        self.current_function_name = py_func_name

        self.add_code(f"def {py_func_name}(this):", force_indent=0)
        self.add_code(f'    """ 原ERB函数: {line} """', force_indent=0)

        # 4. 插入初始化代码
        self.indent_level = 1

        init_code = [
            "# 初始化口上处理器",
            "context = getattr(this, 'current_kojo_context', {})",
            "kojo = EraKojoHandler(this.console, context)",
            "",
            "# 常用变量",
            # 注意：这里加个容错，防止 kojo.MASTER 为空导致报错
            "master_name = '你'",
            "if kojo.MASTER:",
            "    master_name = this.console.init.charaters_key.get(kojo.MASTER, {}).get('全名', '你')",
            "target_name = kojo.NAME",
            "call_name = kojo.CALLNAME", # 确保这一行也有
            "",
            "# 颜色常量",
            "COL_TALK = (255, 255, 255)",
            "COL_DESC = (170, 170, 170)",
            ""
        ]
        for c in init_code:
            self.add_code(c)

    def add_code(self, text, force_indent=None):
        level = self.indent_level if force_indent is None else force_indent
        indent = "    " * level
        self.converted_lines.append(f"{indent}{text}")

    def process_variable(self, text):
        """
        [修复] 增强版变量解析，支持中文键名
        """
        text = text.strip()
        if text == "MASTER":
            return "kojo.MASTER"
        if text == "TARGET":
            return "kojo.TARGET"
        if text == "PLAYER":
            return "kojo.PLAYER"
        if text == "RAND":
            return "kojo.Rand"

        if ':' in text:
            parts = text.split(':')
            var_name = parts[0]

            # 代理属性列表
            proxy_vars = ['BASE', 'ABL', 'TALENT', 'EXP', 'MARK',
                          'CFLAG', 'JUEL', 'TEQUIP', 'PALAM', 'TCVAR', 'EQUIP']

            if var_name in proxy_vars:
                # 情况 1: TALENT:恋慕 -> kojo.TALENT.get('恋慕', 0)
                if len(parts) == 2:
                    key = parts[1]
                    # 只要不是纯数字，就加上引号（除非它已经是变量）
                    if not key.isdigit() and not (key.startswith("'") or key.startswith('"')):
                        # 简单判断：如果是 MASTER/TARGET 等变量不加引号，否则加
                        if key not in ["MASTER", "TARGET", "PLAYER"]:
                            key = f"'{key}'"
                    elif key.isdigit():
                        key = f"'{key}'"  # 数字ID也转字符串key

                    return f"int(kojo.{var_name}.get({key}, 0))"

                # 情况 2: CFLAG:MASTER:31
                elif len(parts) == 3:
                    chara = parts[1]
                    key = parts[2]

                    chara_code = "kojo.TARGET"
                    if chara == "MASTER":
                        chara_code = "kojo.MASTER"
                    elif chara == "TARGET":
                        chara_code = "kojo.TARGET"
                    elif chara == "PLAYER":
                        chara_code = "kojo.PLAYER"
                    elif chara.isdigit():
                        chara_code = f"'{chara}'"

                    if not key.isdigit() and not (key.startswith("'") or key.startswith('"')):
                        key = f"'{key}'"
                    elif key.isdigit():
                        key = f"'{key}'"

                    return f"int(kojo.{var_name}[{chara_code}].get({key}, 0))"

        return text

    def process_line(self, line):
        # 1. 打印
        if line.startswith('PRINT'):
            return self.handle_print(line)

        # 2. 等待
        if line == 'WAIT' or line == 'FORCEWAIT' or line == 'W':
            return "this.console.INPUT() # WAIT"

        # 3. IF / ELSE
        if line.startswith('IF '):
            return self.handle_if(line)
        if line.startswith('ELSEIF '):
            self.indent_level -= 1
            code = self.handle_elseif(line)
            self.indent_level += 1
            return code
        if line == 'ELSE':
            self.indent_level -= 1
            self.add_code("else:")
            self.indent_level += 1
            return None
        if line == 'ENDIF':
            self.indent_level -= 1
            return "# ENDIF"

        # 4. SELECTCASE / CASE / ENDSELECT
        if line.startswith('SELECTCASE '):
            return self.handle_selectcase(line)
        if line.startswith('CASE '):
            return self.handle_case(line)

        if line.startswith('CASEELSE'):
            # CASEELSE 相当于 else
            # 也要先回退一格，退出上一个 elif
            self.indent_level -= 1
            self.add_code("else: # CASEELSE")
            self.indent_level += 1  # 进入 else 块
            return None  # 已经添加了代码，返回 None

        if line == 'ENDSELECT':
            self.in_select_case = False
            # 结束整个 SELECTCASE 结构，回退一格
            # 这一步是退出最后一个 case/else 的 block
            self.indent_level -= 1
            return "# ENDSELECT"

        # 5. CALL
        if line.startswith('CALL '):
            event_name = line[5:].strip()
            return f"this.event_manager.trigger_event('{event_name}', this)"

        # 6. RETURN
        if line.startswith('RETURN'):
            # Python 函数不需要显式 return 0，除非有逻辑需要
            return "return"

        # 7. 复杂/赋值
        if any(x in line for x in ['JUMP', 'GOTO', 'DATALIST', '=']):
            return self.ask_user_action(line, "复杂逻辑/赋值")

        return f"# [未处理] {line}"

    def handle_print(self, line):
        color_var = "COL_TALK"
        if 'D' in line.split(' ')[0]:
            color_var = "COL_DESC"

        content_match = re.match(r'PRINT\w+\s+(.*)', line)
        if not content_match:
            return 'this.console.PRINT("")'

        content = content_match.group(1)
        content = content.replace('%CALLNAME:MASTER%', '{master_name}')
        content = content.replace('%CALLNAME:TARGET%', '{target_name}')
        content = re.sub(r'%(.*?)%', r'{\1}', content)

        has_wait = line.endswith('W') or 'WAIT' in line.split(' ')[0]
        code = f'this.console.PRINT(f"{content}", colors={color_var})'
        if has_wait:
            code += f'\n{"    " * self.indent_level}this.console.INPUT()'
        return code

    def handle_if(self, line):
            condition = line[3:].strip()
            condition = self.replace_era_variables(condition)
            
            if 'GETBIT' in condition:
                condition = re.sub(r'GETBIT\(([^,]+),\s*(\d+)\)', r'((\1 >> \2) & 1)', condition)

            if '=' in condition and not any(x in condition for x in ['==', '!=', '<=', '>=']):
                condition = condition.replace('=', '==')
            
            # [修复] 先添加代码，再增加缩进
            self.add_code(f"if {condition}:")
            self.indent_level += 1
            
            return None # 返回 None

    def handle_elseif(self, line):
            condition = line[7:].strip()
            condition = self.replace_era_variables(condition)
            
            if 'GETBIT' in condition:
                condition = re.sub(r'GETBIT\(([^,]+),\s*(\d+)\)', r'((\1 >> \2) & 1)', condition)
                
            if '=' in condition and not any(x in condition for x in ['==', '!=', '<=', '>=']):
                condition = condition.replace('=', '==')

            # [修复] 先回退，添加代码，再前进
            self.indent_level -= 1
            self.add_code(f"elif {condition}:")
            self.indent_level += 1
            
            return None

    def handle_selectcase(self, line):
        variable = line[11:].strip()

        if 'RAND:' in variable:
            rand_val = variable.split(':')[1]
            py_var = f"kojo.Rand({rand_val})"
        else:
            py_var = self.replace_era_variables(variable)

        self.in_select_case = True
        self.select_variable = f"val_{self.indent_level}"
        self.is_first_case = True

        # [关键] 这一行是赋值，它应该和上一行代码保持同样的缩进
        # 所以我们这里生成的代码，会被 process_line 里的 self.add_code 加上当前的 indent_level
        # 我们不需要手动修改 indent_level
        code = f"{self.select_variable} = {py_var}"
        return code

    def replace_operators(self, text):
        """
        [新增] 将 ERA/C 风格运算符转换为 Python 风格
        """
        # 1. 处理逻辑与 && -> and
        text = text.replace("&&", " and ")

        # 2. 处理逻辑或 || -> or
        text = text.replace("||", " or ")

        # 3. 处理逻辑非 ! -> not
        # 注意：必须使用正则，防止把 != (不等于) 替换成了 not =
        # 含义：匹配一个 !，前提是后面跟着的字符不是 =
        text = re.sub(r'!(?!=)', ' not ', text)

        return text

    def handle_case(self, line):
            value = line[5:].strip()
            
            # 处理列表 CASE 1, 2
            if ',' in value:
                check_code = f"{self.select_variable} in ({value})"
            else:
                if not value.isdigit() and '"' not in value and "RAND" not in value:
                    processed = self.replace_era_variables(value)
                    if processed != value: value = processed
                check_code = f"{self.select_variable} == {value}"

            if self.is_first_case:
                # [修复逻辑]
                # 1. 生成代码
                code = f"if {check_code}:"
                # 2. 立即添加（使用当前的缩进等级，确保和 val_1 = ... 对齐）
                self.add_code(code)
                # 3. 标记结束
                self.is_first_case = False
                # 4. 【最后】才增加缩进，为下一行内容做准备
                self.indent_level += 1
                return None # 告诉 process_line 不要再添加了
            else:
                # 后续分支
                # 1. 先回退一级（退出上一个 if/elif 的内部）
                self.indent_level -= 1
                # 2. 生成代码
                code = f"elif {check_code}:"
                # 3. 添加（此时缩进已回退，和 if 对齐）
                self.add_code(code)
                # 4. 再次增加缩进（进入 elif 的内部）
                self.indent_level += 1
                return None

    def ask_user_action(self, line, reason):
        # ... (保持不变) ...
        dialog = DecisionDialog(self.root, line, reason)
        self.root.wait_window(dialog.top)
        action = dialog.result
        if action == "comment":
            return f"# [TODO: {reason}] {line}"
        elif action == "pass":
            return f"pass # [跳过: {line}]"
        elif action == "manual":
            return f"{dialog.manual_code} # 原文: {line}"
        else:
            return f"# [未处理] {line}"

    def save_file(self):
        # 在保存前，检查是否还有最后一个函数没闭合，补上 trigger
        if self.current_function_name:
            # [修复] 使用 self.func_name_original
            self.converted_lines.append(
                f"{self.current_function_name}.event_trigger = '{self.func_name_original}'")

        code = self.txt_result.get(1.0, tk.END)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            messagebox.showinfo("成功", f"文件已保存至: {filepath}")

    def replace_era_variables(self, text):
        """
        [修改] 综合处理变量和运算符
        """
        # 先处理运算符 (&& -> and)
        text = self.replace_operators(text)

        # 再处理变量 (TALENT:xxx -> kojo...)
        pattern = r'\b([A-Z]+):([^: \t\n=><\)]+)(?::([^: \t\n=><\)]+))?'

        def replace_match(match):
            full_str = match.group(0)
            if "BIT" in full_str:
                return full_str
            return self.process_variable(full_str)

        return re.sub(pattern, replace_match, text)
# ... (DecisionDialog 类保持不变，请直接复制) ...


class DecisionDialog:
    def __init__(self, parent, line, reason):
        top = self.top = tk.Toplevel(parent)
        top.title("遇到复杂逻辑")
        top.geometry("600x400")

        self.result = "comment"
        self.manual_code = ""

        tk.Label(top, text="转换器遇到了无法自动处理的代码：", font=(
            "Arial", 10, "bold")).pack(pady=5)
        tk.Label(top, text=f"原因: {reason}", fg="red").pack()

        frame_code = tk.LabelFrame(top, text="ERB 原文")
        frame_code.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame_code, text=line, bg="#eee", anchor="w",
                 justify=tk.LEFT).pack(fill=tk.X, padx=5, pady=5)

        tk.Label(top, text="请选择处理方式：").pack(pady=5)

        btn_frame = tk.Frame(top)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="1. 注释掉 (TODO)", command=lambda: self.done(
            "comment")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="2. 写个 pass 跳过",
                  command=lambda: self.done("pass")).pack(side=tk.LEFT, padx=5)

        tk.Label(top, text="3. 手动输入 Python 代码替换：").pack(pady=5)
        self.txt_manual = tk.Text(top, height=5, width=60)
        self.txt_manual.pack(padx=10)

        tk.Button(top, text="确认使用手动代码", command=lambda: self.done(
            "manual"), bg="#c8e6c9").pack(pady=10)

    def done(self, result_type):
        self.result = result_type
        if result_type == "manual":
            self.manual_code = self.txt_manual.get(1.0, tk.END).strip()
        self.top.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ERBConverterGUI(root)
    root.mainloop()
