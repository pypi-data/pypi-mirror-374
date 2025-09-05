import tkinter as tk
from tkinter import ttk, messagebox
from .base_gui import BaseDialog, GUIBase

class Dialogs(GUIBase):
    """对话框集合类，支持动态注册对话框功能"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # 存储注册的对话框配置
        self.dialog_configs = {}
        # 存储注册的对话框方法
        self.dialog_methods = {}
        
    def register_dialog(self, method_name, title, size, action=None, elements=None):
        """注册一个对话框
        
        参数:
        - method_name: 对话框方法名
        - title: 对话框标题
        - size: 对话框尺寸
        - action: 运行按钮的回调函数
        - elements: 对话框元素配置列表
        """
        # 存储对话框配置
        self.dialog_configs[method_name] = {
            'title': title,
            'size': size,
            'elements': elements or [],
            'action': action or self._default_action
        }
        
        # 创建并注册对话框方法
        def dialog_method():
            self._create_dialog(method_name)
        
        # 将对话框方法绑定到当前实例
        setattr(self, method_name, dialog_method)
        self.dialog_methods[method_name] = dialog_method
        
        print(f"注册对话框方法: {method_name} - {title}")
    
    def _create_dialog(self, method_name):
        """根据注册的配置创建对话框"""
        config = self.dialog_configs.get(method_name)
        if not config:
            self.log(f"错误: 未找到对话框配置 '{method_name}'")
            return
        
        # 重置当前行计数器
        self.current_row = 0
        
        # 创建基础对话框
        dialog = BaseDialog(self.parent, config['title'], config['size']).dialog
        
        # 存储当前对话框的变量
        dialog_vars = {}
        
        # 根据配置创建对话框元素
        for element in config['elements']:
            element_type = element.get('type')
            element_label = element.get('label', '')
            
            if element_type == 'directory_selector':
                var = self.create_directory_selector(dialog, element_label)
                dialog_vars[element.get('id', element_label)] = var
            elif element_type == 'file_selector':
                filetypes = element.get('filetypes', None)
                var = self.create_file_selector(dialog, element_label, filetypes)
                dialog_vars[element.get('id', element_label)] = var
            elif element_type == 'progress_bar':
                progress_var, progress_bar = self.create_progress_bar(dialog)
                dialog_vars[element.get('id', element_label)] = progress_var
            elif element_type == 'status_label':
                status_var, status_label = self.create_status_label(dialog)
                dialog_vars[element.get('id', element_label)] = status_var
            elif element_type == 'scale':
                from_ = element.get('from', 0)
                to = element.get('to', 100)
                initial = element.get('initial', 50)
                var, scale, value_var = self.create_scale_control(
                    dialog, element_label, from_, to, initial
                )
                dialog_vars[element.get('id', element_label)] = var
                dialog_vars[element.get('id', element_label) + '_value'] = value_var
            elif element_type == 'text':
                initial = element.get('initial', '')
                width = element.get('width', 40)
                var = self.create_text_control(
                    dialog, element_label, initial, width
                )
                dialog_vars[element.get('id', element_label)] = var
        
        # 创建操作按钮，提供通用的函数调用机制
        if config['action'] == None:
            # 如果action为None，创建一个禁用按钮的函数
            def execute_action():
                messagebox.showinfo("提示", "此功能未实现")
                dialog.destroy()
        else:
            # 正常情况的execute_action函数
            def execute_action():
                try:
                    # 获取所有对话框变量的当前值
                    kwargs = {}
                    for key, var in dialog_vars.items():
                        try:
                            if hasattr(var, 'get'):
                                value = var.get()
                            else:
                                value = var
                            kwargs[key] = value
                        except Exception:
                            # 如果获取值失败，跳过这个参数
                            continue
                    
                    # 调用action函数
                    # breakpoint()
                    config['action'](**kwargs)
                
                except Exception as e:
                    self.log(f"执行操作时出错: {str(e)}")
                    messagebox.showerror("错误", f"执行操作时出错: {str(e)}")
                
                finally:
                    # 确保对话框总是关闭
                    dialog.destroy()
        
        self.create_action_buttons(dialog, execute_action)
        
        # 如果action为None，禁用运行按钮
        if config['action'] == None:
            # 获取按钮容器
            for child in dialog.winfo_children():
                if isinstance(child, ttk.Frame):
                    # 遍历按钮容器中的按钮
                    for button in child.winfo_children():
                        if isinstance(button, ttk.Button) and button['text'] == '运行':
                            # 禁用运行按钮
                            button['state'] = 'disabled'
    
    def _default_action(self, dialog, dialog_vars, method_name):
        """默认的对话框操作"""
        self.log(f"运行对话框: {method_name}")
        config = self.dialog_configs.get(method_name)
        if config:
            self.show_feature_removed_message(dialog, config['title'])
    
    def about_dialog(self):
        """显示关于对话框"""
        messagebox.showinfo(
            title="关于CSLib工具合集",
            message="CSLib工具合集 v1.0.0\n\n这是一个集成了图像处理和指标分析功能的工具合集应用程序外壳。\n\n作者: CSLib开发团队\n邮箱: contact@cslib.org"
        )