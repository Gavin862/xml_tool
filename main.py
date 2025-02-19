import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QLabel, QFrame, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QFileDialog, QWidget
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
import math

class DraggableImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.dragging = False
        self.offset = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()  # 记录鼠标点击位置相对于图片左上角的偏移
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            # 计算图片的新位置
            new_pos = self.mapToParent(event.pos() - self.offset)
            
            # 限制图片拖动范围，确保图片不会拖出父控件
            new_pos.setX(max(0, min(new_pos.x(), self.parent().width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), self.parent().height() - self.height())))
            
            self.move(new_pos)  # 移动图片

            # 计算线条的起点和终点
            line_start = self.pos() + QPoint(self.width() // 2, 0)  # 图片中心点
            line_end = QPoint((new_pos.x()) + (self.width()//2), 0)  # 父控件中心点
            y_line_start = self.pos() + QPoint(0, self.height() // 2)  # 图片中心点
            y_line_end = QPoint(0, (new_pos.y()) + (self.height()//2))  # 父控件中心点
            # 通知父控件更新线条
            if isinstance(self.parent(), CustomFrame):
                self.parent().setLinePoints(line_start, line_end, y_line_start, y_line_end)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)

    def focusOutEvent(self, event: QMouseEvent):
        if isinstance(self.parent(), CustomFrame):
                self.parent().ClearLinePoints()
                
class CustomFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_start = QPoint()  # 线条起点
        self.line_end = QPoint()  # 线条终点
        self.y_line_start = QPoint()
        self.y_line_end = QPoint()

    def setLinePoints(self, start, end, y_start, y_end):
        # 设置线条的起点和终点
        self.line_start = start
        self.line_end = end
        self.y_line_start = y_start
        self.y_line_end = y_end
        self.update()  # 触发重绘

    def ClearLinePoints(self):
        self.line_start = QPoint(0, 0)
        self.line_end = QPoint(1, 0)
        self.y_line_start = QPoint(1, 0)
        self.y_line_end = QPoint(1, 0)
        self.update()  # 触发重绘

    def paintEvent(self, event):
        super().paintEvent(event)
        # 在父控件中绘制线条
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))  # 设置线条颜色和宽度
        painter.drawLine(self.line_start, self.line_end)  # 绘制线条
        painter.drawLine(self.y_line_start, self.y_line_end)  # 绘制线条
    
        # 计算线条长度
        dx = self.y_line_end.x() - self.y_line_start.x()
        dy = self.line_end.y() - self.line_start.y()
        
        # # 在水平线条右侧显示X距离
        # font = painter.font()
        # font.setPointSize(12)
        # painter.setFont(font)
        # x_text = f"X: {dx}px"
        # x_text_width = painter.fontMetrics().width(x_text)
        # x_text_height = painter.fontMetrics().height()
        # x_text_x = max(self.line_end.x(), self.line_start.x()) + 10
        # x_text_y = (self.line_end.y() + self.line_start.y()) / 2 + x_text_height / 4
        # painter.drawText(x_text_x, x_text_y, x_text)
        
        # # 在垂直线条下方显示Y距离
        # y_text = f"Y: {dy}px"
        # y_text_x = (self.y_line_end.x() + self.y_line_start.x()) / 2 - painter.fontMetrics().width(y_text) / 2
        # y_text_y = max(self.y_line_end.y(), self.y_line_start.y()) + 20
        # painter.drawText(y_text_x, y_text_y, y_text)

class FileHandling(QWidget):
    def __init__(self, parent=None):
        self.button = QPushButton("打开文件夹", self)
        self.button.clicked.connect(self.open_folder)  # 绑定按钮点击事件
        
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            print(f"选择的文件夹路径: {folder_path}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口大小为2040x780
        self.setGeometry(100, 100, 2040, 780)

        # 创建一个自定义的 QFrame
        self.frame = CustomFrame(self)
        self.frame.setFrameStyle(QFrame.Box | QFrame.Raised)  # 设置边框样式
        # 设置 QFrame 的位置和大小
        self.frame.setGeometry(240, 20, 1560, 720)  # x, y, width, height

        # 设置背景颜色
        self.frame.setStyleSheet("background-color: rgb(200, 200, 200);")

        # 创建可拖动的图片控件
        self.image_label = DraggableImage(self.frame)
        pixmap = QPixmap(r"pic\test.png")  # 替换为你的图片路径
        if pixmap.isNull():
            print("图片加载失败，请检查路径是否正确。")
        else:
            self.image_label.setPixmap(pixmap)
            self.image_label.resize(pixmap.size())  # 调整QLabel大小为图片大小

        # 将图片控件添加到 QFrame 中
        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.image_label, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.frame.setLayout(layout)
        # 设置图片初始位置为距离左边100像素，距离上边100像素
        self.image_label.move(500, 100)

        # 创建一个QListWidget控件
        self.list_widget = QListWidget(self)
        # 设置QListWidget的大小为200x740
        self.list_widget.setGeometry(20, 20, 200, 650)
          # 添加一些示例项到QListWidget中
        self.list_widget.addItems(["Item 1", "Item 2", "Item 3", "Item 4"])

        #self.button = FileHandling(self)
        self.button = QPushButton("打开文件夹", self)
        self.button.setGeometry(20,690,200,40)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
