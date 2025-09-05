import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class BaseDialog:
    """基础对话框类，提供通用的对话框功能"""
    def __init__(self, parent, title, size=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        if size:
            self.dialog.geometry(size)
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)  # 使对话框成为主窗口的子窗口
        self.dialog.grab_set()  # 模态对话框

class GUIBase:
    """GUI基础类，提供通用的GUI功能"""
    def __init__(self, root=None):
        self.root = root
        self.current_row = 0
        
    def log(self, message):
        """记录日志"""
        print(f"[LOG] {message}")
        
    def create_directory_selector(self, parent, label_text):
        """创建文件夹选择控件"""
        # 创建标签
        label = ttk.Label(parent, text=label_text)
        label.grid(row=self.current_row, column=0, padx=5, pady=5, sticky="w")
        
        # 创建文本变量
        var = tk.StringVar()
        
        # 创建输入框
        entry = ttk.Entry(parent, textvariable=var, width=40)
        entry.grid(row=self.current_row, column=1, padx=5, pady=5)
        
        # 创建浏览按钮
        def browse_directory():
            directory = filedialog.askdirectory()
            if directory:
                var.set(directory)
        
        browse_btn = ttk.Button(parent, text="浏览...", command=browse_directory)
        browse_btn.grid(row=self.current_row, column=2, padx=5, pady=5)
        
        self.current_row += 1
        return var
    
    def create_file_selector(self, parent, label_text, filetypes=None):
        """创建文件选择控件"""
        # 创建标签
        label = ttk.Label(parent, text=label_text)
        label.grid(row=self.current_row, column=0, padx=5, pady=5, sticky="w")
        
        # 创建文本变量
        var = tk.StringVar()
        
        # 创建输入框
        entry = ttk.Entry(parent, textvariable=var, width=40)
        entry.grid(row=self.current_row, column=1, padx=5, pady=5)
        
        # 创建浏览按钮
        def browse_file():
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                var.set(file_path)
        
        browse_btn = ttk.Button(parent, text="浏览...", command=browse_file)
        browse_btn.grid(row=self.current_row, column=2, padx=5, pady=5)
        
        self.current_row += 1
        return var
    
    def create_progress_bar(self, parent):
        """创建进度条"""
        # 创建进度条变量
        progress_var = tk.DoubleVar()
        
        # 创建进度条
        progress_bar = ttk.Progressbar(parent, variable=progress_var, length=300)
        progress_bar.grid(row=self.current_row, column=0, columnspan=3, padx=5, pady=10)
        
        self.current_row += 1
        return progress_var, progress_bar
    
    def create_status_label(self, parent):
        """创建状态标签"""
        # 创建状态文本变量
        status_var = tk.StringVar(value="就绪")
        
        # 创建状态标签
        status_label = ttk.Label(parent, textvariable=status_var)
        status_label.grid(row=self.current_row, column=0, columnspan=3, padx=5, pady=5)
        
        self.current_row += 1
        return status_var, status_label
    
    def create_action_buttons(self, parent, run_command):
        """创建操作按钮"""
        # 创建按钮容器
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=self.current_row, column=0, columnspan=3, pady=10)
        
        # 创建运行按钮
        run_btn = ttk.Button(button_frame, text="运行", command=run_command)
        run_btn.pack(side="left", padx=10)
        
        # 创建取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=parent.destroy)
        cancel_btn.pack(side="left", padx=10)
        
        self.current_row += 1
    
    def create_scale_control(self, parent, label_text, from_, to_, initial):
        """创建滑块控件"""
        # 创建标签
        label = ttk.Label(parent, text=label_text)
        label.grid(row=self.current_row, column=0, padx=5, pady=10, sticky="w")
        
        # 创建滑块变量
        var = tk.DoubleVar(value=initial)
        
        # 创建滑块
        scale = ttk.Scale(parent, from_=from_, to=to_, variable=var, length=200, orient="horizontal")
        scale.grid(row=self.current_row, column=1, padx=5, pady=10)
        
        # 创建显示当前值的标签
        value_var = tk.StringVar(value=f"{var.get():.1f}")
        value_label = ttk.Label(parent, textvariable=value_var)
        value_label.grid(row=self.current_row, column=2, padx=5, pady=10)
        
        # 更新值标签的回调
        def update_value_label(event):
            value_var.set(f"{var.get():.1f}")
        
        parent.bind("<Motion>", update_value_label)
        
        self.current_row += 1
        return var, scale, value_var
        
    def create_text_control(self, parent, label_text, initial=None, width=40):
        """创建文本输入控件"""
        # 创建标签
        label = ttk.Label(parent, text=label_text)
        label.grid(row=self.current_row, column=0, padx=5, pady=5, sticky="w")
        
        # 创建文本变量
        var = tk.StringVar()
        if initial:
            var.set(initial)
        
        # 创建输入框
        entry = ttk.Entry(parent, textvariable=var, width=width)
        entry.grid(row=self.current_row, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.current_row += 1
        return var
    
    def show_feature_removed_message(self, dialog, feature_name):
        """显示功能已移除的消息"""
        self.log(f"{feature_name}功能已移除")
        messagebox.showinfo("提示", "此功能已移除")
        dialog.destroy()