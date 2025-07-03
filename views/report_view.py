
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QPushButton, QFileDialog
)
from PySide6.QtCore import Signal, QDate,Qt
from PySide6.QtGui import QPixmap

class ReportView(QWidget):
    """
    报表模块视图：
     - 上方：开始/结束日期选择 + “生成报表”按钮
     - 中部：两个 QLabel 占位，后由 Controller 设置为热力图/折线图的 QPixmap
     - 底部：导出图片按钮
    """
    generate_requested = Signal(str, str)  # 格式化日期 "YYYY-MM-DD"

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        # —— 日期选择区 —— 
        hl = QHBoxLayout()
        hl.addWidget(QLabel("开始日期："))
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        hl.addWidget(self.start_date)

        hl.addWidget(QLabel("结束日期："))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        hl.addWidget(self.end_date)

        btn_gen = QPushButton("生成报表")
        btn_gen.clicked.connect(self._on_generate_clicked)
        hl.addWidget(btn_gen)
        main_layout.addLayout(hl)

        # —— 报表占位 —— 
        self.heatmap_label   = QLabel("热力图区域")
        self.heatmap_label.setFixedHeight(200)
        self.heatmap_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.heatmap_label)

        self.linechart_label = QLabel("时段折线图区域")
        self.linechart_label.setFixedHeight(200)
        self.linechart_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.linechart_label)

        # —— 导出按钮 —— 
        btn_export = QPushButton("导出为PNG")
        btn_export.clicked.connect(self._export_clicked)
        main_layout.addWidget(btn_export)

    def _on_generate_clicked(self):
        s = self.start_date.date().toString("yyyy-MM-dd")
        e = self.end_date.date().toString("yyyy-MM-dd")
        self.generate_requested.emit(s, e)

    def show_heatmap(self, pixmap: QPixmap):
        """Controller 传入热力图渲染结果"""
        self.heatmap_label.setPixmap(pixmap)

    def show_linechart(self, pixmap: QPixmap):
        """Controller 传入折线图渲染结果"""
        self.linechart_label.setPixmap(pixmap)

    def _export_clicked(self):
        """导出两张图之一（示例导出热力图）"""
        path, _ = QFileDialog.getSaveFileName(self, "保存热力图", "", "PNG Files (*.png)")
        if path and not self.heatmap_label.pixmap().isNull():
            self.heatmap_label.pixmap().save(path)
