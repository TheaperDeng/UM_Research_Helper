# coding: utf-8
# author: Junwei Deng
# institute: UMSI
# SI507 Final Project

import plotly.graph_objects as go
import plotly.express as px

def school_distribution_plot(data):
    labels = []
    values = []
    for i in range(len(data)):
        labels.append(data[i][0])
        values.append(data[i][1])
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title="The distribution of the faculties' affiliation")
    fig.show()

def keyword_plot(data):
    # fig = px.scatter(gapminder, x="gdpPercap", y="lifeExp", text="country", log_x=True, size_max=60)
    # fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    fig = px.scatter(x=data[0], y=data[1], text = data[2], log_x=True, log_y = True)
    fig.update_traces(textposition='top center')
    fig.update_layout(title="The keyword of the faculties' description", xaxis_title="Count of faculties who mentions this keyword",
    yaxis_title="Count of this keyword in all faculties' description",)
    fig.show()

def keyword_search_plot(data, keyword):
    labels = []
    value = []
    for i in range(len(data[0][1])):
        value.append([])
    for datum in data:
        labels.append(datum[0])
        for i in range(len(datum[1])):
            value[i].append(datum[1][i])
    data_plot = []
    for i in range(len(keyword)):
        data_plot.append(go.Bar(name = keyword[i], x = labels, y = value[i]))
    fig = go.Figure(data_plot)
    # # Change the bar mode
    fig.update_layout(barmode='group')
    fig.update_layout(title="The faculty match your keyword", xaxis_title="Faculty name",
    yaxis_title="Frequency of mentioning you keyword",)
    fig.show()

def course_recommendation_plot(data, faculty_name):
    course_cat = []
    course_title = []
    course_desc = []
    course_page = []
    course_keyword = []
    course_credit = []
    course_pre = []
    for course in data:
        course_cat.append(course[0])
        course_credit.append(course[1]["credit"])
        course_title.append(course[1]["title"])
        course_desc.append(course[1]["desc"])
        course_page.append(course[1]["page"])
        course_keyword.append(str(sorted(course[1]["keyword"].items(), key = lambda x:(-int(x[1])))))
        course_pre.append(course[1]["pre-request course"])
    fig = go.Figure(data=[go.Table(header=dict(values=['Course Number', 'Course title', 'Course Credit', 'Match Key word']),
                    cells=dict(values=[course_cat, course_title, course_credit, course_keyword]))
                        ])
    fig.update_layout(title=("The Course you may want to take to work with " + faculty_name))
    fig.show()