# controllers/report_controller.py

import pandas as pd
import matplotlib.pyplot as plt
import io
from PySide6.QtCore import Slot
from PySide6.QtGui  import QPixmap
from models.transaction_model import Transaction
import json
from models.product_model import Product

plt.rcParams['font.sans-serif'] = ['SimHei']      # 指定中文字体
plt.rcParams['axes.unicode_minus'] = False        # 负号正常显示

class ReportController:
    """
    ReportController 负责：
      - 响应日期范围信号
      - 从 DB 拉取交易数据到 pandas.DataFrame
      - 生成热力图 & 时段折线图
      - 转成 QPixmap 后传给视图
    """
    def __init__(self, SessionFactory, view):
        """
        :param SessionFactory: sessionmaker
        :param view: ReportView 实例
        """
        self.SessionFactory = SessionFactory
        self.view = view
        self.view.generate_requested.connect(self.on_generate)

    @Slot(str, str)
    def on_generate(self, start: str, end: str):
        """
        1. 拉取 start~end 之间的交易数据
        2. 构造 DataFrame：columns=["product_id","quantity","amount","timestamp"]
        3. 生成热力图：产品 vs 日期 销量
        4. 生成折线图：按小时或天聚合总销售额
        5. 转 QPixmap 并传给 view
        """
        
            # 1) 拉取数据并展开成行记录
        session = self.SessionFactory()
        try:
            records = []
            txs = session.query(Transaction) \
                         .filter(Transaction.timestamp.between(start, end)) \
                         .all()
            for t in txs:
                items = json.loads(t.items_json)  # {"1":2, "3":1, ...}
                for pid_str, qty in items.items():
                    pid = int(pid_str)
                    prod = session.get(Product, pid)
                    if not prod:
                        continue
                    records.append({
                        "product_name": prod.name,
                        "quantity":     qty,
                        "amount":       qty * prod.price,
                        "date":         pd.to_datetime(t.timestamp).date(),
                        "hour":         pd.to_datetime(t.timestamp).hour
                    })
        finally:
            session.close()
            
            
        df = pd.DataFrame(records)
        if df.empty:
            # 没数据时清空视图
            self.view.show_heatmap(QPixmap())
            self.view.show_linechart(QPixmap())
            return

        # 2) 生成热力图
        #    以“商品名称 vs 日期”为透视表，值=quantity
        pivot = df.pivot_table(
            index="product_name",
            columns="date",
            values="quantity",
            aggfunc="sum",
            fill_value=0
        )

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        cax = ax1.imshow(pivot, aspect='auto')
        ax1.set_xticks(range(len(pivot.columns)))
        ax1.set_xticklabels([d.strftime("%Y-%m-%d") for d in pivot.columns],
                            rotation=45, ha='right')
        ax1.set_yticks(range(len(pivot.index)))
        ax1.set_yticklabels(pivot.index)
        ax1.set_xlabel("日期")
        ax1.set_ylabel("商品")
        ax1.set_title("销售数量热力图")
        fig1.colorbar(cax, ax=ax1, label="数量")
        fig1.tight_layout()

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format='png')
        buf1.seek(0)
        pixmap1 = QPixmap()
        pixmap1.loadFromData(buf1.getvalue())
        plt.close(fig1)

        # 3) 生成时段折线图
        hourly = df.groupby("hour")["amount"].sum()
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.plot(hourly.index, hourly.values, marker='o')
        ax2.set_xticks(hourly.index)
        ax2.set_xlabel("小时")
        ax2.set_ylabel("销售额（元）")
        ax2.set_title("各时段销售额折线图")
        fig2.tight_layout()

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format='png')
        buf2.seek(0)
        pixmap2 = QPixmap()
        pixmap2.loadFromData(buf2.getvalue())
        plt.close(fig2)

        # 4) 回传给视图显示
        self.view.show_heatmap(pixmap1)
        self.view.show_linechart(pixmap2)