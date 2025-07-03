# 便利店收银系统 (Cashier System)

一个基于 **Python**、**PySide6** 和 **SQLAlchemy** 的通用便利店收银系统，支持商品管理、购物结算、库存监控、会员管理和销售报表。

---

## 功能概览

1. **商品管理**  
   - 扫描商品、分类检索  
   - 价格调整  
   - 商品图像展示  

2. **支付处理**  
   - 现金、移动支付、积分支付、储值卡支付  
   - 自动计算找零  
   - 消费后自动发放积分（1 积分 = 0.1 元）  

3. **库存监控**  
   - 实时显示当前库存  
   - 库存阈值预警、自动日志  
   - 手动增减库存  

4. **会员管理**  
   - 新增/删除会员  
   - 充值、积分兑换  
   - 余额与积分实时更新  

5. **数据分析**  
   - 销售热力图（商品×日期）  
   - 时段销售额折线图  
   - 支持导出为 PNG  

---

## 项目结构

cashier_system/
├── controllers/ # MVC 控制器
├── models/ # SQLAlchemy ORM 模型
├── views/ # PySide6 界面定义
├── resources/ # 静态资源 (images/ui)
├── main.py # 程序入口
├── seed_products.py # 生成测试数据脚本
├── requirements.txt # 依赖列表
└── README.md # 本文档

---

## 快速开始

1. **克隆仓库**

   ```bash
   git clone git@github.com:你的用户名/CashierSystem.git
   cd CashierSystem
2.创建虚拟环境 & 安装依赖

conda create -n cashier python=3.9
conda activate cashier
pip install -r requirements.txt

3. 准备测试数据
python seed_products.py

运行程序
python main.py
