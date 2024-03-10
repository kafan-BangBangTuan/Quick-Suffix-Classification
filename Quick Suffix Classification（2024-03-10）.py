import os
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


def process_and_copy():
    input_dir = input_entry.get()
    suffix = suffix_entry.get()
    output_dir = output_entry.get()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(suffix):
                shutil.copy(os.path.join(root, file), output_dir)

    messagebox.showinfo("成功", "处理完成！")


def process_and_move():
    input_dir = input_entry.get()
    suffix = suffix_entry.get()
    output_dir = output_entry.get()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(suffix):
                shutil.move(os.path.join(root, file), output_dir)

    messagebox.showinfo("成功", "处理完成！")


def all_process_and_copy():
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    for root, _, files in os.walk(input_dir):
        for file in files:
            if not os.path.exists(os.path.join(output_dir, os.path.splitext(file)[-1].lstrip('.'))):
                os.makedirs(os.path.join(output_dir, os.path.splitext(file)[-1].lstrip('.')))
            shutil.copy(os.path.join(root, file), os.path.join(output_dir, os.path.splitext(file)[-1].lstrip('.')))

    messagebox.showinfo("成功", "处理完成！")


def all_process_and_move():
    input_dir = input_entry.get()
    output_dir = output_entry.get()

    for root, _, files in os.walk(input_dir):
        for file in files:
            if not os.path.exists(os.path.join(output_dir, os.path.splitext(file)[-1].lstrip('.'))):
                os.makedirs(os.path.join(output_dir, os.path.splitext(file)[-1].lstrip('.')))
            shutil.move(os.path.join(root, file), os.path.join(output_dir, os.path.splitext(file)[-1].lstrip('.')))

    messagebox.showinfo("成功", "处理完成！")


def browse_input_dir():
    input_dir = filedialog.askdirectory()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, input_dir)


def browse_output_dir():
    output_dir = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, output_dir)


root = tk.Tk()
root.title("分类 2024-03-10版")
root.geometry('600x180')

label1 = tk.Label(root, text="需要处理的目录：")
label1.grid(row=0, column=0, padx=(10, 0))
input_entry = tk.Entry(root, width=30)
input_entry.grid(row=0, column=1, padx=(10, 0))

label2 = tk.Label(root, text="后缀名：")
label2.grid(row=1, column=0, padx=(10, 0))
suffix_entry = tk.Entry(root, width=15)
suffix_entry.grid(row=1, column=1, padx=(10, 0))

label3 = tk.Label(root, text="输出目录：")
label3.grid(row=2, column=0, padx=(10, 0))
output_entry = tk.Entry(root, width=30)
output_entry.grid(row=2, column=1, padx=(10, 0))

input_button = tk.Button(root, text="目录选择", command=browse_input_dir)
input_button.grid(row=0, column=2)
output_button = tk.Button(root, text="目录选择", command=browse_output_dir)
output_button.grid(row=2, column=2)

copy_button = tk.Button(root, text="指定后缀处理并复制", command=process_and_copy)
copy_button.grid(row=3, column=1)
move_button = tk.Button(root, text="指定后缀处理并移动", command=process_and_move)
move_button.grid(row=3, column=2)
all_copy_button = tk.Button(root, text="所有后缀分类处理并复制", command=all_process_and_copy)
all_copy_button.grid(row=4, column=1)
all_move_button = tk.Button(root, text="所有后缀分类处理并移动", command=all_process_and_move)
all_move_button.grid(row=4, column=2)

root.mainloop()
