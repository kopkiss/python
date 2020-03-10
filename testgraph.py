import plotly.express as px
df = px.data.iris()
# Use directly Columns as argument. You can use tab completion for this!
fig = px.scatter(df, x=df.sepal_length, y=df.sepal_width, color=df.species, size=df.petal_length)
fig.show()