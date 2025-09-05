import tkinter as tk
from tkinter import messagebox

class MenuBar:
    """菜单栏类，用于创建应用程序的菜单栏"""
    def __init__(self, root, dialogs, panels, tools):
        """初始化菜单栏"""
        self.root = root
        self.dialogs = dialogs
        self.panels = panels
        self.tools = tools
        
        # 创建菜单栏
        self._create_menu()
    
    def _create_menu(self):
        """创建菜单栏"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        
        # 创建文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 创建工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        
        # 为每个面板创建子菜单
        for panel_name in self.panels:
            # 创建面板子菜单
            panel_menu = tk.Menu(tools_menu, tearoff=0)
            
            # 添加该面板的所有工具
            if panel_name in self.tools:
                for tool_item in self.tools[panel_name]:
                    # 处理可能的元组格式 (tool_name, description, method_name)
                    if isinstance(tool_item, tuple) and len(tool_item) >= 1:
                        tool_name = tool_item[0]
                        # 获取method_name，如果元组长度大于等于3，则使用第三个元素
                        if len(tool_item) >= 3:
                            method_name = tool_item[2]
                        else:
                            method_name = tool_name
                    else:
                        tool_name = tool_item
                        method_name = tool_item
                    
                    # 获取对应的对话框方法
                    if method_name and isinstance(method_name, str):
                        dialog_method = getattr(self.dialogs, method_name, None)
                    if dialog_method:
                        panel_menu.add_command(label=tool_name, command=dialog_method)
                    else:
                        print(f"警告: 无法找到工具 '{tool_name}' 对应的对话框方法 '{method_name}'")
            
            # 将面板子菜单添加到工具菜单
            tools_menu.add_cascade(label=panel_name, menu=panel_menu)
        
        # 将工具菜单添加到菜单栏
        menubar.add_cascade(label="工具", menu=tools_menu)
        
        # 设置菜单栏
        self.root.config(menu=menubar)
