import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from ui.control_panel import ControlPanel
from player_controller import PlayerController

class MusicController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.player_controller = PlayerController()
        
        # 创建控制面板
        self.control_panel = ControlPanel(self.player_controller)
        # 连接关闭信号
        self.control_panel.destroyed.connect(self.app.quit)
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("assets/icon.png"))  # 需要添加图标文件
        self.setup_tray_menu()
        
    def setup_tray_menu(self):
        menu = QMenu()
        
        # 添加菜单项
        show_action = menu.addAction("显示控制面板")
        show_action.triggered.connect(self.control_panel.show)
        
        hide_action = menu.addAction("隐藏控制面板")
        hide_action.triggered.connect(self.control_panel.hide)
        
        menu.addSeparator()
        
        opacity_menu = menu.addMenu("透明度")
        for value in [100, 75, 50, 25]:
            action = opacity_menu.addAction(f"{value}%")
            action.triggered.connect(lambda checked, v=value: self.control_panel.set_opacity(v))
        
        menu.addSeparator()
        
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self.app.quit)
        
        self.tray_icon.setContextMenu(menu)
        
    def run(self):
        self.control_panel.show()
        self.tray_icon.show()
        return self.app.exec()

if __name__ == "__main__":
    controller = MusicController()
    sys.exit(controller.run()) 