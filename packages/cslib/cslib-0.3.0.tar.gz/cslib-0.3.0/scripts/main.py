#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSLib工具合集主程序
"""
import tkinter as tk
import sys
import os
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.app import App

import images
import metrics

class CslibGUI(App):
    """CSLib工具合集主界面类"""

    def regist_tools(self):
        # 注册面板
        self.register_panel("图像处理", "图像处理相关工具")
        # self.register_panel("指标分析", "指标分析相关工具")
        
        # 注册图像处理工具
        self.register_tool("图像处理", "灰度图片上色", "将灰度图片转换为彩色图片", "gray_to_color_dialog")
        self.register_tool("图像处理", "彩色图片转灰度", "将彩色图片转换为灰度图片", "color_to_gray_dialog")
        self.register_tool("图像处理", "调整图片亮度", "调整图片的亮度", "adjust_brightness_dialog")
        self.register_tool("图像处理", "图片反色", "将图片颜色反转", "reverse_image_dialog")
        self.register_tool("图像处理", "转换图片格式", "转换图片的文件格式", "convert_format_dialog")
        # self.register_tool("图像处理", "添加边框", "为图片添加边框", "add_border_dialog")
        # self.register_tool("图像处理", "归一化图片", "将图片尺寸归一化", "normalize_images_dialog")
        
        # 注册指标分析工具
        # self.register_tool("指标分析", "计算融合指标", "计算图像融合的各项指标", "compute_metrics_dialog")
        # self.register_tool("指标分析", "分析指标数据", "分析已计算的指标数据", "analyze_metrics_dialog")
        # self.register_tool("指标分析", "合并指标数据库", "合并多个指标数据库", "merge_metrics_dialog")
        # self.register_tool("指标分析", "按算法拆分数据库", "按算法将数据库拆分为多个文件", "split_by_alg_dialog")
        # self.register_tool("指标分析", "按指标拆分数据库", "按指标类型将数据库拆分为多个文件", "split_by_metric_dialog")

    def register_dialogs(self):
        """初始化对话框管理器"""
        # 注册图像处理相关对话框
        self.dialogs.register_dialog(
            "gray_to_color_dialog", 
            "灰度图片上色", 
            "500x350",
            images.add_color_to_gray,
            [
                {'type': 'directory_selector', 'label': '彩色图片文件夹：', 'id': 'src_color'},
                {'type': 'directory_selector', 'label': '灰度图片文件夹：', 'id': 'src_gray'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'dst'}
            ]
        )
        
        self.dialogs.register_dialog(
            "color_to_gray_dialog", 
            "彩色图片转灰度", 
            "500x250",
            images.change_color_to_gray,
            [
                {'type': 'directory_selector', 'label': '源图片文件夹：', 'id': 'src_folder'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'output_folder'}
            ]
        )
        
        self.dialogs.register_dialog(
            "adjust_brightness_dialog", 
            "调整图片亮度", 
            "500x300",
            images.adjust_brightness,
            [
                {'type': 'directory_selector', 'label': '源图片文件夹：', 'id': 'src_folder'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'output_folder'},
                {'type': 'scale', 'label': '亮度系数 (0.1-3.0):', 'id': 'brightness', 'from': 0.1, 'to': 3.0, 'initial': 1.5}
            ]
        )
        
        self.dialogs.register_dialog(
            "reverse_image_dialog", 
            "图片反色", 
            "500x250",
            images.reverse_images,
            [
                {'type': 'directory_selector', 'label': '源图片文件夹：', 'id': 'src_folder'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'output_folder'}
            ]
        )
        
        self.dialogs.register_dialog(
            "convert_format_dialog", 
            "转换图片格式", 
            "500x250",
            images.change_image_prefix,
            [
                {'type': 'directory_selector', 'label': '源图片文件夹：', 'id': 'src'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'des'},
                {'type': 'text', 'label': '输出格式：', 'id': 'format', 'initial': 'png'}
            ]
        )
        
        self.dialogs.register_dialog(
            "add_border_dialog", 
            "添加边框", 
            "500x250",
            None,
            [
                {'type': 'directory_selector', 'label': '源图片文件夹：', 'id': 'src_folder'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'output_folder'}
            ]
        )
        
        self.dialogs.register_dialog(
            "normalize_images_dialog", 
            "归一化图片", 
            "500x250",
            None,
            [
                {'type': 'directory_selector', 'label': '源图片文件夹：', 'id': 'src_folder'},
                {'type': 'directory_selector', 'label': '输出文件夹：', 'id': 'output_folder'}
            ]
        )
        
        # 注册指标分析相关对话框
        self.dialogs.register_dialog(
            "compute_metrics_dialog", 
            "计算融合指标", 
            "500x300",
            None,
            [
                {'type': 'directory_selector', 'label': '融合结果文件夹：', 'id': 'fusion_folder'},
                {'type': 'file_selector', 'label': '数据库文件：', 'id': 'db_path', 'filetypes': [('数据库文件', '*.db')]}
            ]
        )
        
        self.dialogs.register_dialog(
            "analyze_metrics_dialog", 
            "分析指标数据", 
            "500x250",
            None,
            [
                {'type': 'file_selector', 'label': '数据库文件：', 'id': 'db_path', 'filetypes': [('数据库文件', '*.db')]}
            ]
        )
        
        self.dialogs.register_dialog(
            "merge_metrics_dialog", 
            "合并指标数据库", 
            "500x300",
            None,
            [
                {'type': 'file_selector', 'label': '第一个数据库：', 'id': 'db1_path', 'filetypes': [('数据库文件', '*.db')]},
                {'type': 'file_selector', 'label': '第二个数据库：', 'id': 'db2_path', 'filetypes': [('数据库文件', '*.db')]},
                {'type': 'file_selector', 'label': '输出数据库：', 'id': 'output_db', 'filetypes': [('数据库文件', '*.db')]}
            ]
        )
        
        self.dialogs.register_dialog(
            "split_by_alg_dialog", 
            "按算法拆分数据库", 
            "500x250",
            None,
            [
                {'type': 'file_selector', 'label': '数据库文件：', 'id': 'db_path', 'filetypes': [('数据库文件', '*.db')]},
                {'type': 'directory_selector', 'label': '输出目录：', 'id': 'output_dir'}
            ]
        )
        
        self.dialogs.register_dialog(
            "split_by_metric_dialog", 
            "按指标拆分数据库", 
            "500x250",
            None,
            [
                {'type': 'file_selector', 'label': '数据库文件：', 'id': 'db_path', 'filetypes': [('数据库文件', '*.db')]},
                {'type': 'directory_selector', 'label': '输出目录：', 'id': 'output_dir'}
            ]
        )
    
if __name__ == "__main__":
    # 创建并运行应用程序
    root = tk.Tk()
    app = CslibGUI(root)
    root.mainloop()