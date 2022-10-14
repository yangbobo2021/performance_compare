"""
展示对比结果
"""

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import csv

from dash.dependencies import Input
from dash.dependencies import Output
from dash.exceptions import PreventUpdate


RESULT_ANALYSIS_TIME   = 'compare_analysis_time.csv'
RESULT_TASK_TYPE_TIME  = 'compare_task_type_time.csv'
RESULT_TASK_TIME       = 'compare_task_time.csv'
RESULT_UNIT_EVENT_TIME = 'compare_unit_event_time.csv'
RESULT_TASK_UNIT_EVENT_TIME = 'compare_task_unit_event_time.csv'
RESULT_COMMIT_TIME     = 'compare_commit_time.csv'
RESULT_FILE_TIME       = 'compare_file_time.csv'


app = Dash(__name__)

def read_repos(repo_file):
    """
    从CSV读取repo信息
    """
    repos = []
    with open(repo_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        repos = [row for row in reader]

    return repos


analysis_time = read_repos(RESULT_ANALYSIS_TIME)
task_type_time = read_repos(RESULT_TASK_TYPE_TIME)
task_time = read_repos(RESULT_TASK_TIME)
unit_event_time = read_repos(RESULT_UNIT_EVENT_TIME)
task_unit_event_time = read_repos(RESULT_TASK_UNIT_EVENT_TIME)
commit_time = read_repos(RESULT_COMMIT_TIME)
file_time = read_repos(RESULT_FILE_TIME)


# 总分析时间对比
analysis_time_x = 'git_url'
analysis_time_y = 'analysis_time'
analysis_time_y_a = 'analysis_time_a'
analysis_time_y_b = 'analysis_time_b'

# 任务时间对比
task_type_time_choose = list(set([v['git_url'] for v in task_type_time]))
task_type_time_x = 'task_type'
task_type_time_y = 'task_time'
task_type_time_y_a = 'task_type_time_a'
task_type_time_y_b = 'task_type_time_b'

# 任务时间对比
task_time_choose = list(set([v['git_url'] for v in task_type_time]))
task_time_x = 'task'
task_time_y = 'task_time'
task_time_y_a = 'task_time_a'
task_time_y_b = 'task_time_b'

# 分析单元执行时间对比
unit_event_time_choose = list(set([v['git_url'] for v in unit_event_time]))
unit_event_time_x = 'unit_event'
unit_event_time_y = 'unit_event_time'
unit_event_time_y_a = 'unit_event_time_a'
unit_event_time_y_b = 'unit_event_time_b'

task_unit_event_time_choose = list(set([v['git_url'] for v in task_unit_event_time]))
task_unit_event_time_x = 'unit_event'
task_unit_event_time_y = 'unit_event_time'
task_unit_event_time_y_a = 'unit_event_time_a'
task_unit_event_time_y_b = 'unit_event_time_b'

# 提交执行时间对比
commit_time_choose = list(set([v['git_url'] for v in commit_time]))
commit_time_x = 'commit'
commit_time_y = 'commit_time'
commit_time_y_a = 'commit_time_a'
commit_time_y_b = 'commit_time_b'

# 文件执行时间对比
file_time_choose = list(set([v['git_url'] for v in file_time]))
file_time_x = 'file'
file_time_y = 'file_time'
file_time_y_a = 'file_time_a'
file_time_y_b = 'file_time_b'


app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    
    # analysis time
    dcc.Dropdown(
        id="xxx",
        options=[{"value": 'a', "label": 'a'}],
        clearable=False,
        style={"width": "40%"},
        ),
    dcc.Graph(id="analysis_time", figure={}),

    # task time
    html.P("Choose Value:"),
    dcc.Dropdown(
        id="repo",
        options=[{"value": x, "label": x} for x in task_type_time_choose],
        clearable=False,
        style={"width": "40%"},
        ),
    dcc.Graph(id="task_type_time", figure={}),
    dcc.Graph(id="task_time", figure={}),

    dcc.Dropdown(
        id="task_select",
        clearable=False,
        style={"width": "40%"},
        ),
    dcc.Graph(id="task_unit_event_time", figure={}),

    html.P("Choose Task:"),
    dcc.Dropdown(
        id="task",
        options=[{'value':'All', 'label': 'All'}] + [{"value": x, "label": x} for x in list(set([v['unit_event'].split('::')[-1] for v in unit_event_time]))],
        clearable=False,
        style={"width": "40%"},
        ),
    # unit event time
    dcc.Graph(id="unit_event_time", figure={"layout": {
            "height": 700,  # px
        },}),

    # commit time
    dcc.Graph(id="commit_time", figure={"layout": {
            "height": 700,  # px
        },}),

    # file time
    dcc.Graph(id="file_time", figure={"layout": {
            "height": 700,  # px
        },}),
])

@app.callback(
    Output("task_select", "options"),
    Input("repo", "value")
)
def update_options(repo):
    if not repo:
        raise PreventUpdate
    set_value = sorted(list(set([v['task'] for v in task_unit_event_time if v['git_url'] == repo])))
    return [{"value": v, "label": v} for v in set_value]

# task_unit_event
@app.callback(
    Output('task_unit_event_time', 'figure'),
    [
        Input("repo", "value"),
        Input("task_select", "value"),
    ],
)
def generate_task_unit_event_time_chart(repo, task_select):
    if not repo or not task_select:
        raise PreventUpdate

    origin_data = task_unit_event_time
    axis_x = task_unit_event_time_x
    axis_y = task_unit_event_time_y
    axis_y_a = task_unit_event_time_y_a
    axis_y_b = task_unit_event_time_y_b

    data_t = [v for v in origin_data if v['git_url'] == repo and v['task'] == task_select]

    x = [v[axis_x] for v in data_t] if axis_x != '' else [i+1 for i in range(0, len(data_t))]
    x += x

    x_axis = axis_x if axis_x != '' else 'index'

    y = [float(v[axis_y_a]) for v in data_t] + [float(v[axis_y_b]) for v in data_t]
    c = ['a' for i in range(0, len(data_t))] + ['b' for b in range(0, len(data_t))]

    df2 = pd.DataFrame({
        x_axis: x,
        axis_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=axis_y, color='color')
    return fig2


@app.callback(
    Output('analysis_time', 'figure'),
    [
        Input("xxx", "value"),
    ],
    # Output("my_graph", "figure"),
    # [
    #     Input("x_axis", "value"),
    #     Input("y_axis", "value"),
    #     Input("repos", "value"),
    #     Input("types", "value"),
    # ],
)
def generate_analysis_time_chart(xxx):
    x = [v[analysis_time_x] for v in analysis_time] if analysis_time_x != '' else [i+1 for i in range(0, len(analysis_time))]
    x += x

    x_axis = analysis_time_x if analysis_time_x != '' else 'index'

    y = [float(v[analysis_time_y_a]) for v in analysis_time] + [float(v[analysis_time_y_b]) for v in analysis_time]
    c = ['a' for i in range(0, len(analysis_time))] + ['b' for b in range(0, len(analysis_time))]

    df2 = pd.DataFrame({
        x_axis: x,
        analysis_time_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=analysis_time_y, color='color')
    return fig2


@app.callback(
    Output('task_time', 'figure'),
    # Output("my_graph", "figure"),
    [
        Input("repo", "value"),
    ],
)
def generate_task_time_chart(repo):
    if not repo:
        raise PreventUpdate

    origin_data = task_time
    axis_x = task_time_x
    axis_y = task_time_y
    axis_y_a = task_time_y_a
    axis_y_b = task_time_y_b

    data_t = [v for v in origin_data if v['git_url'] == repo]

    x = [v[axis_x] for v in data_t] if axis_x != '' else [i+1 for i in range(0, len(data_t))]
    x += x

    x_axis = axis_x if axis_x != '' else 'index'

    y = [float(v[axis_y_a]) for v in data_t] + [float(v[axis_y_b]) for v in data_t]
    c = ['a' for i in range(0, len(data_t))] + ['b' for b in range(0, len(data_t))]

    df2 = pd.DataFrame({
        x_axis: x,
        axis_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=axis_y, color='color')
    return fig2


@app.callback(
    Output('task_type_time', 'figure'),
    # Output("my_graph", "figure"),
    [
        Input("repo", "value"),
    ],
)
def generate_task_type_time_chart(repo):
    if not repo:
        raise PreventUpdate

    origin_data = task_type_time
    axis_x = task_type_time_x
    axis_y = task_type_time_y
    axis_y_a = task_type_time_y_a
    axis_y_b = task_type_time_y_b

    data_t = [v for v in origin_data if v['git_url'] == repo]

    x = [v[axis_x] for v in data_t] if axis_x != '' else [i+1 for i in range(0, len(data_t))]
    x += x

    x_axis = axis_x if axis_x != '' else 'index'

    y = [float(v[axis_y_a]) for v in data_t] + [float(v[axis_y_b]) for v in data_t]
    c = ['a' for i in range(0, len(data_t))] + ['b' for b in range(0, len(data_t))]

    df2 = pd.DataFrame({
        x_axis: x,
        axis_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=axis_y, color='color')
    return fig2


@app.callback(
    Output('unit_event_time', 'figure'),
    [
        Input("repo", "value"),
        Input("task", "value")
    ],
)
def generate_unit_event_time_chart(repo, task):
    if not repo:
        raise PreventUpdate
    if not task:
        task = 'All'

    origin_data = unit_event_time
    axis_x = unit_event_time_x
    axis_y = unit_event_time_y
    axis_y_a = unit_event_time_y_a
    axis_y_b = unit_event_time_y_b

    data_t = [v for v in origin_data if v['git_url'] == repo and (task=='All' or v['unit_event'].split('::')[-1] == task)]

    x = [v[axis_x] for v in data_t] if axis_x != '' else [i+1 for i in range(0, len(data_t))]
    x += x

    x_axis = axis_x if axis_x != '' else 'index'

    y = [float(v[axis_y_a]) for v in data_t] + [float(v[axis_y_b]) for v in data_t]
    c = ['a' for i in range(0, len(data_t))] + ['b' for b in range(0, len(data_t))]

    df2 = pd.DataFrame({
        x_axis: x,
        axis_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=axis_y, color='color')
    return fig2


@app.callback(
    Output('commit_time', 'figure'),
    [
        Input("repo", "value"),
    ],
)
def generate_commit_time_chart(repo):
    if not repo:
        raise PreventUpdate

    origin_data = commit_time
    axis_x = commit_time_x
    axis_y = commit_time_y
    axis_y_a = commit_time_y_a
    axis_y_b = commit_time_y_b

    data_t = [v for v in origin_data if v['git_url'] == repo]

    x = [v[axis_x] for v in data_t] if axis_x != '' else [i+1 for i in range(0, len(data_t))]
    x += x

    x_axis = axis_x if axis_x != '' else 'index'

    y = [float(v[axis_y_a]) for v in data_t] + [float(v[axis_y_b]) for v in data_t]
    c = ['a' for i in range(0, len(data_t))] + ['b' for b in range(0, len(data_t))]

    df2 = pd.DataFrame({
        x_axis: x,
        axis_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=axis_y, color='color')
    return fig2


@app.callback(
    Output('file_time', 'figure'),
    [
        Input("repo", "value"),
    ],
)
def generate_file_time_chart(repo):
    if not repo:
        raise PreventUpdate

    origin_data = file_time
    axis_x = file_time_x
    axis_y = file_time_y
    axis_y_a = file_time_y_a
    axis_y_b = file_time_y_b

    data_t = [v for v in origin_data if v['git_url'] == repo]

    x = [v[axis_x] for v in data_t] if axis_x != '' else [i+1 for i in range(0, len(data_t))]
    x += x

    x_axis = axis_x if axis_x != '' else 'index'

    y = [float(v[axis_y_a]) for v in data_t] + [float(v[axis_y_b]) for v in data_t]
    c = ['a' for i in range(0, len(data_t))] + ['b' for b in range(0, len(data_t))]

    df2 = pd.DataFrame({
        x_axis: x,
        axis_y: y,
        'color': c,
        #'git': [v['git_url'] for v in data_filter],
    })
    #fig2 = px.scatter(df2, x=x_axis, y=y_axis, color='color', hover_data=['git'])
    fig2 = px.scatter(df2, x=x_axis, y=axis_y, color='color')
    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)