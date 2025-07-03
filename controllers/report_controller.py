# controllers/report_controller.py

import pandas as pd
import matplotlib.pyplot as plt
import io
from PySide6.QtCore import Slot
from PySide6.QtGui  import QPixmap
from models.transaction_model import Transaction

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
        # 1) 读取数据
        session = self.SessionFactory()
        try:
            # Transaction.record() 假设存了 transaction.id, pid->qty dict, total, pay_type, timestamp
            rows = []
            for t in session.query(Transaction).filter(Transaction.timestamp.between(start, end)).all():
                for pid, qty in t.items_sold.items():
                    rows.append({
                        "product_id": pid,
                        "quantity":   qty,
                        "amount":     qty * t.unit_price_map[pid],  # 假设模型里有单价映射
                        "timestamp":  t.timestamp
                    })
        finally:
            session.close()

        df = pd.DataFrame(rows)
        if df.empty:
            # 没数据时清空视图并警告
            self.view.heatmap_label.clear()
            self.view.linechart_label.clear()
            return

        # 2) 热力图：按产品 vs 日期 透视
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        pivot = df.pivot_table(
            index="product_id", columns="date", values="quantity", aggfunc="sum", fill_value=0
        )

        fig1, ax1 = plt.subplots()
        # 不指定颜色，由 matplotlib 默认
        cax = ax1.imshow(pivot, aspect="auto")
        ax1.set_xticks(range(len(pivot.columns)))
        ax1.set_xticklabels(pivot.columns, rotation=45, ha="right")
        ax1.set_yticks(range(len(pivot.index)))
        ax1.set_yticklabels(pivot.index)
        ax1.set_title("各产品每日销售热力图")
        fig1.colorbar(cax, ax=ax1)
        # 转 QPixmap
        buf = io.BytesIO()
        fig1.tight_layout()
        fig1.savefig(buf, format="png")
        buf.seek(0)
        pixmap1 = QPixmap()
        pixmap1.loadFromData(buf.getvalue())
        plt.close(fig1)

        # 3) 折线图：按小时聚合总销售额
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        line = df.groupby("hour")["amount"].sum()
        fig2, ax2 = plt.subplots()
        ax2.plot(line.index, line.values)
        ax2.set_xlabel("小时")
        ax2.set_ylabel("销售额")
        ax2.set_title("各时段总销售额")
        buf2 = io.BytesIO()
        fig2.tight_layout()
        fig2.savefig(buf2, format="png")
        buf2.seek(0)
        pixmap2 = QPixmap()
        pixmap2.loadFromData(buf2.getvalue())
        plt.close(fig2)

        # 4) 把图传给 View
        self.view.show_heatmap(pixmap1)
        self.view.show_linechart(pixmap2)
