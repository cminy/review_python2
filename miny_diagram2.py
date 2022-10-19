# -*- coding: utf-8 -*-
"""miny_diagram2.ipynb
Automatically generated by Colaboratory.
Original file is located at
    https://colab.research.google.com/drive/1JH7zILjtdbNC-3LJLGWeqgpm69T8qOVN
"""

# 라이브러리 설치 및 한글폰트 설치
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
from colorspacious import cspace_convert
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import plotly
import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
import warnings
warnings.filterwarnings(action='ignore')

# !pip install colorspacious
# !pip install plotly
# !pip install dash

# 원본불러오기
miny = pd.read_csv(
    '/Users/suuup/Desktop/newminy/cminydev22/cminy_personal/minyref_for_diagram.csv')

miny.months = miny.months.astype('int')


# (1) 주요 사용 툴
temparr = miny.how.tolist()
codes = []
tools = []
# miny.how.values
for i, t in enumerate(miny.how):
    for v in t.split(', '):
        tools.append(v)
        codes.append(miny.iloc[i, 0])

df_how = pd.DataFrame({
    'code': codes,
    'how': tools
})

df_how.loc[(df_how.how.str.startswith('HTML')) | (df_how.how == "CSS")
           | (df_how.how == "JS"), 'how'] = 'HTML/JSX/JS/CSS'
dfhowc = df_how.groupby('how').agg(c=('how', 'count')).sort_values(
    'c', ascending=False).reset_index()
dfhowc.loc[dfhowc.c > 1, :].sort_values('c')


# (3) for 프로젝트별 scatter polar chart
df = miny.copy()
df.under2018.unique()
df['under2018'] = np.where(df.under2018 == 1, ' ~ 2017', '2018 ~ 2022')
df.under2018

df['start'] = pd.to_datetime(df['start'])
df['end'] = pd.to_datetime(df['end'])
df['year'] = df.start.dt.year
df = df.fillna("")


code_all = []
what_all = []
for i in df.loc[df['what'] != "", :].index:
    if "," in df.what[i]:
        a = df.what[i].split(', ')
        for _ in a:
            code_all.append(df.code[i])
            what_all.append(_)
    else:
        code_all.append(df.code[i])
        what_all.append(df.what[i])

codewhat = pd.DataFrame({'code': code_all,
                         'what': what_all
                         })


df1 = pd.merge(codewhat, df.loc[df['what'] != "", [
               'code', 'name', 'under2018', 'year', 'months']], how='left', on='code')
df1.loc[(df1.what == '운영') | (df1.what == '지원'), 'what'] = '운영/지원'


df_whatnum = df1.groupby('what').agg(num=('code', 'count')).sort_values('num')
df_num = df_whatnum.sort_values('num', ascending=False)

# (3) polar bar chart
df2 = pd.DataFrame({'code': df.code,
                    'name': df.name,
                    'name2': df.name_kr,
                    'months': df.months,
                    'under2018': df.under2018})
for c in ['DB', '웹개발', '콘텐츠제작', '마케팅', '기획', '운영/지원', '개선', '체계화']:
    df2[c] = 0

for c in df2.columns[2:]:
    arr = df1.loc[df1.what == c, 'code'].tolist()
    for v in arr:
        df2.loc[df2.code == v, c] = df2.loc[df2.code == v, 'months'] / 12
df2 = df2.assign(whatsum=df2.loc[:, df2.columns[5:]].sum(axis=1))
df3 = df2.loc[df2['whatsum'] > 0, df2.columns[:-1]]


df_radar2 = df3.iloc[:, :5]
df_radar2
new_cols = df3.columns[:5].tolist() + df_num.index.tolist()

for col in new_cols[5:]:
    df_radar2[col] = df3[col]

# (4) work with
miny.loc[miny['with'] != "", ['code', 'with']].values


codes = []
wwiths = []
for i in df.loc[df['with'] != "", ['code', 'with']].values:
    for v in i[1].split(', '):
        codes.append(i[0])
        wwiths.append(v)

df_with = pd.DataFrame({
    'code': codes,
    'wwith': wwiths
})

df_withm = pd.merge(
    df_with, miny.loc[:, ['code', 'months']], how='left', on='code')
df_withm.head()

df_withc = df_withm.groupby('wwith').agg(sumw=('wwith', 'count'),
                                         summ=('months', 'sum')).reset_index()
df_withc = pd.concat(
    [df_withc.iloc[:3, :], df_withc.iloc[6:, :], df_withc.iloc[3:6, :]])


##
##
##
##
# Final : 그래프 4개 합치기
##
# # Initialize figure with subplots
# fig = make_subplots(
#     rows=4, cols=2,
#     column_widths=[0.5, 0.55],
#     vertical_spacing=0.1,
#     # row_heights=[0.6, 0.4],
#     specs=[[{"type": "bar", "rowspan": 2}, {"type": "polar"}],
#            [None, {"type": "polar", "rowspan": 3}],
#            [{"type": "scatter", "rowspan": 2}, None],
#            [None, None]],
#     #    [{"type": "polar", "colspan":2},   None  ,   None ]],
#     subplot_titles=("주요 사용 툴", "업무별 프로젝트 수", "프로젝트별 업무분야", "함께 일한 사람들")
# )
#
# # colors
# # line color : '#d6cab2'
# c = ['#c9ba9b', '#bdaa84', '#b09a6c', '#a28957',
#      '#8b754a', '#74623e', '#5c4e31', '#453a25', '#2e2718']
# bg_color = 'rgb(223, 223, 223)'
#
# # [1,1] 주요 사용 툴 그래프
# fig.add_trace(go.Bar(
#     x=dfhowc.sort_values('c').c.values,
#     y=dfhowc.sort_values('c').how.values,
#     marker=dict(color=c[-3], line_width=1, line_color='#d6cab2'),
#     # opacity = 0.4,
#     orientation='h',
#     showlegend=False,
# ), row=1, col=1)
#
# fig.update_layout(
#     xaxis=dict(
#         showline=False,
#         gridwidth=0,
#         range=[0, 12]
#     ),
#     yaxis=dict(
#         visible=True,
#         showline=True,
#         linecolor=c[-1],
#         gridwidth=0,
#     ),
#     plot_bgcolor=bg_color,
# )
#
#
# # [1,2] 업무분야별 프로젝트 수
# df_num = df_num.sort_values('num', ascending=True)
# w_78 = [2.95, 3.11]
# for i, v in enumerate(df_num.num):
#     if i in [7, 8]:
#         w = w_78[i - 6]
#         x = w / 2
#     else:
#         w = np.pi * v / 12
#         x = (np.pi * v) / 24
#
#     fig.add_trace(go.Barpolar(
#         r=[1],
#         width=90 * w,
#         marker=dict(color=[c[i]], line_width=2, line_color='#d6cab2'),
#         name=df_num.index[i],
#
#         hoverinfo=['text'],
#         hovertext=df_num.index[i] + ": " + str(v) + " projects",
#         hoverlabel=dict(align='left', namelength=-1),
#
#         showlegend=False,
#     ))
#
# fig.update_layout(
#     polar=dict(
#         angularaxis=dict(
#             visible=False,
#             showline=False,
#             rotation=180,
#         ),
#         radialaxis=dict(
#             visible=True,
#             gridcolor='rgb(223, 223, 223)',
#
#             showline=True,
#             linecolor='#d6cab2',
#             linewidth=2,
#
#             ticks='',
#             tickmode='array',
#             ticktext=df_num.index.tolist(),
#             tickfont=dict(size=10),
#             tickvals=[0.7, 1.7, 2.7, 3.7, 4.7, 5.7, 6.7, 7.7],
#             tickangle=-220,
#             tickwidth=0.5,
#
#             range=[0, 8],
#             angle=180,
#
#             side='counterclockwise'
#         ),
#         hole=0.1,
#         sector=[0, 180],
#         bgcolor=bg_color
#     ))
#
#
# # [2,2] 프로젝트별 업무분야
# for i, v in enumerate(df_radar2.name2):
#     fig.add_trace(go.Scatterpolargl(
#         r=df_radar2.iloc[i, 5:].tolist() + [df_radar2.iloc[i, 5]],
#         theta=df_radar2.columns[5:].tolist() + [df_radar2.columns[5]],
#         name=df_radar2.iloc[i, 0] + ' ' + v,
#
#         # ['none', 'tozeroy', 'tozerox', 'tonexty', 'tonextx', 'toself', 'tonext']
#         fill='tonext',
#         opacity=0.4,
#         line=dict(width=5, shape='linear',
#                   color=px.colors.qualitative.Prism[:-1:1][i % 8]),
#         marker=dict(size=2),
#         hoverinfo=['r', 'theta', 'name'],
#         hovertemplate='for %{r:.1f} year : %{theta}',
#         hoverlabel=dict(align='left', namelength=-1),
#
#         showlegend=True,
#         subplot='polar2'
#     ), row=2, col=2)
#
# fig.update_layout(polar2=dict(
#     bgcolor=bg_color,
#     angularaxis=dict(
#         linewidth=1,
#         showline=True,
#         linecolor='darkgrey',
#         rotation=180,
#         direction='clockwise'
#     ),
#     radialaxis=dict(
#         visible=False,
#         showline=True,
#         linewidth=.5,
#         range=[0, 2]
#     ),
# ))
#
# # [3,1] 함께 일한 사람들
# fig.add_trace(go.Scatter(
#     x=df_withc.wwith,
#     y=df_withc.sumw,
#     # [0.17,0.2,0.18,0.15,0.15,0.13,0.18,0.13],
#     mode='markers',
#     text=df_withc.wwith.values.tolist(),
#     marker=dict(size=df_withc.summ.values * 1,
#                 color=c[::-1]),
#     showlegend=False
# ), row=3, col=1)
#
# fig.update_layout(
#     xaxis2=dict(
#         showline=True,
#         linecolor=c[-1],
#         # ['-', 'linear', 'log', 'date', 'category','multicategory']
#         type='category',
#         showspikes=True,
#     ),
#     yaxis2=dict(
#         visible=False,
#         type='linear',
#         gridwidth=0,
#     ),
#     plot_bgcolor=bg_color,
# )
#
#
# # layout 업데이트
# fig.update_layout(
#     height=1000, width=1500,
#     title_text="miny Projects",
#     margin=dict(r=40, b=30, l=40),
#     font=dict(size=12, color='#252521'),
#     paper_bgcolor=bg_color
# )
#
# fig.show()

##
##
##
##
##
##
##
# with Dash
app = Dash(__name__)


app.layout = html.Div([
    html.H4('Live adjustable subplot-height'),
    dcc.Graph(id="graph"),
    html.P("Subplots height:"),
    dcc.Slider(
        id='slider-height', min=.1, max=.9,
        value=0.5, step=0.1)
])


@app.callback(
    Output("graph", "figure"),
    Input("slider-height", "value"))
def customize_width(top_height):
    # Initialize figure with subplots
    fig = make_subplots(
        rows=4, cols=2,
        column_widths=[0.5, 0.55],
        row_heights=[top_height / 2, top_height / 2,
                     (1 - top_height) / 2, (1 - top_height) / 2],
        # vertical_spacing = 0.1,
        specs=[[{"type": "bar", "rowspan": 2}, {"type": "polar"}],
               [None, {"type": "polar", "rowspan": 3}],
               [{"type": "scatter", "rowspan": 2}, None],
               [None, None]],
        #    [{"type": "polar", "colspan":2},   None  ,   None ]],
        subplot_titles=("주요 사용 툴", "업무별 프로젝트 수", "프로젝트별 업무분야", "함께 일한 사람들")
    )

    # colors
    # line color : '#d6cab2'
    c = ['#c9ba9b', '#bdaa84', '#b09a6c', '#a28957',
         '#8b754a', '#74623e', '#5c4e31', '#453a25', '#2e2718']
    bg_color = 'rgb(223, 223, 223)'

    # [1,1] 주요 사용 툴 그래프
    fig.add_trace(go.Bar(
        x=dfhowc.sort_values('c').c.values,
        y=dfhowc.sort_values('c').how.values,
        marker=dict(color=c[-3], line_width=1, line_color='#d6cab2'),
        # opacity = 0.4,
        orientation='h',
        showlegend=False,
    ), row=1, col=1)

    fig.update_layout(
        xaxis=dict(
            showline=False,
            gridwidth=0,
            range=[0, 12]
        ),
        yaxis=dict(
            visible=True,
            showline=True,
            linecolor=c[-1],
            gridwidth=0,
        ),
        plot_bgcolor=bg_color,
    )

    # [1,2] 업무분야별 프로젝트 수
    df_num = df_num.sort_values('num', ascending=True)
    w_78 = [2.95, 3.11]
    for i, v in enumerate(df_num.num):
        if i in [7, 8]:
            w = w_78[i - 6]
            x = w / 2
        else:
            w = np.pi * v / 12
            x = (np.pi * v) / 24

        fig.add_trace(go.Barpolar(
            r=[1],
            width=90 * w,
            marker=dict(color=[c[i]], line_width=2, line_color='#d6cab2'),
            name=df_num.index[i],

            hoverinfo=['text'],
            hovertext=df_num.index[i] + ": " + str(v) + " projects",
            hoverlabel=dict(align='left', namelength=-1),

            showlegend=False,
        ))

    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                visible=False,
                showline=False,
                rotation=180,
            ),
            radialaxis=dict(
                visible=True,
                gridcolor='rgb(223, 223, 223)',

                showline=True,
                linecolor='#d6cab2',
                linewidth=2,

                ticks='',
                tickmode='array',
                ticktext=df_num.index.tolist(),
                tickfont=dict(size=10),
                tickvals=[0.7, 1.7, 2.7, 3.7, 4.7, 5.7, 6.7, 7.7],
                tickangle=-220,
                tickwidth=0.5,

                range=[0, 8],
                angle=180,

                side='counterclockwise'
            ),
            hole=0.1,
            sector=[0, 180],
            bgcolor=bg_color
        ))

    # [2,2] 프로젝트별 업무분야
    for i, v in enumerate(df_radar2.name2):
        fig.add_trace(go.Scatterpolargl(
            r=df_radar2.iloc[i, 5:].tolist() + [df_radar2.iloc[i, 5]],
            theta=df_radar2.columns[5:].tolist() + [df_radar2.columns[5]],
            name=df_radar2.iloc[i, 0] + ' ' + v,

            # ['none', 'tozeroy', 'tozerox', 'tonexty', 'tonextx', 'toself', 'tonext']
            fill='tonext',
            opacity=0.4,
            line=dict(width=5, shape='linear',
                      color=px.colors.qualitative.Prism[:-1:1][i % 8]),
            marker=dict(size=2),
            hoverinfo=['r', 'theta', 'name'],
            hovertemplate='for %{r:.1f} year : %{theta}',
            hoverlabel=dict(align='left', namelength=-1),

            showlegend=True,
            subplot='polar2'
        ), row=2, col=2)

    fig.update_layout(polar2=dict(
        bgcolor=bg_color,
        angularaxis=dict(
            linewidth=1,
            showline=True,
            linecolor='darkgrey',
            rotation=180,
            direction='clockwise'
        ),
        radialaxis=dict(
            visible=False,
            showline=True,
            linewidth=.5,
            range=[0, 2]
        ),
    ))

    # [3,1] 함께 일한 사람들
    fig.add_trace(go.Scatter(
        x=df_withc.wwith,
        y=df_withc.sumw,
        # [0.17,0.2,0.18,0.15,0.15,0.13,0.18,0.13],
        mode='markers',
        text=df_withc.wwith.values.tolist(),
        marker=dict(size=df_withc.summ.values * 1,
                    color=c[::-1]),
        showlegend=False
    ), row=3, col=1)

    fig.update_layout(
        xaxis2=dict(
            showline=True,
            linecolor=c[-1],
            # ['-', 'linear', 'log', 'date', 'category','multicategory']
            type='category',
            showspikes=True,
        ),
        yaxis2=dict(
            visible=False,
            type='linear',
            gridwidth=0,
        ),
        plot_bgcolor=bg_color,
    )

    # layout 업데이트
    fig.update_layout(
        height=1000, width=1500,
        title_text="miny Projects",
        margin=dict(r=40, b=30, l=40),
        font=dict(size=12, color='#252521'),
        paper_bgcolor=bg_color
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='127.0.0.1')