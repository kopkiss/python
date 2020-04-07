from django.shortcuts import render
from django.http import HttpResponse
from .models import Get_db
from .models import Get_db_oracle
from .models import PRPM_v_grt_pj_team_eis
from .models import PRPM_v_grt_pj_budget_eis
from .models import Prpm_v_grt_project_eis
from .models import PRPM_scopus
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

from sqlalchemy.engine import create_engine
import urllib.parse
import os

from datetime import datetime
import pdb

from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json
from pybliometrics.scopus import ScopusSearch
import requests 


# Create your views here.

def getConstring(check):
    if check == 'sql':
        uid = 'root'
        pwd = ''
        host = 'localhost'
        port = 3306
        db = 'mydj2'
        con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'
    elif check == 'oracle':
        DIALECT = 'oracle'
        SQL_DRIVER = 'cx_oracle'
        USERNAME = 'pnantipat' #enter your username
        PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
        HOST = 'delita.psu.ac.th' #enter the oracle db host url
        PORT = 1521 # enter the oracle port number
        SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
        con_string = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

    return con_string

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

    os.environ["NLS_LANG"] = ".UTF8" 
    data = PRPM_v_grt_pj_budget_eis.objects.all()[:50]  #ดึงข้อมูลจากตาราง Get_db_oracle มาทั้งหมด

    return render(request,'showdbOracle.html',{'posts': data})

def home(requests):
    def graph1():
        sql_cmd =  """  SELECT * FROM querygraph1 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR))  """
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)   
        
        # data = df.values.tolist()
        # print(df.budget_year,'', df.budget)
      
        # x = df.budget_year.astype(int)
        # y = df.budget.astype(int)

        fig = px.bar( df,
            x = 'budget_year',
            y = 'budget',  labels = {'x':'aasd'}
        )
        fig.update_layout(title_text='งบประมาณวิจัยต่อปี')
        # fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True)


        # layout = dict(
        #     title = 'Simple Graph',
        #     xaxis = dict(range=[min(x), max(x)]),
        #     yaxis = dict(range=[min(y), max(y)])
        # )

        # trace.show() #test graph
        # fig = go.Figure(data=[trace], layout = layout)
        # fig = go.Figure(data=[trace])
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        # # ทดลองใช้ plotly express px
        # df = px.data.iris()
        # # Use directly Columns as argument. You can use tab completion for this!
        # fig2 = px.scatter(df, x=df.sepal_length, y=df.sepal_width, color=df.species, size=df.petal_length)
        # # haa = fig.show()
        # plot_div = plot(fig2, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph2():
        sql_cmd =  """SELECT * FROM querygraph2 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR)) """
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 

        fig = px.bar(df, x="camp_owner", y="budget", color="camp_owner",
            animation_frame="budget_year", animation_group="faculty_owner")

        fig.update_layout(
            
            width=900, height=450)



        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph3():
        sql_cmd =  """SELECT * FROM querygraph3 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 

        fig = px.line(df, x="budget_year", y="budget", color="camp_owner",
        line_shape="spline", render_mode="svg",  template='plotly_dark' )

        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph4():
        sql_cmd =  """SELECT * FROM querygraph4 
                        where year BETWEEN YEAR(NOW())-10 AND YEAR(NOW())-1
                 """
                #  where year BETWEEN YEAR(NOW())-10 AND YEAR(NOW())
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        # pdb.set_trace()
        fig = px.bar(df, x="year", y="n", color="time",  barmode="group" , template='presentation', text='n')

        fig.update_layout(
            title={   #กำหนดให้ title อยู่ตรงกลาง
                'text': "งานวิจัยที่เสร็จทัน และไม่ทันเวลาที่กำหนด",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
            ,width=900, height=450,  #ความกว้างความสูง ของกราฟในหน้าต่าง 
            xaxis_title="ปี ค.ศ",
            yaxis_title="จำนวน"
            ,margin=dict(l=100, r=100, t=100, b=100)  # กำหนด left right top bottom ของกราฟในหน้าต่าง 
            ,paper_bgcolor="LightSteelBlue" # กำหนด สี BG 
            # font=dict(
            #     family="Courier New, monospace",
            #     size=18,
            #     color="#7f7f7f"
            )
        fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10)    #เพิ่มเส้นขีดสีแดง ตามแกน x 
        fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10, col=1) #เพิ่มเส้นขีดสีแดง ตามแกน y
        # fig.update_yaxes(automargin=True)    

        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph5():
        sql_cmd =  """SELECT camp_owner, sum(budget) as budget
                    FROM querygraph2
                    where budget_year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1
                    group by 1"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        # print(df)
        fig = px.pie(df, values='budget', names='camp_owner')
        fig.update_traces(textposition='inside', textfont_size=14)
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        fig.update_layout( width=900, height=450)
        fig.update_layout(title="budget ในปี 2562" )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph6():
        sql_cmd =  """select year, n_of_publish  as number_of_publication
                    from importdb_prpm_scopus
                    where year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        # print(df)
        fig = px.line(df, x="year", y="number_of_publication",
        line_shape="spline", render_mode="svg",  template='plotly_dark' )
        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def counts():
        
        sql_cmd =  """SELECT COUNT(*) as c
                    FROM importdb_prpm_v_grt_pj_team_eis;
                    """

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        print(df)
        print(df.iloc[0])

        return df.iloc[0]
    
    def budget_per_year():
        
        sql_cmd =  """SELECT FUND_BUDGET_YEAR as budget_year, sum(SUM_BUDGET_PLAN) as sum
                    FROM importdb_prpm_v_grt_project_eis
                    WHERE FUND_BUDGET_YEAR = YEAR(date_add(NOW(), INTERVAL 543 YEAR)) 
                    group by 1"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        print(df)
        return df.iloc[0]
    

    def getScopus():
        
        sql_cmd =  """select year, n_of_publish from importdb_prpm_scopus where year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        print(df.n_of_publish)    
        return df.iloc[0]

    context={
        'plot1': graph1(),
        'plot2': graph2(),
        'plot3': graph3(),
        'plot4': graph4(),
        'plot5': graph5(),
        'plot6': graph6(),
        'counts': counts(),
        'budget_per_year': budget_per_year(),
        'scopus' : getScopus(),
    }
    
    return render(requests, 'welcome.html', context)
    
def rodReport(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    
    data = PRPM_v_grt_pj_team_eis.objects.all()  #ดึงข้อมูลจากตาราง  มาทั้งหมด
    return render(request,'rodreport.html',{'posts':data})


def prpmdump(request):
    return render(request,'prpmdump.html')

def dump(request):
    print('dumping')
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    checkpoint = True
    # now = datetime.now()
    # timestamp = datetime.timestamp(now)


    if request.POST['row']=='Dump1':  #project
        try:
            sql_cmd =  """select * from research60.v_grt_project_eis 
                        WHERE psu_project_id not in ('X541090' ,'X541067','X551445')
                    """
            DIALECT = 'oracle'
            SQL_DRIVER = 'cx_oracle'
            USERNAME = 'pnantipat' #enter your username
            PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
            HOST = 'delita.psu.ac.th' #enter the oracle db host url
            PORT = 1521 # enter the oracle port number
            SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
            ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

            engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" )
            df = pd.read_sql_query(sql_cmd, engine)
            # df = pm.execute_query(sql_cmd, con_string)
            # print(df)

            ###################################################
            # save path
            uid = 'root'
            pwd = ''
            host = 'localhost'
            port = 3306
            db = 'mydj2'
            con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'

            pm.save_to_db('importdb_prpm_v_grt_project_eis', con_string, df)
            # now = datetime.now()
            # timestamp = datetime.timestamp(now)

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Dump2': #team
        try:
            sql_cmd =  """select * 
                        from (
                                select * from research60.v_grt_pj_team_eis
                                where CO_ID not in (select CO_ID from research60.v_grt_pj_team_eis
                                        where CO_ID not in
                                            (
                                                select MAX(CO_ID) AS maxRecordID
                                                from research60.v_grt_pj_team_eis
                                                group by user_id_card
                                            )) and user_active = 1
                                order by co_id
                        )
                        """
            DIALECT = 'oracle'
            SQL_DRIVER = 'cx_oracle'
            USERNAME = 'pnantipat' #enter your username
            PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
            HOST = 'delita.psu.ac.th' #enter the oracle db host url
            PORT = 1521 # enter the oracle port number
            SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
            ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

            engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" )
            df = pd.read_sql_query(sql_cmd, engine)
            # df = pm.execute_query(sql_cmd, con_string)
            print(df)

            ###################################################
            # save path
            uid2 = 'root'
            pwd2 = ''
            host2 = 'localhost'
            port2 = 3306
            db2 = 'mydj2'
            con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

            pm.save_to_db('importdb_prpm_v_grt_pj_team_eis', con_string2, df)
            # now = datetime.now()
            # timestamp = datetime.timestamp(now)

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Dump3':   #budget
        try:
            sql_cmd =  """SELECT 
                        *
                    FROM research60.v_grt_pj_budget_eis
                    """
            DIALECT = 'oracle'
            SQL_DRIVER = 'cx_oracle'
            USERNAME = 'pnantipat' #enter your username
            PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
            HOST = 'delita.psu.ac.th' #enter the oracle db host url
            PORT = 1521 # enter the oracle port number
            SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
            ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

            engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" )
            df = pd.read_sql_query(sql_cmd, engine)
            # df = pm.execute_query(sql_cmd, con_string)
            print(df)

            ###################################################
            # save path
            uid2 = 'root'
            pwd2 = ''
            host2 = 'localhost'
            port2 = 3306
            db2 = 'mydj2'
            con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

            pm.save_to_db('importdb_prpm_v_grt_pj_budget_eis', con_string2, df)
            # now = datetime.now()
            # timestamp = datetime.timestamp(now)

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Dump4':   #budget
        try:
            sql_cmd =  """SELECT 
                        *
                    FROM RESEARCH60.R_FUND_TYPE
                    """

            con_string = getConstring('oracle')
            engine = create_engine(con_string, encoding="latin1" )
            df = pd.read_sql_query(sql_cmd, engine)
            # df = pm.execute_query(sql_cmd, con_string)
            print(df)

            ###################################################
            # save path
            con_string2 = getConstring('sql')
            pm.save_to_db('importdb_prpm_r_fund_type', con_string2, df)
            # now = datetime.now()
            # timestamp = datetime.timestamp(now)

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)


    if checkpoint:
        result = 'Dumped'
    else:
        result = 'Cant Dump'
    
    context={
        'result': result,
        # 'time':datetime.fromtimestamp(timestamp)
    }
    return render(request,'prpmdump.html',context)

def dQueryReports(request):
    return render(request,'dQueryReports.html')

def dQuery(request):
    print('dQuery')
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    checkpoint = True
    whichrows = ''
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    scopus = ""

    if request.POST['row']=='Query1':  #project
        try:
            # sql_cmd =  """select 
            #                 budget_year , 
            #                 sum(budget_amount) as budget 
            #             from importdb_prpm_v_grt_pj_budget_eis 
            #             group by budget_year
            #             having budget_year is not null and budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))
            #             order by 1
            # """

            sql_cmd =  """select  FUND_BUDGET_YEAR as budget_year , 
                                    sum(sum_budget_plan) as budget 
                            from importdb_prpm_v_grt_project_eis
                            group by FUND_BUDGET_YEAR
                            having FUND_BUDGET_YEAR is not null and budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                            order by 1
             """

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string) 

            # print(df)

            ###################################################
            # save path

            pm.save_to_db('querygraph1', con_string, df)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            whichrows = 'row1'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query2': #team
        try:
            # sql_cmd =  """SELECT 
            #                 A.camp_owner,
            #                 A.faculty_owner,
            #                 B.budget_year,
            #                 sum(B.budget_amount) as budget
            #             FROM importdb_prpm_v_grt_project_eis as A
            #             JOIN importdb_prpm_v_grt_pj_budget_eis as B on A.psu_project_id = B.psu_project_id
            #             where budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))
            #             and		 A.camp_owner is not null and 
            #                 A.faculty_owner is not null
            #             GROUP BY 1, 2, 3
            # """

            sql_cmd =  """SELECT 
                                A.camp_owner,
                                A.faculty_owner,
                                A.FUND_BUDGET_YEAR as budget_year,
                                sum(A.SUM_BUDGET_PLAN) as budget
                        FROM importdb_prpm_v_grt_project_eis as A
                        where FUND_BUDGET_YEAR BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                        and		 A.camp_owner is not null and 
                        A.faculty_owner is not null
                        GROUP BY 1, 2, 3
            """

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string) 
            # df = pm.execute_query(sql_cmd, con_string)
            print(df)

            ###################################################
            # save path
            pm.save_to_db('querygraph2', con_string, df)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            whichrows = 'row2'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query3':   #budget
        try:
            sql_cmd =  """SELECT 
                            A.camp_owner,
                            B.budget_year,
                            sum(B.budget_amount) as budget
                        FROM importdb_prpm_v_grt_project_eis as A
                        JOIN importdb_prpm_v_grt_pj_budget_eis as B on A.psu_project_id = B.psu_project_id
                        where budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR)) and camp_owner IS NOT null
                        GROUP BY 1, 2
            """
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            print(df)

            ###################################################
            # save path
            pm.save_to_db('querygraph3', con_string, df)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            whichrows = 'row3'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
        
    elif request.POST['row']=='Query4':   #budget
        try:
            #เสร็จก่อน
            sql_cmd1 =  """SELECT 
                            year(PROJECT_END_DATE) as year,
                            count(year(PROJECT_END_DATE)) as n
                        FROM `importdb_prpm_v_grt_project_eis` 
                        WHERE PROJECT_FINISH_DATE <= PROJECT_END_DATE and PROJECT_FINISH_DATE is not null
                        group by 1 
                        order by 1
            """
            #เสร็จไม่ทัน
            sql_cmd2 =  """SELECT 
                            year(PROJECT_END_DATE) as year,
                            count(year(PROJECT_END_DATE)) as n
                        FROM `importdb_prpm_v_grt_project_eis` 
                        WHERE PROJECT_FINISH_DATE > PROJECT_END_DATE  and PROJECT_FINISH_DATE is not null
                        group by 1 
                        order by 1
            """
            con_string = getConstring('sql')
            df1 = pm.execute_query(sql_cmd1, con_string)
            df1['time'] = 'onTime'
            df2 = pm.execute_query(sql_cmd2, con_string)
            df2['time'] = 'late'
            df = df1.append(df2, ignore_index=True)
            df = df.sort_values(by='year', ignore_index = True)
            # df1['late'] = df2['late']
            # df = pd.merge(df2,df1, left_on = 'year', right_on ="year", how = 'left')
            # print(df1)
            ###################################################
            # save path
            pm.save_to_db('querygraph4', con_string, df)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            whichrows = 'row4'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query5':   
        # api-endpoint 
        URL = "https://api.elsevier.com/content/search/scopus"

        # params given here 
        con_file = open("importDB\config.json")
        config = json.load(con_file)
        con_file.close()

        now = datetime.now()
        year = now.year
       
        apiKey = config['apikey']
        query = f"AF-ID(60006314) and PUBYEAR IS {year}"

        try:
            # defining a params dict for the parameters to be sent to the API 
            PARAMS = {'query':query,'apiKey':apiKey}  

            # sending get request and saving the response as response object 
            r = requests.get(url = URL, params = PARAMS) 
            
            print ("Saving")

            # extracting data in json format 
            data = r.json() 
            print("total:",data['search-results']['opensearch:totalResults'])
            scopus = data['search-results']['opensearch:totalResults']

            obj, created = PRPM_scopus.objects.get_or_create(year = year+543, defaults ={ 'n_of_publish': scopus})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า n_of_publish = scopus
                obj.n_of_publish =  scopus
                obj.save()
            now = datetime.now()
            timestamp = datetime.timestamp(now)

            print ("Saved")

        except Exception as e:
            scopus = "error"

        checkpoint = "actionScopus"
        whichrows = 'row5'

    if checkpoint is True:
        result = 'Dumped'
    elif checkpoint == 'actionScopus':
        result = ""+scopus
    else:
        result = 'Cant Dump'
    
    context={
        'result': result,
        'time':datetime.fromtimestamp(timestamp),
        'whichrow' : whichrows
    }
    return render(request,'dQueryReports.html',context)
