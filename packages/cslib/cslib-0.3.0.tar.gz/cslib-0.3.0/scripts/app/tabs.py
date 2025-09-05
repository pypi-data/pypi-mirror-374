import tkinter as tk
from tkinter import ttk

class TabsManager:
    """选项卡管理器，负责创建和管理所有选项卡"""
    def __init__(self, root, dialogs, panels, tools):
        self.root = root
        self.dialogs = dialogs
        self.panels = panels
        self.tools = tools
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 根据注册的面板和工具动态创建选项卡
        self._create_tabs_from_registry()
    
    def _create_tabs_from_registry(self):
        """根据注册的面板和工具动态创建选项卡"""
        for panel_name in self.panels:
            # 创建选项卡
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=panel_name)
            
            # 获取面板描述
            panel_desc = self.panels.get(panel_name, "")
            
            # 创建按钮容器
            button_frame = ttk.LabelFrame(tab, text=f"{panel_name}工具")
            button_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 获取该面板的工具
            panel_tools = self.tools.get(panel_name, [])
            
            # 计算需要的列数（最多3列）
            columns = min(3, len(panel_tools))
            if columns > 0:
                # 设置列配置
                for i in range(columns):
                    button_frame.columnconfigure(i, weight=1)
                
                # 创建按钮
            for i, tool_item in enumerate(panel_tools):
                row = i // columns
                col = i % columns
                
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
                dialog_method = getattr(self.dialogs, method_name, None)
                if dialog_method:
                    btn = ttk.Button(
                        button_frame, 
                        text=tool_name, 
                        command=dialog_method,
                        width=20
                    )
                    btn.grid(row=row, column=col, padx=5, pady=5)
                else:
                    print(f"警告: 无法找到工具 '{tool_name}' 对应的对话框方法 '{method_name}'")
            
            # 创建预览/结果显示框架
            show_frame_title = "预览" if "图像" in panel_name else "结果显示"
            show_frame = ttk.LabelFrame(tab, text=show_frame_title)
            show_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # 添加占位标签
            placeholder_label = ttk.Label(show_frame, text=f"{show_frame_title}区域")
            placeholder_label.pack(pady=20)