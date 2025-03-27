from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMenu, QApplication
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, Property, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
import json
import os

class ControlPanel(QWidget):
    def __init__(self, player_controller):
        super().__init__()
        self.player_controller = player_controller
        self.dragging = False
        self.drag_position = None
        self.opacity = 100
        
        # 初始化时获取当前播放状态，之后只在点击时切换
        self.is_playing = self.player_controller.get_playing_state()
        
        # 动画相关的属性
        self._hover_section = -1  # -1表示没有悬停
        self._pressed_section = -1  # -1表示没有按下
        self._press_animation = 0.0  # 按压动画进度
        self._hover_opacity = [0.0, 0.0, 0.0]  # 三个按钮的悬停透明度
        
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(150, 50)
        self.setMouseTracking(True)  # 启用鼠标追踪
        
        # 创建布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 创建右键菜单
        self.context_menu = QMenu(self)
        self.setup_context_menu()
        
        # 创建动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(16)  # 约60fps
        
        # 加载上次保存的位置
        self.load_position()
        
    def setup_context_menu(self):
        """设置右键菜单"""
        # 添加透明度子菜单
        opacity_menu = self.context_menu.addMenu("透明度")
        for value in [100, 75, 50, 25]:
            action = opacity_menu.addAction(f"{value}%")
            action.triggered.connect(lambda checked, v=value: self.set_opacity(v))
            
        self.context_menu.addSeparator()
        
        # 添加隐藏选项
        hide_action = self.context_menu.addAction("隐藏")
        hide_action.triggered.connect(self.hide)
        
    def contextMenuEvent(self, event):
        """处理右键点击事件"""
        self.context_menu.exec(event.globalPos())
        
    def update_animations(self):
        need_update = False
        
        # 更新按压动画
        if self._pressed_section != -1:
            self._press_animation = min(1.0, self._press_animation + 0.2)
            need_update = True
        else:
            self._press_animation = max(0.0, self._press_animation - 0.2)
            if self._press_animation > 0:
                need_update = True
        
        # 更新悬停动画
        for i in range(3):
            target = 1.0 if i == self._hover_section else 0.0
            current = self._hover_opacity[i]
            if abs(target - current) > 0.01:
                self._hover_opacity[i] += (target - current) * 0.2
                need_update = True
        
        if need_update:
            self.update()
    
    def get_section_at(self, x):
        """获取指定x坐标所在的区域（0-2）"""
        width = self.width()
        if x < width / 3:
            return 0
        elif x < (width * 2) / 3:
            return 1
        return 2
        
    def load_position(self):
        """加载上次保存的窗口位置"""
        try:
            if os.path.exists('window_position.json'):
                with open('window_position.json', 'r') as f:
                    pos = json.load(f)
                    # 确保窗口不会完全超出屏幕
                    screen = QApplication.primaryScreen().geometry()
                    x = max(0, min(pos['x'], screen.width() - self.width()))
                    y = max(0, min(pos['y'], screen.height() - self.height()))
                    self.move(x, y)
            else:
                # 如果没有保存的位置，将窗口放在屏幕右下角
                screen = QApplication.primaryScreen().geometry()
                self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 20)
        except Exception as e:
            print(f"加载窗口位置失败: {e}")
            # 如果加载失败，将窗口放在屏幕右下角
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 20)
            
    def save_position(self):
        """保存当前窗口位置"""
        try:
            pos = {
                'x': self.x(),
                'y': self.y()
            }
            with open('window_position.json', 'w') as f:
                json.dump(pos, f)
        except Exception as e:
            print(f"保存窗口位置失败: {e}")
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._pressed_section = self.get_section_at(event.position().x())
            event.accept()
            
            # 检测点击区域并发送控制命令
            try:
                if self._pressed_section == 0:
                    self.player_controller.previous_track()
                elif self._pressed_section == 1:
                    # 发送播放/暂停命令并直接切换图标状态
                    self.player_controller.play_pause()
                    self.is_playing = not self.is_playing  # 切换状态
                    self.update()  # 更新界面
                else:
                    self.player_controller.next_track()
            except Exception as e:
                print(f"控制命令执行失败: {e}")
                
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self._pressed_section = -1
            # 保存新的窗口位置
            self.save_position()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # 更新悬停区域
            self._hover_section = self.get_section_at(event.position().x())
            self.update()
            event.accept()
            
    def enterEvent(self, event):
        self.opacity = 100
        self.update()
        event.accept()
        
    def leaveEvent(self, event):
        self.opacity = 80
        self._hover_section = -1
        self.update()
        event.accept()
        
    def closeEvent(self, event):
        # 保存窗口位置
        self.save_position()
        event.accept()
        
    def hideEvent(self, event):
        # 保存窗口位置
        self.save_position()
        event.accept()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置透明度
        painter.setOpacity(self.opacity / 100.0)
        
        # 绘制背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(60, 60, 60, 200))
        gradient.setColorAt(1, QColor(40, 40, 40, 200))
        painter.fillPath(path, gradient)
        
        # 绘制分隔线
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawLine(self.width() // 3, 5, self.width() // 3, self.height() - 5)
        painter.drawLine((self.width() * 2) // 3, 5, (self.width() * 2) // 3, self.height() - 5)
        
        # 绘制按钮悬停和按压效果
        section_width = self.width() // 3
        for i in range(3):
            if self._hover_opacity[i] > 0 or (self._pressed_section == i and self._press_animation > 0):
                hover_path = QPainterPath()
                x = i * section_width
                hover_path.addRoundedRect(x, 0, section_width, self.height(), 
                                        10 if i == 0 else 0, 
                                        10 if i == 2 else 0)
                
                # 混合悬停和按压效果
                hover_color = QColor(255, 255, 255, 
                                   int(30 * self._hover_opacity[i] + 
                                       50 * self._press_animation if i == self._pressed_section else 0))
                painter.fillPath(hover_path, hover_color)
        
        # 绘制图标
        self.draw_icons(painter)
        
    def draw_icons(self, painter):
        # 设置图标颜色，考虑悬停和按压状态
        for i, draw_func in enumerate([self.draw_previous_icon, 
                                     self.draw_play_pause_icon, 
                                     self.draw_next_icon]):
            x = (i * 2 + 1) * self.width() // 6
            
            # 计算图标颜色
            base_color = QColor(255, 255, 255)
            if i == self._pressed_section:
                # 按压时图标变暗
                base_color = QColor(200, 200, 200)
            elif self._hover_opacity[i] > 0:
                # 悬停时图标变亮
                base_color = QColor(255, 255, 255)
            
            painter.setPen(QPen(base_color, 2))
            draw_func(painter, x)
        
    def draw_previous_icon(self, painter, x):
        y = self.height() // 2
        size = 12
        # 添加按压效果的偏移
        if self._pressed_section == 0:
            y += int(2 * self._press_animation)
        painter.drawLine(x - size//2, y, x + size//2, y - size)
        painter.drawLine(x - size//2, y, x + size//2, y + size)
        
    def draw_play_pause_icon(self, painter, x):
        y = self.height() // 2
        size = 12
        
        # 添加按压效果的偏移
        if self._pressed_section == 1:
            y += int(2 * self._press_animation)
            
        if self.is_playing:  # 当正在播放时显示暂停图标
            # 绘制暂停图标（两条竖线）
            painter.drawLine(x - size//2, y - size, x - size//2, y + size)
            painter.drawLine(x + size//2, y - size, x + size//2, y + size)
        else:  # 当暂停时显示播放图标
            # 绘制播放图标（三角形）
            points = [
                QPoint(x - size//2, y - size),  # 左上
                QPoint(x - size//2, y + size),  # 左下
                QPoint(x + size, y),            # 右中
            ]
            path = QPainterPath()
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            path.lineTo(points[0])
            painter.fillPath(path, painter.pen().color())
        
    def draw_next_icon(self, painter, x):
        y = self.height() // 2
        size = 12
        # 添加按压效果的偏移
        if self._pressed_section == 2:
            y += int(2 * self._press_animation)
        painter.drawLine(x - size//2, y - size, x + size//2, y)
        painter.drawLine(x - size//2, y + size, x + size//2, y)
        
    def set_opacity(self, value):
        self.opacity = value
        self.update() 