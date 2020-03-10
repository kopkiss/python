from django.shortcuts import render
from django.http import HttpResponse
from .models import Get_db
from .models import Get_db_oracle
import pymysql
import pandas as pd
# from mysql.connector import connection
import cx_Oracle
import importDB.pandasMysql as pm
import numpy as np
import matplotlib as plt

from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px

# Create your views here.

def hello(request):
     return HttpResponse("HELLO")

def homepage(request):
    return render(request, 'index.html')

def showdbsql(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    #################################
    ##### Mysql#######################
    ###############################
    uid = 'root'
    pwd = ''
    host = 'localhost'
    port = 3306
    db = 'sakila.db'
    ##########################################################
    #format--> dialect+driver://username:password@host:port/database
    con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'
    #############################################################
    #print(f'connection string = {con_string}')
    sql_cmd =  """select 
                customer_id,
                first_name,
                last_name
                from customer
                limit 10;
            """

    uid2 = 'root'
    pwd2 = ''
    host2 = 'localhost'
    port2 = 3306
    db2 = 'mydj2'
    con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

    df = pm.execute_query(sql_cmd, con_string)
    print(df)
    pm.save_to_db('importdb_get_db', con_string2, df)
    #############################
    ################################################
    ##############Oracle #######################
    ##############################################

    # sql_cmd =  """SELECT 
    #                 *
    #               FROM CUSTOMER
    #             """

    # uid = 'SYSTEM'
    # pwd = 'Qwer1234!'
    # host = 'localhost'
    # port = 1521
    # db = 'orcl101'
    # con_string = f'oracle://{uid}:{pwd}@{host}:{port}/{db}'

    # df = pm.execute_query(sql_cmd, con_string)
    # print(df)
    ###################################################
    data = Get_db.objects.all()  #ดึงข้อมูลจากตาราง Post มาทั้งหมด
    #data = Meta.objects.all()  #ดึงข้อมูลจากตาราง Post มาทั้งหมด

    return render(request,'showdbsql.html',{'posts':data})

def showdbOracle(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    

    # uid2 = 'root'
    # pwd2 = ''
    # host2 = 'localhost'
    # port2 = 3306
    # db2 = 'mydj1'
    # con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

    # df = pm.execute_query(sql_cmd, con_string)
    # print(df)
    # pm.save_to_db('importdb_get_db', con_string2, df)
    #############################
    ################################################
    ##############Oracle #######################
    ##############################################

    sql_cmd =  """SELECT 
                    *
                  FROM CUSTOMER
                """

    uid = 'SYSTEM'
    pwd = 'Qwer1234!'
    host = 'localhost'
    port = 1521
    db = 'orcl101'
    con_string = f'oracle://{uid}:{pwd}@{host}:{port}/{db}'

    df = pm.execute_query(sql_cmd, con_string)
    print(df)
    ###################################################
    

    uid2 = 'root'
    pwd2 = ''
    host2 = 'localhost'
    port2 = 3306
    db2 = 'mydj2'
    con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

    pm.save_to_db('importdb_get_db_oracle', con_string2, df)

    #################################################################

    data = Get_db_oracle.objects.all()  #ดึงข้อมูลจากตาราง Get_db_oracle มาทั้งหมด
    
    return render(request,'showdbOracle.html',{'posts':data})

# def testGraph(request):
#   print("testGraph")
#   iris = pd.read_csv('iris.csv')
#   fig, ax = plt.subplots() 
#   ax.hist(iris['sepal.length'], color='g', density =1,  bins = 50)  
#   fig.savefig("testpic.pdf", bbox_inches='tight')

#   return render(request,'showdbOracle.html',{'posts':data})

def home(requests):
    def scatter():
        sql_cmd =  """SELECT 
                *
                FROM CUSTOMER
            """
        uid = 'SYSTEM'
        pwd = 'Qwer1234!'
        host = 'localhost'
        port = 1521
        db = 'orcl101'
        con_string = f'oracle://{uid}:{pwd}@{host}:{port}/{db}'
        #df = pd.read_sql(sql, con, params = [2])
        # df = execute_query(sql_cmd, con_string, params= [2])
        df = pm.execute_query(sql_cmd, con_string)    
        
        data = df.values.tolist()
        print(df)
        print('-'*100)
        print(data[1][4])
        x2 = [0, 0]
        x3 = [0,0]

        for i in range(len(df)):
            x2[i] = data[i][4]
            x3[i] = data[i][5]
        print(x2)

        x1 = [1, 2, 3, 4]
        y1 = [30, 35, 25, 45]

        #trace แปลว่า การร่างภาพ
        trace = go.Bar(   
            x = x2,
            y = x3
        )

        


        layout = dict(
            title = 'Simple Graph',
            xaxis = dict(range=[min(x2), max(x2)]),
            yaxis = dict(range=[min(x3), max(x3)])
        )

        fig = go.Figure(data=[trace], layout = layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)

        # ทดลองใช้ plotly express px
        df = px.data.iris()
        # Use directly Columns as argument. You can use tab completion for this!
        fig2 = px.scatter(df, x=df.sepal_length, y=df.sepal_width, color=df.species, size=df.petal_length)
        # haa = fig.show()
        plot_div = plot(fig2, output_type='div', include_plotlyjs=False)
        return plot_div
    
    context={
        'plot1': scatter()
    }


    return render(requests, 'importDB/welcome.html', context)
    


