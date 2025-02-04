import os
import shutil
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, font
import webbrowser
import time

# 修复链接问题
def open_github():
    webbrowser.open("https://github.com/kafan-BangBangTuan/Quick-Suffix-Classification")

# 创建一个带有动态省略号的等待窗口
def create_waiting_window():
    waiting_window = tk.Toplevel(root)
    waiting_window.title("正在处理")
    waiting_window.geometry("300x100")
    waiting_window.resizable(False, False)
    waiting_window.attributes('-topmost', True)  # 置顶

    waiting_label = tk.Label(waiting_window, text="正在处理，请稍等", font=("微软雅黑", 16), fg="red")
    waiting_label.pack(pady=20)

    def update_ellipsis():
        ellipsis = ["", ".", "..", "..."]
        index = 0
        while waiting_window.winfo_exists():
            waiting_label.config(text=f"正在处理，请稍等{ellipsis[index]}")
            index = (index + 1) % len(ellipsis)
            waiting_window.update()
            time.sleep(0.5)
        waiting_window.destroy()

    threading.Thread(target=update_ellipsis).start()
    return waiting_window

# 检测重复文件并弹出窗口询问是否覆盖
def check_and_ask_overwrite(files_to_copy, output_dir):
    duplicates = {}
    for src_path, dest_path in files_to_copy:
        if os.path.exists(dest_path):
            if dest_path not in duplicates:
                duplicates[dest_path] = []
            duplicates[dest_path].append(src_path)

    if duplicates:
        duplicate_window = tk.Toplevel(root)
        duplicate_window.title("有重复文件")
        duplicate_window.geometry("600x400")  # 调整窗口大小

        # 标签部分
        label_message = tk.Label(duplicate_window, text="检测到以下重复文件，是否覆盖这些文件？", font=("微软雅黑", 14), fg="red")
        label_message.pack(pady=10)

        # 按钮部分
        button_frame = tk.Frame(duplicate_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        user_choice = None

        def on_yes():
            nonlocal user_choice
            user_choice = True
            duplicate_window.destroy()

        def on_no():
            nonlocal user_choice
            user_choice = False
            duplicate_window.destroy()

        yes_button = tk.Button(button_frame, text="是，覆盖", command=on_yes, font=("微软雅黑", 14))
        no_button = tk.Button(button_frame, text="否，停止", command=on_no, font=("微软雅黑", 14))
        yes_button.pack(side=tk.LEFT, padx=20)
        no_button.pack(side=tk.RIGHT, padx=20)

        # 编辑框部分（带滚动条）
        text_area = scrolledtext.ScrolledText(duplicate_window, font=("微软雅黑", 12), wrap=tk.WORD)
        text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 显示重复文件信息
        message = ""
        for dest_path, src_paths in duplicates.items():
            message += f"目标路径: {dest_path}\n"
            for src_path in src_paths:
                message += f"  来源路径: {src_path}\n"
        text_area.insert(tk.INSERT, message)
        text_area.config(state=tk.DISABLED)

        duplicate_window.grab_set()  # 模态窗口
        duplicate_window.wait_window()  # 等待窗口关闭

        return user_choice
    return True

# 处理文件并复制
def process_and_copy():
    input_dir = input_entry.get()
    suffix = suffix_entry.get()
    output_dir = output_entry.get()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def copy_files():
        waiting_window = create_waiting_window()
        files_to_copy = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith(suffix):
                    ext = os.path.splitext(file)[-1].lstrip('.')
                    dest_dir = os.path.join(output_dir, ext)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_dir, file)
                    files_to_copy.append((src_path, dest_path))

        if check_and_ask_overwrite(files_to_copy, output_dir):
            output_text.delete(1.0, tk.END)  # 清空输出框
            success_count = 0
            fail_count = 0
            for src_path, dest_path in files_to_copy:
                try:
                    shutil.copy(src_path, dest_path)
                    output_text.insert(tk.END, f"复制: {src_path} -> {dest_path}\n")
                    success_count += 1
                except Exception as e:
                    output_text.insert(tk.END, f"操作失败: {src_path} ({e})\n")
                    fail_count += 1
            messagebox.showinfo("操作完成", f"成功 {success_count} 个，失败 {fail_count} 个")
        waiting_window.destroy()

    threading.Thread(target=copy_files).start()

# 处理文件并移动
def process_and_move():
    input_dir = input_entry.get()
    suffix = suffix_entry.get()
    output_dir = output_entry.get()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def move_files():
        waiting_window = create_waiting_window()
        files_to_move = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith(suffix):
                    ext = os.path.splitext(file)[-1].lstrip('.')
                    dest_dir = os.path.join(output_dir, ext)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_dir, file)
                    files_to_move.append((src_path, dest_path))

        if check_and_ask_overwrite(files_to_move, output_dir):
            output_text.delete(1.0, tk.END)  # 清空输出框
            success_count = 0
            fail_count = 0
            for src_path, dest_path in files_to_move:
                try:
                    shutil.move(src_path, dest_path)
                    output_text.insert(tk.END, f"移动: {src_path} -> {dest_path}\n")
                    success_count += 1
                except Exception as e:
                    output_text.insert(tk.END, f"操作失败: {src_path} ({e})\n")
                    fail_count += 1
            messagebox.showinfo("操作完成", f"成功 {success_count} 个，失败 {fail_count} 个")
        waiting_window.destroy()

    threading.Thread(target=move_files).start()

# 全部文件分类处理并复制
def all_process_and_copy():
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    def copy_all_files():
        waiting_window = create_waiting_window()
        files_to_copy = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                ext = os.path.splitext(file)[-1].lstrip('.')
                dest_dir = os.path.join(output_dir, ext)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, file)
                files_to_copy.append((src_path, dest_path))

        if check_and_ask_overwrite(files_to_copy, output_dir):
            output_text.delete(1.0, tk.END)  # 清空输出框
            success_count = 0
            fail_count = 0
            for src_path, dest_path in files_to_copy:
                try:
                    shutil.copy(src_path, dest_path)
                    output_text.insert(tk.END, f"复制: {src_path} -> {dest_path}\n")
                    success_count += 1
                except Exception as e:
                    output_text.insert(tk.END, f"操作失败: {src_path} ({e})\n")
                    fail_count += 1
            messagebox.showinfo("操作完成", f"成功 {success_count} 个，失败 {fail_count} 个")
        waiting_window.destroy()

    threading.Thread(target=copy_all_files).start()

# 全部文件分类处理并移动
def all_process_and_move():
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    def move_all_files():
        waiting_window = create_waiting_window()
        files_to_move = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                ext = os.path.splitext(file)[-1].lstrip('.')
                dest_dir = os.path.join(output_dir, ext)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, file)
                files_to_move.append((src_path, dest_path))

        if check_and_ask_overwrite(files_to_move, output_dir):
            output_text.delete(1.0, tk.END)  # 清空输出框
            success_count = 0
            fail_count = 0
            for src_path, dest_path in files_to_move:
                try:
                    shutil.move(src_path, dest_path)
                    output_text.insert(tk.END, f"移动: {src_path} -> {dest_path}\n")
                    success_count += 1
                except Exception as e:
                    output_text.insert(tk.END, f"操作失败: {src_path} ({e})\n")
                    fail_count += 1
            messagebox.showinfo("操作完成", f"成功 {success_count} 个，失败 {fail_count} 个")
        waiting_window.destroy()

    threading.Thread(target=move_all_files).start()

# 浏览输入目录
def browse_input_dir():
    input_dir = filedialog.askdirectory()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, input_dir)

# 浏览输出目录
def browse_output_dir():
    output_dir = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_dir)

# 主窗口
root = tk.Tk()
root.title("分类 2025-02-04版")
root.geometry('800x600')  # 调整窗口大小以适应所有组件

# 设置字体
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="微软雅黑", size=12)

# 界面布局
label1 = tk.Label(root, text="需要处理的目录：", font=("微软雅黑", 12))
label1.grid(row=0, column=0, padx=(10, 0), sticky="w")
input_entry = tk.Entry(root, width=30, font=("微软雅黑", 12))
input_entry.grid(row=0, column=1, padx=(10, 0), sticky="ew")

label2 = tk.Label(root, text="后缀名：", font=("微软雅黑", 12))
label2.grid(row=1, column=0, padx=(10, 0), sticky="w")
suffix_entry = tk.Entry(root, width=15, font=("微软雅黑", 12))
suffix_entry.grid(row=1, column=1, padx=(10, 0), sticky="ew")

label3 = tk.Label(root, text="输出目录：", font=("微软雅黑", 12))
label3.grid(row=2, column=0, padx=(10, 0), sticky="w")
output_entry = tk.Entry(root, width=30, font=("微软雅黑", 12))
output_entry.grid(row=2, column=1, padx=(10, 0), sticky="ew")

input_button = tk.Button(root, text="目录选择", command=browse_input_dir, font=("微软雅黑", 12))
input_button.grid(row=0, column=2, padx=(10, 10), sticky="ew")
output_button = tk.Button(root, text="目录选择", command=browse_output_dir, font=("微软雅黑", 12))
output_button.grid(row=2, column=2, padx=(10, 10), sticky="ew")

copy_button = tk.Button(root, text="指定后缀处理并复制", command=process_and_copy, font=("微软雅黑", 12))
copy_button.grid(row=3, column=1, pady=(10, 0), sticky="ew")
move_button = tk.Button(root, text="指定后缀处理并移动", command=process_and_move, font=("微软雅黑", 12))
move_button.grid(row=3, column=2, pady=(10, 0), sticky="ew")
all_copy_button = tk.Button(root, text="所有后缀分类处理并复制", command=all_process_and_copy, font=("微软雅黑", 12))
all_copy_button.grid(row=4, column=1, pady=(10, 0), sticky="ew")
all_move_button = tk.Button(root, text="所有后缀分类处理并移动", command=all_process_and_move, font=("微软雅黑", 12))
all_move_button.grid(row=4, column=2, pady=(10, 0), sticky="ew")

output_label = tk.Label(root, text="处理日志：", font=("微软雅黑", 12))
output_label.grid(row=5, column=0, pady=(10, 0), sticky="w")
output_text = scrolledtext.ScrolledText(root, width=70, height=10, font=("微软雅黑", 12))
output_text.grid(row=6, column=0, columnspan=3, padx=(10, 10), pady=(0, 10), sticky="nsew")

github_label = tk.Label(root, text="开源地址: https://github.com/kafan-BangBangTuan/Quick-Suffix-Classification", fg="blue", cursor="hand2", font=("微软雅黑", 12))
github_label.grid(row=7, column=0, columnspan=3, pady=(10, 0), sticky="w")
github_label.bind("<Button-1>", lambda e: open_github())

root.mainloop()