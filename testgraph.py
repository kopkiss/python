import pandas as pd
import chart_studio.plotly as py
import plotly.graph_objs as go

df = pd.read_csv('https://raw.githubusercontent.com/yankev/test/master/life-expectancy-per-GDP-2007.csv')

americas = df[(df.continent=='Americas')]
europe = df[(df.continent=='Europe')]

print(americas)
print('*'*100)
print(europe)
print('*'*100)
print(americas.gdp_percap)
print('*'*100)
print(americas.life_exp)
trace_comp0 = go.Scatter(
    x=americas.gdp_percap,
    y=americas.life_exp,
    mode='markers',
    marker=dict(size=12,
                line=dict(width=1),
                color="navy"
               ),
    name='Americas',
    text=americas.country,
    )

trace_comp1 = go.Scatter(
    x=europe.gdp_percap,
    y=europe.life_exp,
    mode='markers',
    marker=dict(size=12,
                line=dict(width=1),
                color="red"
               ),
    name='Europe',
    text=europe.country,
        )

data_comp = [trace_comp0, trace_comp1]
layout_comp = go.Layout(
    title='Life Expectancy v. Per Capita GDP, 2007',
    hovermode='closest',
    xaxis=dict(
        title='GDP per capita (2000 dollars)',
        ticklen=5,
        zeroline=False,
        gridwidth=2,
    ),
    yaxis=dict(
        title='Life Expectancy (years)',
        ticklen=5,
        gridwidth=2,
    ),
)
fig_comp = go.Figure(data=data_comp, layout=layout_comp)
py.iplot(fig_comp, filename='life-expectancy-per-GDP-2007')