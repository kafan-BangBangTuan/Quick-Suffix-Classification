import os
import shutil
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, font
import webbrowser
import time
import queue

def open_github():
    webbrowser.open("https://github.com/kafan-BangBangTuan/Quick-Suffix-Classification")

def show_tempfile_info():
    messagebox.showinfo("忽略系统临时文件说明", 
                      "如勾选：\nWindows系统将忽略desktop.ini；\nmacOS将忽略.DS_Store")

def create_waiting_window():
    waiting_window = tk.Toplevel(root)
    waiting_window.title("正在处理")
    waiting_window.geometry("300x100")
    waiting_window.resizable(False, False)
    waiting_window.attributes('-topmost', True)

    waiting_label = tk.Label(waiting_window, text="正在处理，请稍等", font=("微软雅黑", 16), fg="red")
    waiting_label.pack(pady=20)

    running = [True]

    def update_ellipsis():
        ellipsis = ["", ".", "..", "..."]
        index = 0
        while running[0] and waiting_window.winfo_exists():
            try:
                waiting_label.config(text=f"正在处理，请稍等{ellipsis[index]}")
                waiting_window.update()
                index = (index + 1) % len(ellipsis)
                time.sleep(0.5)
            except tk.TclError:
                break

    def on_close():
        running[0] = False
        waiting_window.destroy()

    waiting_window.protocol("WM_DELETE_WINDOW", on_close)
    threading.Thread(target=update_ellipsis, daemon=True).start()
    return waiting_window

def handle_duplicates(files_to_process):
    #自动重命名
    dest_counter = {}
    processed_files = []
    
    for src_path, dest_path in files_to_process:
        base, ext = os.path.splitext(dest_path)
        if os.path.exists(dest_path) or dest_path in dest_counter:
            count = dest_counter.get(dest_path, 1)
            new_dest_path = f"{base}_{count}{ext}"
            
            # 确保新路径也不存在
            while os.path.exists(new_dest_path):
                count += 1
                new_dest_path = f"{base}_{count}{ext}"
            
            dest_counter[dest_path] = count + 1
            processed_files.append((src_path, new_dest_path))
        else:
            dest_counter[dest_path] = 1
            processed_files.append((src_path, dest_path))
    
    return processed_files

def check_duplicate_sources(files_to_process):
    #不同源重名文件
    filename_to_sources = {}
    
    for src_path, dest_path in files_to_process:
        filename = os.path.basename(dest_path)
        if filename not in filename_to_sources:
            filename_to_sources[filename] = []
        filename_to_sources[filename].append(src_path)
    
    #find
    conflicts = {fn: srcs for fn, srcs in filename_to_sources.items() 
                if len(srcs) > 1 and len({os.path.dirname(p) for p in srcs}) > 1}
    
    if not conflicts:
        return None
    
    
    conflict_info = []
    for filename, src_paths in conflicts.items():
        conflict_info.append(f"文件名: {filename}")
        for src_path in src_paths:
            conflict_info.append(f"  来源路径: {src_path}")
        conflict_info.append("")
    
    return "\n".join(conflict_info)

def check_existing_destinations(files_to_process):
    #目标目录重复文件
    existing_files = [(src, dest) for src, dest in files_to_process if os.path.exists(dest)]
    
    if not existing_files:
        return None
    
    
    existing_info = []
    for src_path, dest_path in existing_files:
        existing_info.append(f"目标路径: {dest_path}")
        existing_info.append(f"  来源路径: {src_path}")
        if os.path.exists(dest_path):
            existing_info.append(f"  目标文件已存在，大小: {os.path.getsize(dest_path)}字节")
        existing_info.append("")
    
    return "\n".join(existing_info)

def ask_user_action(conflict_type, message):
    #处理方式
    dialog = tk.Toplevel(root)
    dialog.title(f"检测到{conflict_type}冲突")
    dialog.geometry("700x500")
    
    label = tk.Label(dialog, text=f"检测到以下{conflict_type}冲突，请选择处理方式:", 
                    font=("微软雅黑", 12))
    label.pack(pady=10)
    
    text_area = scrolledtext.ScrolledText(dialog, font=("微软雅黑", 11), wrap=tk.WORD)
    text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, message)
    text_area.config(state=tk.DISABLED)
    
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    choice = tk.StringVar(value="rename")  # 默认选择自动重命名
    
    tk.Radiobutton(button_frame, text="自动重命名", variable=choice, 
                  value="rename", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(button_frame, text="覆盖", variable=choice, 
                  value="overwrite", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(button_frame, text="跳过", variable=choice, 
                  value="skip", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=10)
    
    def on_confirm():
        dialog.choice = choice.get()
        dialog.destroy()
    
    confirm_button = tk.Button(dialog, text="确认", command=on_confirm, 
                             font=("微软雅黑", 12))
    confirm_button.pack(pady=10)
    
    dialog.grab_set()
    dialog.wait_window()
    
    return getattr(dialog, 'choice', None)

def browse_input_dir():
    #input_dir
    input_dir = filedialog.askdirectory()
    if input_dir:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, input_dir)

def browse_output_dir():
    #output_dir
    output_dir = filedialog.askdirectory()
    if output_dir:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_dir)

def process_files(input_dir, output_dir, suffix, operation="copy"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def process():
        waiting_window = create_waiting_window()
        files_to_process = []
        
        #待处理文件
        for root, _, files in os.walk(input_dir):
            for file in files:
                #忽略系统临时文件
                if ignore_temp_var.get():
                    if file.lower() in ['.ds_store', 'desktop.ini']:
                        continue
                
                if not suffix or file.endswith(suffix):
                    ext = os.path.splitext(file)[-1].lstrip('.')
                    dest_dir = os.path.join(output_dir, ext)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_dir, file)
                    files_to_process.append((src_path, dest_path))

        #1处理源目录同名文件冲突
        source_conflict_msg = check_duplicate_sources(files_to_process)
        if source_conflict_msg:
            source_action = ask_user_action("不同源目录的同名文件", source_conflict_msg)
            if not source_action:  
                message_queue.put(("info", "操作取消", "用户取消了操作"))
                waiting_window.destroy()
                return
            
            if source_action == "skip":
                #
                conflict_srcs = set()
                for src_path, dest_path in files_to_process:
                    filename = os.path.basename(dest_path)
                    if filename in [line.split(":")[1].strip() for line in source_conflict_msg.split("\n") if line.startswith("文件名:")]:
                        conflict_srcs.add(src_path)
                
                files_to_process = [item for item in files_to_process if item[0] not in conflict_srcs]
            elif source_action == "rename":
                files_to_process = handle_duplicates(files_to_process)
            #如果选择"overwrite"则不做特殊处理
        
        #2处理目标目录已有文件冲突
        dest_conflict_msg = check_existing_destinations(files_to_process)
        if dest_conflict_msg:
            dest_action = ask_user_action("目标目录已存在文件", dest_conflict_msg)
            if not dest_action:  # 用户关闭窗口
                message_queue.put(("info", "操作取消", "用户取消了操作"))
                waiting_window.destroy()
                return
            
            if dest_action == "skip":
                files_to_process = [item for item in files_to_process if not os.path.exists(item[1])]
            elif dest_action == "rename":
                files_to_process = handle_duplicates(files_to_process)
            #如果选择"overwrite"则不做特殊处理
        
       
        output_text.delete(1.0, tk.END)
        success_count = 0
        fail_count = 0
        
        for src_path, dest_path in files_to_process:
            try:
                if operation == "copy":
                    shutil.copy(src_path, dest_path)
                    message_queue.put(("log", f"复制: {src_path} -> {dest_path}\n"))
                else:
                    shutil.move(src_path, dest_path)
                    message_queue.put(("log", f"移动: {src_path} -> {dest_path}\n"))
                success_count += 1
            except Exception as e:
                message_queue.put(("log", f"操作失败: {src_path} ({e})\n"))
                fail_count += 1
        
        message_queue.put(("info", "操作完成", f"成功 {success_count} 个，失败 {fail_count} 个"))
        waiting_window.destroy()

    def check_queue():
        try:
            while True:
                msg_type, *args = message_queue.get_nowait()
                if msg_type == "log":
                    output_text.insert(tk.END, args[0])
                    output_text.see(tk.END)
                elif msg_type == "info":
                    messagebox.showinfo(args[0], args[1])
        except queue.Empty:
            pass
        root.after(100, check_queue)

    threading.Thread(target=process, daemon=True).start()
    root.after(100, check_queue)

# 创建主窗口
root = tk.Tk()
root.title("快速后缀分类 2025-07-27版")
root.geometry('800x650')

# 设置默认字体
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="微软雅黑", size=12)

# 主界面布局
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

#忽略系统临时文件
options_frame = tk.Frame(root)
options_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky="w")

ignore_temp_var = tk.BooleanVar(value=False)
ignore_temp_check = tk.Checkbutton(options_frame, text="忽略系统临时文件", 
                                  variable=ignore_temp_var, font=("微软雅黑", 12))
ignore_temp_check.pack(side=tk.LEFT, padx=(10, 0))

info_button = tk.Button(options_frame, text="查看详情", command=show_tempfile_info, 
                        font=("微软雅黑", 10), fg="blue")
info_button.pack(side=tk.LEFT, padx=(5, 0))

copy_button = tk.Button(root, text="指定后缀处理并复制", 
                       command=lambda: process_files(input_entry.get(), output_entry.get(), suffix_entry.get(), "copy"), 
                       font=("微软雅黑", 12))
copy_button.grid(row=4, column=1, pady=(10, 10), sticky="ew")

move_button = tk.Button(root, text="指定后缀处理并移动", 
                       command=lambda: process_files(input_entry.get(), output_entry.get(), suffix_entry.get(), "move"), 
                       font=("微软雅黑", 12))
move_button.grid(row=4, column=2, pady=(10, 10), sticky="ew")

all_copy_button = tk.Button(root, text="所有后缀分类处理并复制", 
                           command=lambda: process_files(input_entry.get(), output_entry.get(), "", "copy"), 
                           font=("微软雅黑", 12))
all_copy_button.grid(row=5, column=1, pady=(10, 10), sticky="ew")

all_move_button = tk.Button(root, text="所有后缀分类处理并移动", 
                           command=lambda: process_files(input_entry.get(), output_entry.get(), "", "move"), 
                           font=("微软雅黑", 12))
all_move_button.grid(row=5, column=2, pady=(10, 10), sticky="ew")


output_label = tk.Label(root, text="处理日志：", font=("微软雅黑", 12))
output_label.grid(row=6, column=0, pady=(10, 0), sticky="w")
output_text = scrolledtext.ScrolledText(root, width=70, height=10, font=("微软雅黑", 12))
output_text.grid(row=7, column=0, columnspan=3, padx=(10, 10), pady=(0, 10), sticky="nsew")


github_label = tk.Label(root, text="开源地址: https://github.com/kafan-BangBangTuan/Quick-Suffix-Classification", 
                       fg="blue", cursor="hand2", font=("微软雅黑", 12))
github_label.grid(row=8, column=0, columnspan=3, pady=(10, 0), sticky="w")
github_label.bind("<Button-1>", lambda e: open_github())


message_queue = queue.Queue()

root.mainloop()

# 2025.07.27  构建发布