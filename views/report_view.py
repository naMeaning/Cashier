
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QPushButton, QFileDialog,QSizePolicy
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
        # 主布局：垂直
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        # —— 顶部：日期选择 + 生成按钮 —— 
        date_layout = QHBoxLayout()
        date_layout.setSpacing(8)
        date_layout.addWidget(QLabel("开始日期："))
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(QLabel("结束日期："))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)

        btn_gen = QPushButton("生成报表")
        btn_gen.clicked.connect(self._on_generate_clicked)
        date_layout.addWidget(btn_gen)

        date_layout.addStretch()   # 右侧留白
        main_layout.addLayout(date_layout)

        # —— 中部：两个图表并排 —— 
        chart_layout = QHBoxLayout()
        chart_layout.setSpacing(12)

        # 热力图
        self.heatmap_label = QLabel()
        self.heatmap_label.setAlignment(Qt.AlignCenter)
        self.heatmap_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        chart_layout.addWidget(self.heatmap_label)

        # 折线图
        self.linechart_label = QLabel()
        self.linechart_label.setAlignment(Qt.AlignCenter)
        self.linechart_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        chart_layout.addWidget(self.linechart_label)

        main_layout.addLayout(chart_layout, stretch=1)

        # —— 底部：导出按钮右对齐 —— 
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        btn_export = QPushButton("导出为PNG")
        btn_export.clicked.connect(self._export_clicked)
        export_layout.addWidget(btn_export)
        main_layout.addLayout(export_layout)

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
