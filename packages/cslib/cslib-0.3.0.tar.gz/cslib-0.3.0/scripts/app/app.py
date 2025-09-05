from .dialogs import Dialogs
from .menu import MenuBar
from .tabs import TabsManager
from .dialogs import Dialogs

class App:
    """CSLib工具合集主界面类"""
    def __init__(self, root):
        """初始化应用程序界面"""
        # 设置窗口标题和大小
        self.root = root
        self.root.title("CSLib工具合集")
        self.root.geometry("900x600")
        self.root.minsize(800, 600)
        
        # 设置中文字体支持
        self._setup_fonts()
        
        # 初始化对话框管理器
        self.dialogs = Dialogs(self.root)
        
        # 存储面板和工具信息
        self.panels = {}
        self.tools = {}
        
        self.regist()

    def regist(self):
        # 先注册对话框
        self.register_dialogs()
        # 再注册工具和面板
        self.regist_tools()
        # 最后创建菜单栏和选项卡（在所有注册完成后）
        self.menu = MenuBar(self.root, self.dialogs, self.panels, self.tools)
        self.tabs_manager = TabsManager(self.root, self.dialogs, self.panels, self.tools)
    
    def register_dialogs(self):
        raise NotImplementedError("register_dialogs方法必须在子类中实现")
    
    def regist_tools(self):
        raise NotImplementedError("regist_tools方法必须在子类中实现")
    
    def register_panel(self, name, description=""):
        """注册一个新的面板"""
        if name not in self.panels:
            self.panels[name] = description
            print(f"注册面板: {name} - {description}")
        # 初始化该面板的工具列表
        if name not in self.tools:
            self.tools[name] = []
    
    def register_tool(self, panel_name, tool_name, description="", method_name=None):
        """在指定面板中注册一个工具"""
        if panel_name in self.panels:
            # 确保面板的工具列表已初始化
            if panel_name not in self.tools:
                self.tools[panel_name] = []
            # 添加工具，如果未提供method_name，则使用默认规则生成
            if method_name is None:
                method_name = tool_name
            self.tools[panel_name].append((tool_name, description, method_name))
            print(f"在面板 '{panel_name}' 中注册工具: {tool_name} - {description}")
        else:
            print(f"警告: 面板 '{panel_name}' 不存在，无法注册工具 '{tool_name}'")

    def _setup_fonts(self):
        """设置中文字体支持"""
        # 设置默认字体
        default_font = ("SimHei", 10)
        text_font = ("SimHei", 10)
        heading_font = ("SimHei", 11, "bold")
        
        # 配置字体
        self.root.option_add("*Font", default_font)
        self.root.option_add("*TLabel.Font", default_font)
        self.root.option_add("*TButton.Font", default_font)
        self.root.option_add("*TEntry.Font", default_font)
