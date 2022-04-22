import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import *
from tkinter import filedialog
from creator import creator
from creator.docx2md import Docx2Md
from pathlib import Path
import windnd
from creator import obtrans

intab = '/'
outtab = '\\'
table_value = str.maketrans(intab, outtab)


class WikiCreator:
    def __init__(self, master):
        self.master = master
        self.master.title('WikiCreator')
        self.master.geometry('800x800+500+100')
        self.master.resizable(True, True)
        windnd.hook_dropfiles(self.master, func=self.drag_callback)
        ttk.Label(self.master, text="WikiCreator", font=("微软雅黑", 20)).pack(side='top', pady=5, fill='x', padx=5) # 标题
        ttk.Label(self.master, text="拖拽或点击将md、docx文件或obsidian目录上传至wiki.js", font=("微软雅黑", 15)).pack(side='top', pady=5, fill='x', padx=5)
        commit = ttk.Button(self.master, text="提交WIKI库", bootstyle=SUCCESS)  # 提交测试按钮
        commit.pack(side='bottom', fill='x', padx=5, pady=5)
        commit.bind('<Button-1>', func=self.commit_callback)
        self.need_path, self.all_path, self.exist_title = creator.get_path()
        self.exist_title = [x[0] for x in self.exist_title]
        self.user_frame()
        self.master.mainloop()

    def user_frame(self):
        """创建用户操作frame区域"""
        module_width = 30
        font = ("微软雅黑", 10)
        pady = 10
        frame = tk.Frame(self.master)
        frame.pack()
        # 文件选择框
        self.file_input = ttk.Entry(frame, font=font, width=module_width)
        self.file_input.grid(row=0, column=0, pady=30)
        frame2 = tk.Frame(frame)
        frame2.grid(row=0, column=1, pady=30)
        choose_btn = ttk.Button(frame2, text="选择文件", bootstyle='success-outline', width=16)
        choose_btn.bind('<Button-1>', func=self.choosbtn_callback)
        choose_btn.grid(row=0, column=0)
        choosedir_btn = ttk.Button(frame2, text="选择文件夹", bootstyle='success-outline', width=16)
        choosedir_btn.bind('<Button-1>', func=self.choosdirbtn_callback)
        choosedir_btn.grid(row=0, column=1)
        # 添加下拉框
        self.cbox = ttk.Combobox(frame, width=27, font=font, state='readonly')
        list_path = list(self.need_path)
        list_path = sorted(list_path)
        self.cbox['value'] = list_path
        self.cbox.current(0)
        self.cbox.grid(row=1, column=0, pady=pady)
        # 路径输入框
        self.path = ttk.Entry(frame, width=module_width, font=font)
        self.path.grid(row=1, column=1, pady=pady)
        # 标题
        self.title_lable = ttk.Label(frame, text='输入文档标题', width=module_width, font=font, bootstyle='inverse-success')
        self.title_lable.grid(row=2, column=0, pady=pady)
        self.title_input = ttk.Entry(frame, width=module_width, font=font)
        self.title_input.grid(row=2, column=1, pady=pady)
        # 文档描述
        self.desc_lable = ttk.Label(frame, text='请输入文档描述', width=module_width, font=font, bootstyle='inverse-success')
        self.desc_lable.grid(row=3, column=0, pady=pady)
        self.desc_input = ttk.Entry(frame, width=module_width, font=font)
        self.desc_input.grid(row=3, column=1, pady=pady)
        # 文档标签
        self.tag_lable = ttk.Label(frame, text='请输入标签', width=module_width, font=font, bootstyle='inverse-success')
        self.tag_lable.grid(row=4, column=0, pady=pady)
        self.tag_input = ttk.Entry(frame, width=module_width, font=font)
        self.tag_input.grid(row=4, column=1, pady=pady)

    def drag_callback(self, file):
        self.file_input.delete(0, END)
        self.file_input.insert(0, file[0].decode('gbk'))

    def choosbtn_callback(self, event):
        file_path = filedialog.askopenfilename()
        self.file_input.delete(0, END)
        self.file_input.insert(0, file_path)

    def choosdirbtn_callback(self, event):
        dir_path = filedialog.askdirectory()
        self.file_input.delete(0, END)
        self.file_input.insert(0, dir_path)

    def commit_callback(self, event):
        file = self.file_input.get()
        file = file.translate(table_value)
        path = self.cbox.get() + '/' + self.path.get()
        title = self.title_input.get()
        desc = self.desc_input.get()
        tags = self.tag_input.get()
        if path in self.all_path:
            Messagebox.show_warning('已存在此页面路径，请更换路径', '路径重复', self.master)
        elif title in self.exist_title:
            Messagebox.show_warning('已存在此页面标题，请更换文档标题', '标题重复', self.master)
        else:
            try:
                if all([path, title, file]):
                    if file.endswith('.md'):
                        content, img_list = creator.read_md(r''.join(file))
                    elif file.endswith('.docx'):
                        # print(file)
                        content, img_list = Docx2Md(file).docx2md()
                    elif Path(file).is_dir():
                        md_list, png_list = obtrans.obsidian_trans((file,))
                        md_file = md_list[0]
                        content, img_list = creator.read_md(md_file)
                        img_list = png_list
                    else:
                        raise Exception("目前仅支持markdown和docx格式文件！！！")
                    for img in img_list:
                        res = creator.upload_pic(img)
                    res = creator.create_markdown(content=content, desc=desc, path=path, tags=tags, title=title)
                    if int(res.status_code) == 200:
                        Messagebox.ok('文件上传成功！！！', '上传成功', False, self.master)
                    else:
                        Messagebox.show_error('文件上传失败！！！', '上传失败', self.master)
                    for pics in img_list:
                        Path(pics).unlink(missing_ok=True)
                else:
                    Messagebox.show_warning(message='文件、路径和标题不能为空！！！', title='提交失败', parent=self.master)
            except Exception as e:
                Messagebox.show_error(f'上传出错，出错原因\n{e}', '运行出错', self.master)


if __name__ == '__main__':
    root = ttk.Window(themename='minty')
    WikiCreator(root)

