import os
import shutil
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

def process_files():
    input_dir = input_entry.get()
    suffix = suffix_entry.get()
    output_dir = output_entry.get()
    
    # 检查输入目录和输出目录是否存在
    if not os.path.exists(input_dir) or not os.path.exists(output_dir):
        # 如果输出目录不存在，则新建目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
    
    # 获取输入目录下的所有文件
    files = os.listdir(input_dir)
    
    # 遍历文件，按照后缀分类并复制到输出目录
    for file in files:
        if file.endswith(suffix):
            file_path = os.path.join(input_dir, file)
            shutil.copy(file_path, output_dir)
    
    # print("处理完成")
    messagebox.showinfo("提示", "处理完成")

def browse_input_dir():
    input_dir = filedialog.askdirectory()
    input_entry.delete(0, END)
    input_entry.insert(0, input_dir)

def browse_output_dir():
    output_dir = filedialog.askdirectory()
    output_entry.delete(0, END)
    output_entry.insert(0, output_dir)
    
    

# 创建窗口
window = Tk()
window.title("分类 2207版")
window.geometry("350x120")

# 创建输入框和标签
input_label = Label(window, text="输入目录:")
input_label.grid(row=0, column=0)
input_entry = Entry(window)
input_entry.grid(row=0, column=1)

browse_input_button = Button(window, text="浏览", command=browse_input_dir)
browse_input_button.grid(row=0, column=2)

suffix_label = Label(window, text="后缀名:")
suffix_label.grid(row=1, column=0)
suffix_entry = Entry(window)
suffix_entry.grid(row=1, column=1)

output_label = Label(window, text="输出目录:")
output_label.grid(row=2, column=0)
output_entry = Entry(window)
output_entry.grid(row=2, column=1)

browse_output_button = Button(window, text="浏览", command=browse_output_dir)
browse_output_button.grid(row=2, column=2)

# 创建按钮
process_button = Button(window, text="处理", command=process_files)
process_button.grid(row=3, columnspan=3)

# 运行窗口
window.mainloop()
