# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个智能电力负荷预测系统，用于智能电网的能源管理。项目使用 LSTM 模型基于德里邦调度中心（Delhi SLDC）的历史数据进行短期负荷预测。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 Streamlit 应用
streamlit run app.py

# 使用 Jupyter Notebook 进行模型训练和数据分析
# 打开 utilities/jupyter-notebook/load-forecasting.ipynb
```

## 项目架构

- **app.py**: Streamlit Web 应用，负责数据可视化，提供年/月/日负荷曲线展示和预测结果展示
- **scripts/data-scraping.py**: 数据抓取脚本，从德里邦调度中心网站抓取电力负荷数据
- **utilities/datasets/**: 训练数据集（2023、2024年数据）
- **utilities/jupyter-notebook/load-forecasting.ipynb**: Jupyter Notebook，包含 LSTM 模型训练代码和数据分析
- **utilities/datasets/selected_data.xlsx**: 预测结果数据，用于 app.py 中的预测展示

## 技术栈

- **前端/可视化**: Streamlit, Altair, Matplotlib
- **数据处理**: Pandas, NumPy, OpenPyXL
- **机器学习**: TensorFlow, Keras (LSTM)
- **数据抓取**: BeautifulSoup4, requests

## 数据说明

- 数据来源：Delhi State Load Dispatch Centre (https://www.delhisldc.org/)
- 数据采样间隔：5分钟
- 预测目标：根据过去10天数据预测未来24小时负荷
- 模型评估指标：RMSE, MAE, MAPE, Accuracy
