from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
import altair as alt

st.set_page_config(layout='wide')


@st.cache_data
def load_data(selected_year):
    files = {
        2023: 'utilities/datasets/2023_load_data_clean.csv',
        2024: 'utilities/datasets/load_data_2024_cleaned.csv'
    }
    data = pd.read_csv(files[selected_year])
    data['datetime'] = pd.to_datetime((data['datetime']), format='%Y-%m-%d %H:%M:%S')
    data.rename(columns={'datetime': '时间'}, inplace=True)
    return data


def load_data_2024():
    data = pd.read_csv('utilities/datasets/load_data_2024_cleaned.csv')
    data['datetime'] = pd.to_datetime((data['datetime']), format='%Y-%m-%d %H:%M:%S')
    data.rename(columns={'datetime': '时间'}, inplace=True)
    return data


def custom_resampler(arraylike):
    return np.sum(arraylike) / (12 * 1000)


def description():
    description, image = st.columns([1, 1], gap='large')

    with description:
        st.markdown('''
        ### 项目介绍

        - 本项目专注于开发智能负荷预测系统，以提升智能电网的能源管理效率。
        - 采用 LSTM（长短期记忆网络）模型，旨在预测每日电力负荷模式，助力高效能源管理。

        #### 项目目标

        1. **实现预测分析：** 基于德里邦调度中心的历史数据，开发并实施 LSTM 模型来预测每日电力负荷模式。

        2. **提升能源管理：** 通过提供电力负荷模式和能源消耗的实时洞察，增强智能电网的能源管理能力。

        3. **设计友好界面：** 设计用户友好的仪表板，提供历史能源消耗和未来负荷预测的实时洞察，
        提升可访问性和实际应用价值。

        #### 主要功能

        - 分析德里邦调度中心（SLDC）2023 年和 2024 年的历史电力负荷数据。
        - 可视化日、周、月负荷曲线，识别趋势和模式。
        - 获取每 5 分钟采集一次的数据，预测未来负荷模式和能源消耗。
        - 机器学习 LSTM 模型基于 SLDC 每 5 分钟采集的历史数据预测每日电力负荷模式。

            ''')
        with st.expander('德里邦调度中心运营地图'):
            map_data = pd.DataFrame({
                'latitude': [28.6139],
                'longitude': [77.2090]
            })  # Latitude and Longitude for Delhi
            st.map(map_data, use_container_width=True)

    with image:
        # st.image('power-line-rounded-modified.png', use_column_width=True)
        st.image('images/smart_grid.png', use_column_width=True)


def year_load(data, selected_year):
    average_daily_load_full_year = int(data['load'].mean())
    cumulative_energy_full_year = int(data['load'].sum())
    cumulative_energy_full_year_GWh = round(cumulative_energy_full_year / (12 * 1000), 2)
    with st.container(border=True):
        average_daily_load_full_year_card, cumulative_energy_full_year_card = st.columns(2, gap='medium')

        with average_daily_load_full_year_card:
            with st.container(border=True):
                st.info('日均负荷')
                st.metric(label='日均负荷',
                          value=str(average_daily_load_full_year) + ' MW',
                          label_visibility='collapsed')
            with st.container(border=True):
                year_data_per_day = data.resample('D', on='时间').median()
                year_data_per_day.rename(columns={'load': '负荷 (MW)'}, inplace=True)
                st.line_chart(data=year_data_per_day, y='负荷 (MW)', use_container_width=True, color='#BED754')
        with cumulative_energy_full_year_card:
            with st.container(border=True):
                st.info('总发电量')
                st.metric(label='总发电量',
                          value=str(cumulative_energy_full_year_GWh) + ' GWh',
                          label_visibility='collapsed')

            with st.container(border=True):
                year_data_per_month = data.resample('M', on='时间').apply(custom_resampler)
                year_data_per_month.rename(columns={'load': '发电量 (GWh)'}, inplace=True)
                st.bar_chart(data=year_data_per_month, y='发电量 (GWh)', use_container_width=True, color='#BED754')


def month_load(data, selected_month):
    month_data = data[data['时间'].dt.month == selected_month]
    average_daily_load = int(month_data['load'].mean())
    average_daily_load_delta = int(average_daily_load - data['load'].mean())
    average_daily_load_delta_percentage = round(average_daily_load_delta / average_daily_load * 100, 2)

    cumulative_energy_per_month = data.resample('M', on='时间').sum()
    cumulative_month_energy = int(month_data['load'].sum())
    cumulative_month_energy_GWh = round(cumulative_month_energy / (12 * 1000), 2)
    cumulative_month_energy_delta = int(cumulative_month_energy - cumulative_energy_per_month['load'].mean())
    cumulative_month_energy_delta_percentage = round(cumulative_month_energy_delta / cumulative_month_energy * 100, 2)

    with st.container(border=True):
        average_month_load_card, cumulative_month_energy_card = st.columns(2, gap='medium')
        with average_month_load_card:
            with st.container(border=True):
                st.info('日均负荷')
                st.metric(label='日均负荷',
                          value=str(average_daily_load) + ' MW',
                          delta=str(average_daily_load_delta_percentage) + ' %',
                          label_visibility='collapsed')

            with st.container(border=True):
                month_data_resampled_H = month_data.resample('H', on='时间').median()
                month_data_resampled_H.rename(columns={'load': '负荷 (MW)'}, inplace=True)
                # st.line_chart(data=monthly_data, x='datetime', y='load', width=300, color='#f8007a')
                # st.line_chart(data=monthly_data, x='datetime', y='Load in MW', width=300)
                st.line_chart(data=month_data_resampled_H, y='负荷 (MW)')

        with cumulative_month_energy_card:
            with st.container(border=True):
                st.info('当月总发电量')
                st.metric(label='当月总发电量',
                          value=str(cumulative_month_energy_GWh) + ' GWh',
                          delta=str(cumulative_month_energy_delta_percentage) + ' %',
                          label_visibility='collapsed')
            with st.container(border=True):
                month_data_resampled_D = month_data.resample('D', on='时间').apply(custom_resampler)
                month_data_resampled_D.rename(columns={'load': '发电量 (GWh)'}, inplace=True)
                # st.bar_chart(monthly_data, color='#f95959')
                st.bar_chart(data=month_data_resampled_D, y='发电量 (GWh)')


def day_load(data, selected_date):
    # Filter data for the selected date
    selected_data = data[data['时间'].dt.date == selected_date]
    selected_data.rename(columns={'load': '负荷 (MW)'}, inplace=True)
    # st.dataframe(selected_data)
    # selected_data.to_excel('selected_data.xlsx')
    # print(selected_data.head())
    st.line_chart(data=selected_data, x='时间', y='负荷 (MW)', use_container_width=True, color='#ff8011')


def load_prediction():
    predicted_data = pd.read_excel('utilities/datasets/selected_data.xlsx')
    predicted_data.drop(columns=['Unnamed: 0'], inplace=True)
    predicted_data.rename(columns={'Load in MW': '实际负荷 (MW)', 'load': '预测负荷 (MW)', 'datetime': '时间'}, inplace=True)
    # predicted_data = predicted_data.set_index('datetime')
    print(predicted_data.head())
    # st.dataframe(predicted_data)

    with st.container(border=True):
        actual_graph, predicted_graph = st.columns(2, gap='medium')

        with actual_graph:
            with st.container(border=True):
                st.markdown('#### 实际负荷')
                st.line_chart(data=predicted_data, x='时间',
                              y="实际负荷 (MW)",
                              color=['#ff8011'], use_container_width=True)
        with predicted_graph:
            with st.container(border=True):
                st.markdown('#### 预测负荷')
                st.line_chart(data=predicted_data, x='时间',
                              y="预测负荷 (MW)",
                              color=["#83c9ff"],
                              use_container_width=True)

        actual_vs_predicted_graph, prediction_metrics = st.columns(2, gap='medium')
        with actual_vs_predicted_graph:
            with st.container(border=True):
                st.markdown('#### 实际负荷 vs 预测负荷')
                st.line_chart(data=predicted_data, x='时间',
                              y=["实际负荷 (MW)", "预测负荷 (MW)"],
                              color=['#ff8011', '#83c9ff'], use_container_width=True)

        with prediction_metrics:
            RMSE = round(np.sqrt(np.mean((predicted_data['实际负荷 (MW)'] - predicted_data['预测负荷 (MW)']) ** 2)),
                         3)
            MAE = round(np.mean(np.abs(predicted_data['实际负荷 (MW)'] - predicted_data['预测负荷 (MW)'])), 3)
            MAPE = round(np.mean(np.abs(
                (predicted_data['实际负荷 (MW)'] - predicted_data['预测负荷 (MW)']) / predicted_data[
                    '实际负荷 (MW)'])), 3) * 100
            accuracy = round(100 - MAPE, 3)
            with st.container(border=True):
                st.markdown('#### 预测指标')
                col1, col2 = st.columns(2, gap='small')
                with col1:
                    with st.container(border=True):
                        st.info('RMSE (均方根误差)')
                        st.metric(label='RMSE',
                                  value=str(RMSE) + ' MW',
                                  label_visibility='collapsed')
                    with st.container(border=True):
                        st.info('MAE (平均绝对误差)')
                        st.metric(label='MAE',
                                  value=str(MAE) + ' MW',
                                  label_visibility='collapsed')

                with col2:
                    with st.container(border=True):
                        st.info('MAPE (平均绝对百分比误差)')
                        st.metric(label='MAPE',
                                  value=str(MAPE) + ' %',
                                  label_visibility='collapsed')
                    with st.container(border=True):
                        st.info('准确率')
                        st.metric(label='准确率',
                                  value=str(accuracy) + ' %',
                                  label_visibility='collapsed')


@st.cache_data
def get_min_max_date(data):
    min_date = data['时间'].min().date()
    max_date = data['时间'].max().date()
    return min_date, max_date


# data_2024 = load_data_2024()

st.title('智能电网负荷预测系统 - 智慧能源管理')
st.markdown('---')
description()

st.sidebar.header('数据选择')
st.markdown('---')

# Year-wise load
st.header('年度负荷曲线')
with st.sidebar:
    selected_year = st.selectbox('选择年份', [2023, 2024])

data = load_data(selected_year)
year_load(data, selected_year)
st.markdown('---')

# Month-wise load
st.header('月度负荷曲线')

with st.sidebar:
    selected_month = st.selectbox('选择月份', data['时间'].dt.month.unique())
month_load(data, selected_month)
st.markdown('---')

# Day-wise load
st.header('日度负荷曲线')
with st.sidebar:
    min_date, max_date = get_min_max_date(data)
    default_date = min_date + (max_date - min_date) // 2
    selected_date = st.date_input('选择日期', default_date, min_value=min_date, max_value=max_date)
day_load(data, selected_date)

st.markdown('---')

# Load Prediction
st.header('负荷预测')
load_prediction()



