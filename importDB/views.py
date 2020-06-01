from django.shortcuts import render    # หมายถึง เป็นการเรียกจาก Template ที่เราสร้างไว้
from django.http import HttpResponse   # หมายถึง เป็นการ วาด HTML เอง
import pandas as pd
import numpy as np
import os
from datetime import datetime
import time
import json
import requests
from pprint import pprint
# เกี่ยวกับฐานข้อมูล
from .models import Get_db       
from .models import Get_db_oracle
from .models import PRPM_v_grt_pj_team_eis  # " . " หมายถึง subfolder ต่อมาจาก root dir
from .models import PRPM_v_grt_pj_budget_eis
from .models import Prpm_v_grt_project_eis
from .models import PRPM_ranking
from .models import PRPM_ranking_cited_isi
import pymysql
import cx_Oracle
from sqlalchemy.engine import create_engine
import importDB.pandasMysql as pm
import urllib.parse
# เกี่ยวกับกราฟ
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# เกี่ยวกับ scopus isi tci
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# เกี่ยวกับการ login
from django.contrib.auth.decorators import login_required

# Create your views here.

def getConstring(check):  # สร้างไว้เพื่อ เลือกที่จะ get database ด้วย mysql หรือ oracle
    
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
    
    pm.save_to_db('importDB/importdb_get_db', con_string2, df)
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
    data = PRPM_v_grt_pj_budget_eis.objects.all()[:50]  #ดึงข้อมูลจากตาราง Get_db_oracle index 0 - 49

    return render(request,'importDB/showdbOracle.html',{'posts': data})

def home(requests):  # หน้า homepage หน้าแรก

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def get_head_page(): # get จำนวนของนักวิจัย 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)


    def graph7():
        df = pd.read_csv("""mydj1/static/csv/Filled_area_chart.csv""")

        df1 = df[["year","Goverment"]]
        df2 = df[["year","Revenue"]]
        df3 = df[["year","Campus"]]
        df4 = df[["year","Department"]]
        df5 = df[["year","National"]]
        df6 = df[["year","International"]]
        df7 = df[["year","Matching_fund"]]

        fig = go.Figure()

        # 0
        fig.add_trace(go.Scatter(
            x=df1["year"], y=df1["Goverment"],
            fill='tozeroy',
            mode='lines',
            line_color='#0066FF',
            line=dict(width=0.8),
            name="เงินงบประมาณแผ่นดิน"
            ))
        # 1
        fig.add_trace(go.Scatter(
            x=df2["year"], 
            y=df2["Revenue"],
            fill='tozeroy', # fill area between trace0 and trace1
            mode='lines',
            line_color='#1976D2 ' ,
            line=dict(width=0.8),
            name="เงินรายได้มหาวิทยาลัย"
            ))
        # 2
        fig.add_trace(go.Scatter(
            x=df3["year"], y=df3["Campus"],
            fill='tozeroy',
            mode='lines',
            line_color='#4FC3F7  ',
            line=dict(width=0.8),
            name="เงินรายได้วิทยาเขต"
            ))
        # 3
        fig.add_trace(go.Scatter(
            x=df4["year"], 
            y=df4["Department"],
            fill='tozeroy', # fill area between trace0 and trace1
            mode='lines',
            line_color='#03A9F4', 
            line=dict(width=0.8),
            name="เงินรายได้คณะ/หน่วยงาน"
        ))
        # 4
        fig.add_trace(go.Scatter(
            x=df5["year"], 
            y=df5["National"],
            fill='tozeroy',
            mode='lines',
            line_color='#5DADE2   ',
            line=dict(width=0.8),
            name="เงินทุนภายนอก(ในประเทศ)"
            ))
        # 5
        fig.add_trace(go.Scatter(
            x=df6["year"], 
            y=df6["International"],
            fill='tozeroy', # fill area between trace0 and trace1
            mode='lines', line_color='#2196F3 ' ,
            line=dict(width=0.8),
            name="เงินทุนภายนอก (ต่างประเทศ)"
        ))
        # 6
        fig.add_trace(go.Scatter(
            x=df7["year"], y=df7["Matching_fund"],
            fill='tozeroy',
            mode='lines',
            line_color='#80DEEA ',
            line=dict(width=0.8),
            name="เงินทุนร่วม"
            ))

        fig.update_layout(
            xaxis_title="<b>ปี พ.ศ.</b>",
            yaxis_title="<b>จำนวนเงิน (บาท)</b>",
            # font=dict(
            #     size=16,
            # )
        )
        fig.update_layout(  # ปรับความสูง ของกราฟให้เต็ม ถ้าใช้ graph object
            margin=dict(t=50),
        )
    
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)

        return  plot_div

    def graph8(filter_year):  # แสดงกราฟโดนัด ของจำนวน เงินทั้ง 7 หัวข้อ
        sql_cmd =  """select * from revenues where year = """+str(filter_year)
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        df = df[["Goverment","Revenue","Campus","Department","National","International","Matching_fund"]]
        
        newdf = pd.DataFrame({'BUDGET_TYPE' : ["เงินงบประมาณแผ่นดิน","เงินรายได้มหาวิทยาลัย","เงินรายได้วิทยาเขต"
                                                ,"เงินรายได้คณะ/หน่วยงาน","เงินทุนภายนอก(ในประเทศ)","เงินทุนภายนอก (ต่างประเทศ)","เงินทุนร่วม"]})
        df = df.T # ทรานโพส เพื่อให้ plot เป็นกราฟได้สะดวก
        print("*df***")
        print(df)
        newdf["budget"] = 0.0  # สร้าง column ใหม่
        for n in range(0,7):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = df[0][n] 

        df = newdf.copy()   # copy เพื่อ ใช้ในการรวมจำนวนเงินทั้งหมด แสดงในกราฟ ตรงกลางของ donut

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' ,color_discrete_sequence=px.colors.sequential.haline, hole=0.5 ,)
        fig.update_traces(textposition='inside', textfont_size=14)
        fig.update_traces(hoverinfo="label+percent+name",
                  marker=dict(line=dict(color='#000000', width=2)))

        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        # fig.update_layout( width=1000, height=485)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))
        fig.update_layout( annotations=[dict(text="<b>{:,.2f}</b>".format(df.budget.sum()), x=0.50, y=0.5,  font_color = "black", showarrow=False)]) ##font_size=20,
        # fig.update_layout(
        #     title="""<b>รายได้งานวิจัย ปี"""+str(filter_year)+""" แยกตามแหล่งทุน</b>""",
        # )
        fig.update_traces(hovertemplate='GDP: %{name} <br>Life Expectany: %{value}') 
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)

        return plot_div

    def graph3():

        df = pd.read_csv("""mydj1/static/csv/query_graph3.csv""")

        # df.to_csv ("""mydj1/static/csv/query_graph3.csv""", index = False, header=True)

        fig = px.line(df, x="budget_year", y="budget", color="camp_owner",
        line_shape="spline", render_mode="svg",  )
        fig.update_layout(
            xaxis_title="<b>ปี พ.ศ.</b>",
            yaxis_title="<b>จำนวนเงิน (บาท)</b>",
            # font=dict(
            #     size=16,
            # )
        )
        # fig.update_traces(mode="markers+lines", hovertemplate=None)
        # fig.update_layout(hovermode="x")
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph5():
        sql_cmd =  """SELECT camp_owner, sum(budget) as budget
                    FROM querygraph2
                    where budget_year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                    group by 1"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 

        # df = pd.read_csv("""mydj1/static/csv/querygraph2.csv""")
        
        fig = px.pie(df, values='budget', names='camp_owner')
        fig.update_traces(textposition='inside', textfont_size=14)
        # fig.update_layout( width=900, height=450)
        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        # fig.update_layout( width=1000, height=485)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))

        fig.update_traces(hoverinfo="label+percent+name",
                  marker=dict(line=dict(color='#000000', width=2)))
        
        # fig.update_layout( height=400, width=520,)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph1():
        df = pd.read_csv("""mydj1/static/csv/query_graph1.csv""")

        fig = make_subplots(rows=1, cols=2,
                            column_widths=[1, 0.5],
                            specs=[[{"type": "bar"},{"type": "table"}]]
                            )

        fig.add_trace(
                        px.bar( df,
                            x = 'budget_year',
                            y = 'budget', 
                       ).data[0],
                       row=1,col=1
        )
              
    

        df['budget'] = df['budget'].apply(moneyformat) #เปลี่ยน format ของ budget เป็นรูปเเบบของเงิน

        fig.add_trace(
                        go.Table( 
                            columnwidth = [140,400],
                            header=dict(values=["<b>Year</b>","<b>Budget<b>"],
                                        fill = dict(color='#C2D4FF'),
                                        align = ['center'] * 10),
                            cells=dict(values=[df.budget_year, df.budget],
                                    fill = dict(color='#F5F8FF'),
                                    align = ['center','right'] * 5)
                                    )
                            , row=1, col=2)

        fig.update_layout(
                        
                        # height=500, width=800,
                        xaxis_title="<b>ปี พ.ศ</b>",
                        yaxis_title="<b>จำนวนเงิน (บาท)</b>")

        fig.update_layout(  # ปรับความสูง ของกราฟให้เต็ม ถ้าใช้ graph object
            margin=dict(t=50),
        )
        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph2():
        # sql_cmd =  """SELECT * FROM querygraph2 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR)) """
        # con_string = getConstring('sql')
        # df = pm.execute_query(sql_cmd, con_string) 
        df = pd.read_csv("""mydj1/static/csv/query_graph2.csv""")

        fig = px.bar(df, x="camp_owner", y="budget", color="camp_owner",
            animation_frame="budget_year", animation_group="faculty_owner")

        fig.update_layout(
            
            width=900, height=450)



        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph4():

        df = pd.read_csv("""mydj1/static/csv/query_graph4.csv""")

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

    def graph6():
        sql_cmd =  """select year, n_of_publish  as number_of_publication
                    from importdb_prpm_scopus
                    where year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        
        fig = px.line(df, x="year", y="number_of_publication",
        line_shape="spline", render_mode="svg",  template='plotly_dark' )
        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################
        
        'plot1' : graph1(),
        'plot3': graph3(),
        # 'plot4': graph4(),
        'plot5': graph5(),
        # 'plot6': graph6(),
        'plot7': graph7(),
        'plot8': graph8(datetime.now().year+543),

    }
    
    return render(requests, 'importDB/welcome.html', context)
    
def rodReport(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    
    data = PRPM_v_grt_pj_team_eis.objects.all()  #ดึงข้อมูลจากตาราง  มาทั้งหมด
    return render(request,'importDB/rodreport.html',{'posts':data})

def prpmdump(request):
    return render(request,'importDB/prpmdump.html')

def dump(request):  # ดึงข้อมูล เข้าสู่ ฐาน Mysql
    print('dumping')
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    checkpoint = True

    dt = datetime.now()
    timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

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
            

            ###################################################
            # save path
            uid = 'root'
            pwd = ''
            host = 'localhost'
            port = 3306
            db = 'mydj2'
            con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'

            pm.save_to_db('importdb_prpm_v_grt_project_eis', con_string, df)
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

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
            

            ###################################################
            # save path
            uid2 = 'root'
            pwd2 = ''
            host2 = 'localhost'
            port2 = 3306
            db2 = 'mydj2'
            con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

            pm.save_to_db('importdb_prpm_v_grt_pj_team_eis', con_string2, df)
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

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
            

            ###################################################
            # save path
            uid2 = 'root'
            pwd2 = ''
            host2 = 'localhost'
            port2 = 3306
            db2 = 'mydj2'
            con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

            pm.save_to_db('importdb_prpm_v_grt_pj_budget_eis', con_string2, df)
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

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
            

            ###################################################
            # save path
            con_string2 = getConstring('sql')
            pm.save_to_db('importdb_prpm_r_fund_type', con_string2, df)

            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)


    if checkpoint:
        result = 'Dumped'
    else:
        result = 'Cant Dump'
    
    context={
        'result': result,
        'time':datetime.fromtimestamp(timestamp)
    }
    return render(request,'importDB/prpmdump.html',context)

# @login_required
def dQueryReports(request):
    return render(request,'importDB/dQueryReports.html')

# @login_required
def dQuery(request): # Query ฐานข้อมูล Mysql (เป็น .csv) เพื่อสร้างเป็น กราฟ หรือ แสดงข้อมูล บน tamplate
    print('dQuery')
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    checkpoint = True
    whichrows = ''
    ranking = ""

    dt = datetime.now()
    timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

    def cited_isi():
        path = """importDB"""
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
        WebDriverWait(driver, 10)
        
        # try: 
        # get datafreame by web scraping
        driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

        btn1 =driver.find_element_by_id('value(input1)')
        btn1.clear()
        btn1.send_keys("Prince Of Songkla University")
        driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
        driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
        driver.find_element_by_xpath("//span[@class='select2-results']").click() 
        driver.find_element_by_xpath("//span[@class='searchButton']").click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
        driver.find_element_by_class_name('summary_CitLink').click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
        driver.find_element_by_xpath("//a[@class='snowplow-citation-report']").click() 
        element = wait.until(EC.element_to_be_clickable((By.NAME, 'cr_timespan_submission')))  # hold by name

        # หาค่า citation ของปีปัจจุบันd
        cited1 = driver.find_element_by_id("CR_HEADER_4" ).text
        cited2 = driver.find_element_by_id("CR_HEADER_3" ).text
        h_index = driver.find_element_by_id("H_INDEX" ).text
        print(cited1)
        print(cited2)
        # หาค่า h_index ของปีปัจจุบัน

        print(h_index)
        
        cited1 =  cited1.replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
        cited2 =  cited2.replace(",","")

        
        # ใส่ ตัวเลขที่ได้ ลง dataframe
        df1=pd.DataFrame({'year':datetime.now().year+543 , 'cited':cited1}, index=[0])
        df2=pd.DataFrame({'year':datetime.now().year+543-1 , 'cited':cited2}, index=[1])
        df_records = pd.concat([df1,df2],axis = 0) # ต่อ dataframe
        df_records['cited'] = df_records['cited'].astype('int') # เปลี่ยนตัวเลขเป็น int    

        

        return df_records, h_index

        # except Exception as e:
        #     print("Error")
        #     print(e)
        #     return None, None

        # finally:
        #     driver.quit()

    def isi():
        path = """importDB"""
        # print(path+'/chromedriver.exe')
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
        # os.chdir(path)  # setpath
        WebDriverWait(driver, 10)
        try:
            # กำหนด URL ของ ISI
            driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))

            btn1 =driver.find_element_by_id('value(input1)')  # เลือกกล่อง input
            btn1.clear() # ลบ ค่าที่อยู่ในกล่องเดิม ที่อาจจะมีอยู่
            btn1.send_keys("Prince Of Songkla University")   # ใส่ค่าเพื่อค้นหาข้อมูล
            driver.find_element_by_xpath("//span[@id='select2-select1-container']").click() # กดปุ่ม
            driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")
            driver.find_element_by_xpath("//span[@class='select2-results']").click()
            driver.find_element_by_xpath("//span[@class='searchButton']").click()

            # กดปุ่ม Analyze Results
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))
            # driver.find_element_by_class_name('summary_CitLink').click()
            # WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
            driver.find_element_by_class_name('summary_CitLink').click()
   
            # กดปุ่ม Publication Years
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
            driver.find_element_by_xpath('//*[contains(text(),"Publication Years")]').click()  # กดจากการค้าหา  ด้วย text
       
            # ดึงข้อมูล ในปีปัจุบัน ใส่ใน row1 และ ปัจุบัน -1 ใส่ใน row2
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
            row1 = driver.find_element_by_class_name("RA-NEWRAresultsEvenRow" ).text.split(' ')[:2]
            WebDriverWait(driver, 15)  
            row2 = driver.find_element_by_class_name("RA-NEWRAresultsOddRow" ).text.split(' ') [:2]

            for i in range(len(row2)):
                row2[i] =  row2[i].replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
                row1[i] =  row1[i].replace(",","")
            
            # ใส่ ตัวเลขที่ได้ ลง dataframe
            df1=pd.DataFrame({'year':row1[0] , 'record_count':row1[1]}, index=[0])
            df2=pd.DataFrame({'year':row2[0] , 'record_count':row2[1]}, index=[1])
            df_records = pd.concat([df1,df2],axis = 0) # ต่อ dataframe
            df_records['record_count'] = df_records['record_count'].astype('int') # เปลี่ยนตัวเลขเป็น int

            return df_records

        except Exception as e:
            print(e)
            return None

        finally:
            driver.quit()          

    def sco(year):
        
        URL = "https://api.elsevier.com/content/search/scopus"

        # params given here 
        con_file = open("importDB\config.json")
        config = json.load(con_file)
        con_file.close()
        year2 = year-1
        apiKey = config['apikey']
        
        try:
            query = f"(AF-ID(60006314) or AF-ID(60025527)) and PUBYEAR IS {year}"
            # defining a params dict for the parameters to be sent to the API 
            PARAMS = {'query':query,'apiKey':apiKey}  

            # sending get request and saving the response as response object 
            r = requests.get(url = URL, params = PARAMS) 

            # extracting data in json format 
            data1= r.json() 

            query = f"(AF-ID(60006314) or AF-ID(60025527)) and PUBYEAR IS {year2}"
                
            # defining a params dict for the parameters to be sent to the API 
            PARAMS = {'query':query,'apiKey':apiKey}  

            # sending get request and saving the response as response object 
            r = requests.get(url = URL, params = PARAMS) 

            # extracting data in json format 
            data2 = r.json() 
            # convert the datas to dataframe
            df1=pd.DataFrame({'year':year, 'record_count':data1['search-results']['opensearch:totalResults']}, index=[0])
            df2=pd.DataFrame({'year':year2 , 'record_count':data2['search-results']['opensearch:totalResults']}, index=[1])
            df_records = pd.concat([df1,df2],axis = 0)
            df_records['record_count']= df_records['record_count'].astype('int')

            return df_records

        except Exception as e:
            print(e)
            return None

    def get_df_by_rows(rows):
        categories = list()
        i = 0
        for row in rows:
            j = 0
            for j, c in enumerate(row.text):
                if c.isdigit():
                    break
            categories.append(tuple((row.text[0:j-1],row.text[j:])))

        for index, item in enumerate(categories):
            itemlist = list(item)
            itemlist[1] = itemlist[1].split(" ",1)[0].replace(",","")
            item = tuple(itemlist)
            categories[index] = item

        return(categories)    

    def chrome_driver_get_research_areas_ISI():
        
        try: 
            # get datafreame by web scraping
            driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

            btn1 =driver.find_element_by_id('value(input1)')
            btn1.clear()
            btn1.send_keys("Prince Of Songkla University")
            driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
            driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
            driver.find_element_by_xpath("//span[@class='select2-results']").click() 
            driver.find_element_by_xpath("//span[@class='searchButton']").click()

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
            driver.find_element_by_class_name('summary_CitLink').click()

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color'))) 
            driver.find_element_by_xpath('//*[contains(text(),"Research Areas")]').click()  # กดจากการค้าหา  ด้วย text

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="bold-text" and contains(text(), "Treemap")]')))  # hold until find text by CLASSNAME

            evens = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
            odds = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )

            categories_evens = get_df_by_rows(evens)
            categories_odds = get_df_by_rows(odds)

            df1 = pd.DataFrame(categories_evens, columns=['categories', 'count'])
            df2 = pd.DataFrame(categories_odds, columns=['categories', 'count'])

            df = pd.concat([df1,df2], axis = 0)
            df['count'] = df['count'].astype('int')
            df = df.sort_values(by='count', ascending=False)

        except Exception as e :
            df = None
            print('Something went wrong :', e)
        
        return df

    def chrome_driver_get_catagories_ISI():
        
        try: 
            # get datafreame by web scraping
            driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

            btn1 =driver.find_element_by_id('value(input1)')
            btn1.clear()
            btn1.send_keys("Prince Of Songkla University")
            driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
            driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
            driver.find_element_by_xpath("//span[@class='select2-results']").click() 
            driver.find_element_by_xpath("//span[@class='searchButton']").click()

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
            driver.find_element_by_class_name('summary_CitLink').click()

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color'))) 
            driver.find_element_by_xpath('//*[contains(text(),"Web of Science Categories")]').click()  # กดจากการค้าหา  ด้วย text

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="bold-text" and contains(text(), "Treemap")]')))  # hold until find text by CLASSNAME

            evens = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
            odds = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )

            categories_evens = get_df_by_rows(evens)
            categories_odds = get_df_by_rows(odds)

            df1 = pd.DataFrame(categories_evens, columns=['categories', 'count'])
            df2 = pd.DataFrame(categories_odds, columns=['categories', 'count'])

            df = pd.concat([df1,df2], axis = 0)
            df['count'] = df['count'].astype('int')
            df = df.sort_values(by='count', ascending=False)

        except Exception as e :
            df = None
            print('Something went wrong :', e)
        
        return df

    if request.POST['row']=='Query1':  #project
        try:
            sql_cmd =  """select  FUND_BUDGET_YEAR as budget_year , 
                                    sum(sum_budget_plan) as budget 
                            from importdb_prpm_v_grt_project_eis
                            group by FUND_BUDGET_YEAR
                            having FUND_BUDGET_YEAR is not null and budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1
                            order by 1
             """                                               

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string) 

            # save to csv
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/query_graph1.csv""", index = False, header=True)
            ###### get time #####################################
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row1'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query2': #team
        try:
           
            sql_cmd =  """SELECT 
                                A.camp_owner,
                                A.faculty_owner,
                                A.FUND_BUDGET_YEAR as budget_year,
                                sum(A.SUM_BUDGET_PLAN) as budget
                        FROM importdb_prpm_v_grt_project_eis as A
                        where FUND_BUDGET_YEAR BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1
                        and		 A.camp_owner is not null and 
                        A.faculty_owner is not null
                        GROUP BY 1, 2, 3
            """

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string) 

            # save to csv
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/query_graph2.csv""", index = False, header=True)
            ###### get time #####################################
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

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
                        where budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR)) -10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1 and camp_owner IS NOT null
                        GROUP BY 1, 2
            """
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)

            # save to csv
            if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/query_graph3.csv""", index = False, header=True)
            ###### get time #####################################
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            ###################################################
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
                        WHERE (PROJECT_FINISH_DATE <= PROJECT_END_DATE) and (PROJECT_FINISH_DATE is not null) and (year(PROJECT_END_DATE) BETWEEN YEAR(NOW())-10 AND YEAR(NOW())-1)
                        group by 1 
                        order by 1
            """    
            #เสร็จไม่ทัน
            sql_cmd2 =  """SELECT 
                            year(PROJECT_END_DATE) as year,
                            count(year(PROJECT_END_DATE)) as n
                        FROM `importdb_prpm_v_grt_project_eis` 
                        WHERE PROJECT_FINISH_DATE > PROJECT_END_DATE  and PROJECT_FINISH_DATE is not null and (year(PROJECT_END_DATE) BETWEEN YEAR(NOW())-10 AND YEAR(NOW())-1)
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
            
            # save to csv
            if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                    
            print("graph4 save csv")
            df.to_csv ("""mydj1/static/csv/query_graph4.csv""", index = False, header=True)
            ###### get time #####################################
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            whichrows = 'row4'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query5':   # ISI SCOPUS Citation
        # api-endpoint 
        dt = datetime.now()
        year = dt.year
        try:
            sco_df = sco(year)  # get scopus dataframe จาก API scopus_search
            # print(sco_df)
            if(sco_df is None): 
                print("Scopus ERROR")
            else:
                print("finished_Scopus")

            isi_df = isi()  # get ISI dataframe จาก web Scraping
            # print(isi_df)
            if(isi_df is None): 
                print("ISI ERROR 1 time, call isi() again....")
                isi_df = isi()
                if(isi_df is None): 
                    print("ISI ERROR 2 times, break....")
            else:
                print("finished_ISI")

            ranking = 'sco:'+str(sco_df['record_count'][0])+', isi:'+str(isi_df['record_count'][0])
            # print(ranking)
            # ใส่ ข้อมูลในฐานข้อมูล  sco isi tci ด้วย ปีปัจจุบัน
            obj, created = PRPM_ranking.objects.get_or_create(year = year+543, defaults ={ 'sco': sco_df['record_count'][0], 'isi': isi_df['record_count'][0], 'tci': 0})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.sco =  sco_df['record_count'][0]
                obj.isi =  isi_df['record_count'][0]
                obj.tci =  2 
                obj.save()

            # ใส่ ข้อมูล sco isi tci ในฐานข้อมูล ด้วย ปีปัจจุบัน - 1 
            obj, created = PRPM_ranking.objects.get_or_create(year = year+543-1, defaults ={ 'sco': sco_df['record_count'][1], 'isi': isi_df['record_count'][1], 'tci': 0})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.sco =  sco_df['record_count'][1]
                obj.isi =  isi_df['record_count'][1]
                obj.tci =  9
                obj.save()

            # dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            print ("Saved")

        except Exception as e:
            print("Error: "+str(e))
            ranking = "error"

        checkpoint = "actionScopus"
        whichrows = 'row5'

    elif request.POST['row']=='Query6': #ตาราง จำนวนทุน 7 ประเภท revenue  
        
        sql_cmd01 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as Goverment from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "01" 
                        Group BY 1
                        
            """

        sql_cmd02 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as Revenue from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "02" 
                        Group BY 1
                       
            """
        sql_cmd03 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as Campus from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "03" 
                        Group BY 1
                        
            """
        
        sql_cmd04 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as Department from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "04" 
                        Group BY 1
                        
            """

        sql_cmd05 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as National from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "05" 
                        Group BY 1
                        
            """
    
        sql_cmd06 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as International from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "06" 
                        Group BY 1
                        
            """

        sql_cmd07 =  """SELECT FUND_BUDGET_YEAR as year, sum(SUM_BUDGET_PLAN) as Matching_fund from importdb_prpm_v_grt_project_eis
                        where FUND_SOURCE_ID = "07" 
                        Group BY 1
                        
            """
        con_string = getConstring('sql')
        df01 = pm.execute_query(sql_cmd01, con_string)
        df02 = pm.execute_query(sql_cmd02, con_string)
        df03 = pm.execute_query(sql_cmd03, con_string)
        df04 = pm.execute_query(sql_cmd04, con_string)
        df05 = pm.execute_query(sql_cmd05, con_string)
        df06 = pm.execute_query(sql_cmd06, con_string)
        df07 = pm.execute_query(sql_cmd07, con_string)
        df = pd.merge(df01, df02, left_on="year",right_on="year",how="left")
        df = pd.merge(df, df03, left_on="year",right_on="year",how="left")
        df = pd.merge(df, df04, left_on="year",right_on="year",how="left")
        df = pd.merge(df, df05, left_on="year",right_on="year",how="left")
        df = pd.merge(df, df06, left_on="year",right_on="year",how="left")
        df = pd.merge(df, df07, left_on="year",right_on="year",how="left")
        df = df.fillna(0)

        ###################################################
        # save path
        pm.save_to_db('revenues', con_string, df)
        
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        whichrows = 'row6'

        checkpoint = True

    elif request.POST['row']=='Query7':   #ตารางย่อย จากประเภทที่ 5 ---> Revenues From Goverment & PrivateCompany
        try:
            sql_cmd =  """with 
                            temp1 as (SELECT FUND_BUDGET_YEAR, sum(SUM_BUDGET_PLAN) as A from importdb_prpm_v_grt_project_eis
                            join importdb_prpm_r_fund_type on importdb_prpm_v_grt_project_eis.FUND_TYPE_ID = importdb_prpm_r_fund_type.FUND_TYPE_ID
                            where importdb_prpm_v_grt_project_eis.FUND_SOURCE_ID = 05  and importdb_prpm_r_fund_type.FUND_TYPE_GROUP = 1
                            Group BY FUND_BUDGET_YEAR
                            ),

                            temp2 as (SELECT FUND_BUDGET_YEAR, sum(SUM_BUDGET_PLAN) as B from importdb_prpm_v_grt_project_eis
                            join importdb_prpm_r_fund_type on importdb_prpm_v_grt_project_eis.FUND_TYPE_ID = importdb_prpm_r_fund_type.FUND_TYPE_ID
                            where importdb_prpm_v_grt_project_eis.FUND_SOURCE_ID = 05  and importdb_prpm_r_fund_type.FUND_TYPE_GROUP = 2
                            Group BY FUND_BUDGET_YEAR
                            ),

                            temp3 as (SELECT FUND_BUDGET_YEAR, sum(SUM_BUDGET_PLAN) as nnull from importdb_prpm_v_grt_project_eis
                            join importdb_prpm_r_fund_type on importdb_prpm_v_grt_project_eis.FUND_TYPE_ID = importdb_prpm_r_fund_type.FUND_TYPE_ID
                            where importdb_prpm_v_grt_project_eis.FUND_SOURCE_ID = 05  and importdb_prpm_r_fund_type.FUND_TYPE_GROUP is null
                            Group BY FUND_BUDGET_YEAR
                            )


                            select temp1.fund_budget_year, (temp1.A+IFNULL(temp3.nnull, 0)) as Governmentagencies, IFNULL(temp2.B, 0) as Privatecompany
                            from temp1 
                            left join temp2 on temp1.fund_budget_year = temp2.fund_budget_year
                            left join temp3 on temp1.fund_budget_year = temp3.fund_budget_year

                            
            """
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
           
            
            ###################################################
            # save path
            pm.save_to_db('revenues_national_g_p', con_string, df)   
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            whichrows = 'row7'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
    
    elif request.POST['row']=='Query8':   #ตาราง marker * และ ** ของแหล่งทุน 
        try:
            ################### แหล่งทุนใหม่ #######################
            sql_cmd =  """with temp as  (SELECT A.FUND_TYPE_ID, A.FUND_TYPE_TH,A.FUND_SOURCE_TH, C.Fund_type_group, count(A.fund_type_id) as count, A.fund_budget_year
                                        from importdb_prpm_v_grt_project_eis as A 
							            join importdb_prpm_r_fund_type as C on A.FUND_TYPE_ID = C.FUND_TYPE_ID
								        where  (A.FUND_SOURCE_ID = 05 or A.FUND_SOURCE_ID = 06 )
                                        group by 1, 2 ,3 ,4 
								        ORDER BY 5 desc)
																
                        select FUND_TYPE_ID from temp where count = 1 and (fund_budget_year >= YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1)
                        order by 1"""

            con_string = getConstring('sql')
            df1 = pm.execute_query(sql_cmd, con_string)
            df1['marker'] = '*'
            ################## แหล่งทุน ให้ทุนซ้ำ>=3ครั้ง  #####################
            sql_cmd2 =  """with temp as  (SELECT A.FUND_TYPE_ID, 
                                                A.FUND_TYPE_TH,
                                                A.FUND_SOURCE_TH, 
                                                C.Fund_type_group, 
                                                A.fund_budget_year
                                            from importdb_prpm_v_grt_project_eis as A 
                                            join importdb_prpm_r_fund_type as C on A.FUND_TYPE_ID = C.FUND_TYPE_ID
                                            where  (A.FUND_SOURCE_ID = 05 or A.FUND_SOURCE_ID = 06 )
                                            ORDER BY 1 desc
                                            ),
                                                                            
                                temp2 as (select * 
                                            from temp 
                                            where  (fund_budget_year  BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-5 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1)
                                        ),
            
                                temp3 as( select FUND_TYPE_ID, FUND_TYPE_TH,FUND_SOURCE_TH, fund_budget_year ,count(fund_type_id) as count
                                            from temp2
                                            group by 1
                                        )
                            
                                select FUND_TYPE_ID from temp3 where count >= 3"""

            con_string2 = getConstring('sql')
            df2 = pm.execute_query(sql_cmd2, con_string2)
            df2['marker'] = '**'
           
            ################## รวม df1 และ df2 ########################
            df = pd.concat([df1,df2],ignore_index = True)
            ###################################################
            # save path
            pm.save_to_db('q_marker_ex_fund', con_string, df)   
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            whichrows = 'row8'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
    
    elif request.POST['row']=='Query9':   #ตารางแหล่งทุนภายนอก  
        try:
            sql_cmd =  """with temp1 as (select A.fund_type_id
                                    ,A.fund_type_th
                                    ,A.FUND_TYPE_GROUP
                                    ,B.fund_type_group_th
                                    ,A.fund_source_id
                        from importdb_prpm_r_fund_type as A
                        left join fund_type_group as B on A.FUND_TYPE_GROUP = B.FUND_TYPE_GROUP_ID
                        where flag_used = 1 and (fund_source_id = 05 or fund_source_id = 06 )
                        order by 1 )

                        select A.fund_type_id,A.fund_type_th,A.fund_source_id,A.FUND_TYPE_GROUP, A.FUND_TYPE_GROUP_TH, B.marker
                        from temp1 as A
                        left join q_marker_ex_fund as B on A.fund_type_id = B.fund_type_id
                        order by 4 desc
                                 """
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            df = df.fillna("")
            ###################################################
            # save path
            pm.save_to_db('q_ex_fund', con_string, df)   
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            whichrows = 'row9'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query10': # Research Areas
        
        path = """importDB"""
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
        WebDriverWait(driver, 10)
        try:
            df = chrome_driver_get_research_areas_ISI()
            if df is None:
                print("fail to get df, call again...")
                df = chrome_driver_get_research_areas_ISI()
        
            driver.quit()
            ######### Save to DB
            con_string = getConstring('sql')
            pm.save_to_db('research_areas_isi', con_string, df) 

            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
            # save to csv        
            df[:20].to_csv ("""mydj1/static/csv/research_areas_20_isi.csv""", index = False, header=True)
                        
            ###### get time #####################################
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

        whichrows = 'row10'

    elif request.POST['row']=='Query11': # ISI catagories  
         
        path = """importDB"""
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
        WebDriverWait(driver, 10)
        
        try: 
            df = chrome_driver_get_catagories_ISI()
            if df is None:
                print("fail to get df, call again...")
                df = chrome_driver_get_catagories_ISI()    

            driver.quit()
            ######### Save to DB
            con_string = getConstring('sql')
            pm.save_to_db('categories_isi', con_string, df) 


            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
            # save to csv        
            df[:20].to_csv ("""mydj1/static/csv/categories_20_isi.csv""", index = False, header=True)
                       
            ###### get time #####################################
           
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

        whichrows = 'row11'

    elif request.POST['row']=='Query12':   # Query 9 รูปกราฟ ที่จะแสดงใน ตารางของ tamplate revenues.html
        try:
            ### 7 กราฟ ในหัวข้อ 1 - 7
            FUND_SOURCES = ["Campus","Department","Goverment","International","Matching_fund","National","Revenue"]

            for FUND_SOURCE in FUND_SOURCES:
                # sql_cmd = """select year, """+FUND_SOURCE+""" from revenues 
                #         where year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-9 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
            
                # con_string = getConstring('sql')
                # df = pm.execute_query(sql_cmd, con_string) 
                
                sql_cmd3 = """select year, """+FUND_SOURCE+""" from revenues 
                        where year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-9 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""
                con_string3 = getConstring('sql')
                df = pm.execute_query(sql_cmd3, con_string3) 
                
                df2 = df[0:9]  # กราฟเส้นทึบ
                df3 = df[8:]  # กราฟเส้นประ
                
                fig = go.Figure(data=go.Scatter(x=df2["year"], y=df2[FUND_SOURCE] ,line=dict( color='royalblue')),
                                 layout= go.Layout( xaxis={
                                                'zeroline': False,
                                                'showgrid': False,
                                                'visible': False,},
                                        yaxis={
                                                'showgrid': False,
                                                'showline': False,
                                                'zeroline': False,
                                                'visible': False,
                                        })
                                )

                fig.add_trace(go.Scatter(x=df3["year"], y=df3[FUND_SOURCE]
                        ,line=dict( width=2, dash='dot',color='royalblue') )
                    )

                fig.update_layout(showlegend=False)
                fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
                fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

                plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
                
                # write an img
                if not os.path.exists("mydj1/static/img"):
                    os.mkdir("mydj1/static/img")
                fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE+"""1.png""")

                # save to csv
                if not os.path.exists("mydj1/static/csv"):
                        os.mkdir("mydj1/static/csv")       
                df.to_csv ("""mydj1/static/csv/"""+FUND_SOURCE.capitalize()+""".csv""", index = False, header=True)
            
            ### 2 กราฟย่อย ใน หัวข้อ 5.1 และ 5.2
            FUND_SOURCES2 = ["Governmentagencies","Privatecompany"]

            for FUND_SOURCE2 in FUND_SOURCES2:
                sql_cmd = """select fund_budget_year as year, """+FUND_SOURCE2+""" from revenues_national_g_p  
                    where fund_budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-9 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""
            
                con_string = getConstring('sql')
                df = pm.execute_query(sql_cmd, con_string) 
                df2 = df[0:9]  # กราฟเส้นทึบ
                df3 = df[8:]  # กราฟเส้นประ
                fig = go.Figure(data=go.Scatter(x=df2["year"], y=df2[FUND_SOURCE2],line=dict( color='royalblue')), layout= go.Layout( xaxis={
                                                'zeroline': False,
                                                'showgrid': False,
                                                'visible': False,},
                                        yaxis={
                                                'showgrid': False,
                                                'showline': False,
                                                'zeroline': False,
                                                'visible': False,
                                        }))

                #### กราฟเส้นประ ###
                fig.add_trace(go.Scatter(x=df3["year"], y=df3[FUND_SOURCE2]
                        ,line=dict( width=2, dash='dot',color='royalblue') )
                    )

                fig.update_layout(showlegend=False)
                fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
                fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

                plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
                
                if not os.path.exists("mydj1/static/img"):
                    os.mkdir("mydj1/static/img")
                fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE2+"""1.png""")
                
                 # save to csv
                if not os.path.exists("mydj1/static/csv"):
                        os.mkdir("mydj1/static/csv")       
                df.to_csv ("""mydj1/static/csv/"""+FUND_SOURCE2.capitalize()+""".csv""", index = False, header=True)
    
            whichrows = 'row12'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)          

    elif request.POST['row']=='Query13': # Filled area chart กราฟหน้าแรก รูปแรก
        try:
           
            sql_cmd = """select *
                    from revenues
                    where year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
        

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string) 

            # save to csv
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/Filled_area_chart.csv""", index = False, header=True)
            ###### get time #####################################
            
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            whichrows = 'row13'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query15': # Citation ISI and H-index
        dt = datetime.now()
        year = dt.year
        cited, h_index = cited_isi()

        if(cited is None): 
                print("Get Citation ERROR 1 time, call cited_isi() again....")
                ccited, h_index = cited_isi()
                if(cited is None): 
                    print("Get Citation ERROR 2 times, break....")
                else:
                    print("finished Get Citation")
        else:
            print("finished Get Citation")

        print(cited)
        print(h_index)
        try:   
            
            # ใส่ ข้อมูลในฐานข้อมูล  sco isi tci ด้วย ปีปัจจุบัน
            obj, created = PRPM_ranking_cited_isi.objects.get_or_create(year = year+543, defaults ={ 'cited': cited['cited'][0]})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.cited =  cited['cited'][0]
                obj.save()
            print("ddddd1")
            # ใส่ ข้อมูล sco isi tci ในฐานข้อมูล ด้วย ปีปัจจุบัน - 1 
            obj, created = PRPM_ranking_cited_isi.objects.get_or_create(year = year+543-1, defaults ={ 'cited': cited['cited'][1]})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.cited =  cited['cited'][1]
                obj.save()

            ###### save h-index to csv ######
            df=pd.DataFrame({'h_index':h_index }, index=[0])
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/h_index.csv""", index = False, header=True)

            ##### timestamp ####
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            print ("Saved")

            whichrows = 'row15'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query16':   # head page
        try:
            ### จำนวนของนักวิจัย
            sql_cmd =  """SELECT COUNT(*) as count
                    FROM importdb_prpm_v_grt_pj_team_eis;
                    """
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            final_df=pd.DataFrame({'total_of_guys':df['count'].astype(int) }, index=[0])

            ### รายได้งานวิจัย
            sql_cmd =  """SELECT  sum(SUM_BUDGET_PLAN) as sum
                    FROM importdb_prpm_v_grt_project_eis
                    WHERE FUND_BUDGET_YEAR = YEAR(date_add(NOW(), INTERVAL 543 YEAR)) """
            df = pm.execute_query(sql_cmd, con_string)
            final_df["total_of_budget"] = df["sum"]

            ### จำนวนงานวิจัย 
            sql_cmd =  """select year, sco, isi
                            from importdb_prpm_ranking  
                            where year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""

            df = pm.execute_query(sql_cmd, con_string)
            final_df["num_of_pub_sco"] = df["sco"].astype(int)
            final_df["num_of_pub_isi"] = df["isi"].astype(int)

            ### หน่วยงานภายนอกที่เข้าร่วม 
            sql_cmd =  """SELECT count(*) as count 
                            from importdb_prpm_r_fund_type 
                            where flag_used = "1" and (fund_source_id = 05 or fund_source_id = 06) """

            df = pm.execute_query(sql_cmd, con_string)
            final_df["num_of_networks"] = df["count"].astype(int)
            print(final_df)
            ########## save to csv ##########      
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            final_df.to_csv ("""mydj1/static/csv/head_page.csv""", index = False, header=True)

            ##### timestamp ####
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            print ("Saved")

            whichrows = 'row16'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query17':   # ISI SCOPUS and Citation of ISI to CSV
        try:
            
            sql_cmd =  """select year, sco, isi from importdb_prpm_ranking
                            where  year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-20 
                            AND YEAR(date_add(NOW(), INTERVAL 543 YEAR)) """

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)

            sql_cmd =  """SELECT cited
                    FROM importdb_prpm_ranking_cited_isi
                    WHERE  year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-20 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                    """
            df2 = pm.execute_query(sql_cmd, con_string)

            df = pd.concat([df,df2],axis=1)
            
            ########## save to csv ##########      
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/isi_scopus.csv""", index = False, header=True)

            ##### timestamp ####
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            print ("Saved")

            whichrows = 'row17'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    if checkpoint:
        result = 'Dumped'
    elif checkpoint == 'actionScopus':
        result = ""+ranking
    else:
        result = 'Cant Dump'
    
    context={
        'result': result,
        'time':datetime.fromtimestamp(timestamp),
        'whichrow' : whichrows
    }
    return render(request,'importDB/dQueryReports.html',context)

def pageRevenues(request): # page รายได้งานวิจัย

    selected_year = datetime.now().year+543 # กำหนดให้ ปี ใน dropdown เป็นปีปัจจุบัน
    def get_head_page(): # get จำนวนของนักวิจัย 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    if request.method == "POST":
        filter_year =  request.POST["year"]   #รับ ปี จาก dropdown 
        print("post = ",request.POST )
        selected_year = int(filter_year)      # ตัวแปร selected_year เพื่อ ให้ใน dropdown หน้าต่อไป แสดงในปีที่เลือกไว้ก่อนหน้า(จาก year)
    else:
        filter_year = "YEAR(date_add(NOW(), INTERVAL 543 YEAR))"

    
    def get_budget_amount(): # แสดง จำนวนของเงิน 7 ประเภท ในตาราง
        sql_cmd =  """select * from revenues where year = """+filter_year

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        budget_type = df[["Goverment","Revenue","Campus","Department","National","International","Matching_fund"]]
              
        return budget_type.iloc[0]

    def get_percentage(): # แสดง % ของเงิน 7 ประเภท ในตาราง
        sql_cmd =  """select * from revenues where year = """+filter_year

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        result = df[["Goverment","Revenue","Campus","Department","National","International","Matching_fund"]] 
        # result.to_csv (r'C:\Users\Asus\Desktop\export_dataframe4.csv', index = False, header=True)
        result = result.apply(lambda x: x/x.sum()*100, axis=1)
        result= result.round(2)
        # print("dddddd")
        # print(result)
        # print(result.sum(axis = 1))
        

        return result.iloc[0]

    def get_width(): #แสดงค่าในตัวแปร width ของ หลอด %
        sql_cmd =  """select * from revenues where year = """+filter_year

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        budget_type = df[["Goverment","Revenue","Campus","Department","National","International","Matching_fund"]]
        sumall = budget_type.sum(axis=1)
        results = budget_type.applymap(lambda x:(x/sumall)*100)
        per = results.applymap(lambda x:(180*x/100))
        
        return per.iloc[0]
    
    def get_budget_goverment_privatecomp(): # แสดง จำนวนเงินของ ตารางย่อยเงินทุนในประเทศ หน่วยงานภาครัฐ และ หน่วยงานเอกชน
        sql_cmd =  """select * from revenues_national_g_p where fund_budget_year = """+filter_year

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        # percen ของ Goverment Agencies (nper) และ ของ privatecomp (pper)
        df["nper"] = df["Governmentagencies"].apply(lambda x: x/ df[["Governmentagencies","Privatecompany"]].sum(axis=1)*100).round(2)  
        df["pper"] = df["Privatecompany"].apply(lambda x: x/df[["Governmentagencies","Privatecompany"]].sum(axis=1)*100).round(2)

        # ความกว้างของหลอดpercen ในตาราง ของ Goverment Agencies (wnper) และ ของ privatecomp (wpper)
        df["wnper"] = df["nper"].apply(lambda x:(180*x/100))
        df["wpper"] = df["pper"].apply(lambda x:(180*x/100))
 
        return df.iloc[0]
    
    def graph1():  # แสดงกราฟโดนัด ของจำนวน เงินทั้ง 7 หัวข้อ
        sql_cmd =  """select * from revenues where year = """+filter_year
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        df = df[["Goverment","Revenue","Campus","Department","National","International","Matching_fund"]]
        
        newdf = pd.DataFrame({'BUDGET_TYPE' : ["เงินงบประมาณแผ่นดิน","เงินรายได้มหาวิทยาลัย","เงินรายได้วิทยาเขต"
                                                ,"เงินรายได้คณะ/หน่วยงาน","เงินทุนภายนอก(ในประเทศ)","เงินทุนภายนอก (ต่างประเทศ)","เงินทุนร่วม"]})
        df = df.T # ทรานโพส เพื่อให้ plot เป็นกราฟได้สะดวก

        newdf["budget"] = 0.0  # สร้าง column ใหม่
        for n in range(0,7):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = df[0][n] 

        df = newdf.copy()   # copy เพื่อ ใช้ในการรวมจำนวนเงินทั้งหมด แสดงในกราฟ ตรงกลางของ donut
        # print("*donut*******")
        # s = pd.to_numeric(newdf["budget"], errors='coerce')
        # print( type(s))
        
        # newdf["budget"] = newdf["budget"].apply(lambda x: x/newdf["budget"].sum()*100)
        # newdf = newdf.round()

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' ,color_discrete_sequence=px.colors.sequential.haline, hole=0.5 ,)
        fig.update_traces(textposition='inside', textfont_size=14)
        fig.update_traces(hoverinfo="label+percent+name",
                  marker=dict(line=dict(color='#000000', width=2)))

        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        # fig.update_layout( width=1000, height=485)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))
        

        fig.update_layout( annotations=[dict(text="<b>{:,.2f}</b>".format(df.budget.sum()), x=0.50, y=0.5,  font_color = "black", showarrow=False)]) ##font_size=20,
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def campus_budget():
        sql_cmd =  """SELECT camp_owner, sum(budget) as budget FROM querygraph2 where budget_year = """+filter_year+"""
                        group by camp_owner"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        df2 = df.budget.T
        # print(df2)
        print(df2.sum())

        return df2


    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################
        'budget' : get_budget_amount(),
        'width': get_width(),
        'year' :range((datetime.now().year)+543-10,(datetime.now().year+1)+543),
        'filter_year': selected_year,
        'graph1' :graph1(),
        'percentage': get_percentage(),
        'national' : get_budget_goverment_privatecomp(),
        'campus' : campus_budget(),
        


    }
    
    
    
    return render(request, 'importDB/revenues.html', context)

def revenues_graph(request, value):  # รับค่า value มาจาก url

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def graph(source):
        df = pd.read_csv("""mydj1/static/csv/"""+source+""".csv""")
        
        df2 = df[0:9]  # df สำหรับ กราฟเส้นทึบ
        df3 = df[8:]  #df สำหรับ กราฟเส้นประ
        
        # กำหนดค่าเริ่มต้น ว่าจะต้องมี กี่ row, col และมี กราฟ scatter + table 
        fig = make_subplots(rows=1, cols=2,
                            column_widths=[0.7, 0.3],
                            specs=[[{"type": "scatter"},{"type": "table"}]]
                            )

        ### สร้าง กราฟเส้นทึบ ####
        fig.add_trace(go.Scatter(x=df2["year"], y=df2[source],line=dict( color='royalblue')))
        ### สร้าง กราฟเส้นประ ####
        fig.add_trace(go.Scatter(x=df3["year"], y=df3[source]
                ,line=dict( width=2, dash='dot',color='royalblue') )
            )

        labels = { "Goverment":"เงินงบประมาณแผ่นดิน","Revenue":"เงินรายได้มหาวิทยาลัย","Campus":"เงินรายได้วิทยาเขต"
                    ,"Department":"เงินรายได้คณะ/หน่วยงาน","National":"เงินทุนภายนอก(ในประเทศ)","International":"เงินทุนภายนอก (ต่างประเทศ)",
                    "Matching_fund":"เงินทุนร่วม","Privatecompany":"หน่วยงานภาคเอกชน","Governmentagencies":"หน่วยงานภาครัฐ"}
 

        fig.update_layout(showlegend=False)
        fig.update_layout(title_text=f"<b>รายได้งานวิจัยจาก {labels[source]} 10 ปี ย้อนหลัง </b>",
                        height=500,width=1000,
                        xaxis_title="ปี พ.ศ",
                        yaxis_title="จำนวนเงิน (บาท)",
                        font=dict(
                            size=14,
                        ))

        ### ตาราง ####
        df[source] = df[source].apply(moneyformat)

        fig.add_trace(
            go.Table(
                columnwidth = [100,200],
                header=dict(values=["<b>Year</b>","<b>Budget\n<b>"],
                            fill = dict(color='#C2D4FF'),
                            align = ['center'] * 5),
                cells=dict(values=[df["year"], df[source]],
                        fill = dict(color='#F5F8FF'),
                        align = ['center','right'] * 5))
                        
                , row=1, col=2)
        fig.update_layout(autosize=True)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)

        
        return  plot_div

    source = value
    # for k, v in enumerate(request.POST.keys()):  # รับ key ของตัวแปร dictionary จาก ปุ่ม view มาใส่ในตัวแปร source เช่น source = Goverment
    #     if (k == 1):
    #         source = v
    print(source)
    context={
        'plot1' : graph(source),
    }
        
    return render(request,'importDB/revenues_graph.html', context)

def revenues_table(request):  # รับค่า value มาจาก url

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def get_table(year,source,check):

        sql_cmd=""
        if(check):
            index = { "Goverment":"01","Revenue":"02","Campus":"03"
                        ,"Department":"04","National":"05","International":"06",
                        "Matching_fund":"07"}
            
            source_index = index[source]

            sql_cmd =  """select psu_project_id,submit_name_surname_th,camp_owner,faculty_owner,fund_th,sum_budget_plan,pj_status_th 
                            from importdb_prpm_v_grt_project_eis
                            where fund_budget_year = """+year+""" and fund_source_id = """+source_index
        else:
            if source == "Privatecompany":
                sql_cmd = """select A.psu_project_id,A.submit_name_surname_th,A.camp_owner,A.faculty_owner,A.fund_th,A.sum_budget_plan,A.pj_status_th 
                        from importdb_prpm_v_grt_project_eis as A
                        join importdb_prpm_r_fund_type as B on A.FUND_TYPE_ID = B.FUND_TYPE_ID
                        where A.fund_budget_year = """+year+""" and A.fund_source_id = '05' and B.FUND_TYPE_GROUP = "2" """
            else:
                sql_cmd = """select A.psu_project_id,A.submit_name_surname_th,A.camp_owner,A.faculty_owner,A.fund_th,A.sum_budget_plan,A.pj_status_th 
                        from importdb_prpm_v_grt_project_eis as A
                        join importdb_prpm_r_fund_type as B on A.FUND_TYPE_ID = B.FUND_TYPE_ID
                        where A.fund_budget_year = """+year+""" and A.fund_source_id = '05' and (B.FUND_TYPE_GROUP = "1" or B.FUND_TYPE_GROUP = 3) """
                    
        print(sql_cmd)
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        df['sum_budget_plan'] = df['sum_budget_plan'].apply(moneyformat)
        # print(df)
        return df
    
    labels = { "Goverment":"เงินงบประมาณแผ่นดิน","Revenue":"เงินรายได้มหาวิทยาลัย","Campus":"เงินรายได้วิทยาเขต"
                    ,"Department":"เงินรายได้คณะ/หน่วยงาน","National":"เงินทุนภายนอก(ในประเทศ)","International":"เงินทุนภายนอก (ต่างประเทศ)",
                    "Matching_fund":"เงินทุนร่วม","Privatecompany":"หน่วยงานภาคเอกชน","Governmentagencies":"หน่วยงานภาครัฐ"}
    temp=[]
    
    for k, v in enumerate(request.POST.keys()):  # รับ key ของตัวแปร dictionary จาก ปุ่ม view มาใส่ในตัวแปร source เช่น source = Goverment
        if(k==1):
            temp = v.split("/")
    year = temp[0]
    source = temp[1]
    check = False if (source == "Privatecompany") | (source == "Governmentagencies") else True
    print(check)
    context={
        'a_table' : get_table(year,source,check),
        'year' : year,
        'source' : labels[source]
    }
        
    return render(request,'importDB/revenues_table.html', context)

def pageExFund(request): # page รายได้จากทุนภายนอกมหาวิทยาลัย

    def get_head_page(): # get จำนวนของนักวิจัย 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    # globle var
    selected_i = ""
    queryByselected = ""
    choices = ["----ทั้งหมด----","หน่วยงานภาครัฐ","หน่วยงานภาคเอกชน"]

    # check ตัวเลื่อกจาก dropdown
    if request.method == "POST" and "selected" in request.POST:
        re =  request.POST["selected"]   #รับ ตัวเลือก จาก dropdown 
        # print("post = ",request.POST )
        selected_i = re    # ตัวแปร selected_i เพื่อ ให้ใน dropdown หน้าต่อไป แสดงในปีที่เลือกไว้ก่อนหน้า(จาก selected)   
    else:
        selected_i = "----ทั้งหมด----"
        
    ##########################################################
    ################ เปลี่ยน selected_i เพื่อ นำไปเป็นค่า 1 หรือ 2 ที่สามารถคิวรี่ได้
    if selected_i == "หน่วยงานภาครัฐ":
        queryByselected = "1"
    elif selected_i == "หน่วยงานภาคเอกชน": 
        queryByselected = "2"
    else:
        queryByselected = "3"
    ##########################################################

   
    def getNationalEXFUND():
        
        if queryByselected=="3":
            # ---ทั้งหมด--- ถูกเลือก
            sql_cmd =  """select * from q_ex_fund
                            where fund_source_id = 05
                            order by 6 desc """
        else:  
            # 1 และ 2 ถูกเลือก 
            sql_cmd =  """select * from q_ex_fund    
                            where fund_source_id = 05 and FUND_TYPE_GROUP ="""+ queryByselected +""" 
                            order by 6 desc """

        # print(sql_cmd)
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        # print(df)
        return df

      
    def getInterNationalEXFUND():
        
        sql_cmd =  """select * from q_ex_fund
                            where fund_source_id = 06
                            order by 6 desc """

        # print(sql_cmd)
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        return df

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################
        #### tables1 
         'choices' : choices,
         'selected_i' : selected_i,
        'df_Na_Fx_fund' : getNationalEXFUND(),
        #### tables1 
        'df_Inter_Fx_fund':getInterNationalEXFUND(),
    }

    # return render(request, 'importDB/exFund.html', context)
    return render(request, 'importDB/exFund.html', context)

def pageRanking(request):

    def get_head_page(): # get จำนวนของนักวิจัย 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    def tree_map():

        df = pd.read_csv("""mydj1/static/csv/categories_20_isi.csv""")
        
        fig = px.treemap(df, path=['categories'], values='count',
                  color='count', 
                  hover_data=['categories'],
                  color_continuous_scale='Plasma',
                )     
        fig.data[0].textinfo = 'label+text+value'
        fig.update_traces(textfont_size=16)
        fig.data[0].hovertemplate = "<b>categories=%{customdata[0]}<br>count=%{value}<br></b>"
        fig.update_layout( hoverlabel = dict( bgcolor = 'white' ) )
            
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def bar_chart1(): #categories

        df = pd.read_csv("""mydj1/static/csv/categories_20_isi.csv""")
        
        fig = px.bar(df[:10], y = 'categories', x = "count" , text = 'count', orientation='h')
        fig.update_traces(texttemplate = "%{text:,f}", textposition= 'inside' )
        fig.update_layout(uniformtext_minsize = 8, uniformtext_mode = 'hide')
        # fig.update_layout( xaxis_tickangle=-45)    
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def bar_chart2(): #research_areas

        df = pd.read_csv("""mydj1/static/csv/research_areas_20_isi.csv""")
        
        fig = px.bar(df[:10], y = 'categories', x = "count" , text = 'count', orientation='h')
        fig.update_traces(texttemplate = "%{text:,f}", textposition= 'inside' )
        fig.update_layout(uniformtext_minsize = 8, uniformtext_mode = 'hide')
        # fig.update_layout( xaxis_tickangle=-45)    
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def line_chart_total_publications():

        df0 = pd.read_csv("""mydj1/static/csv/isi_scopus.csv""")

        ####  กราฟเส้นทึบ
        df = df0[-20:-1]
        # df1 = pd.DataFrame({"year":df["year"], "count": df["sco"] ,"type":"Scopus"})
        # df2 = pd.DataFrame({"year":df["year"], "count": df["isi"] ,"type":"ISI"})
        # newdf = pd.concat([df1,df2], axis = 0)
        
        # fig = px.line(newdf, x="year", y="count", color='type')
        fig = go.Figure(data = go.Scatter(x=df["year"], y=df["sco"],
                    mode='lines+markers',
                    name='Scopus' ,line=dict( width=2,color='royalblue')  ) )

        fig.add_trace(go.Scatter(x=df["year"], y=df["isi"],
                    mode='lines+markers',
                    name='ISI',line=dict( width=2,color='red') ))
        
        # ####  กราฟเส้นประ

        df2 = df0[-2:]
        # fig.add_trace(go.Scatter(x=df2["year"], y=df2["sco"],
        #             mode='markers',line=dict( width=2, dash='dot',color='royalblue'),showlegend=False,hoverinfo='skip'))
        # fig.add_trace(go.Scatter(x=df2["year"], y=df2["isi"],
        #             mode='markers' ,line=dict( width=2, dash='dot',color='red'),showlegend=False ,hoverinfo='skip') )

        fig.add_trace(go.Scatter(x=df2["year"], y=df2["sco"],
                    mode='markers',name='Scopus',line=dict( width=2, dash='dot',color='royalblue'),showlegend=False))
        fig.add_trace(go.Scatter(x=df2["year"], y=df2["isi"],
                    mode='markers',name='ISI' ,line=dict( width=2, dash='dot',color='red'),showlegend=False))

        
        fig.update_traces(mode="markers+lines", hovertemplate=None)
        fig.update_layout(hovermode="x")    
        fig.update_layout(
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Number of Publications</b>",
        )
        fig.update_layout(legend=dict(x=0, y=1.1))

        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear',
                tick0 = 2554,
                dtick = 2
            )
        )

        fig.update_layout(legend=dict(orientation="h"))
        fig.update_layout(
            margin=dict(t=55),
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def line_chart_cited_per_year():

        df = pd.read_csv("""mydj1/static/csv/isi_scopus.csv""")

        df1 = df[-20:-1]
        fig = go.Figure(data = go.Scatter(x=df1["year"], y=df1["cited"],
                    mode='lines+markers',
                    name='ISI' ,line=dict( width=2,color='red') ,showlegend=False, ) )

        df2 = df[-2:]
        fig.add_trace(go.Scatter(x=df2["year"], y=df2["cited"],
                    mode='markers',name='ISI',line=dict( width=2, dash='dot',color='red'),showlegend=False))

        # fig = px.scatter(df, x=df["year"], y=df["cited"])
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear',
                tick0 = 2554,
                dtick = 2
            )
        )
        fig.update_layout(
            margin=dict(t=50),
        )
        
        fig.update_xaxes(showspikes=True)
        fig.update_yaxes(showspikes=True)

        fig.update_layout(
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Sum of Times Cited</b>",
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def sum_of_cited():
        
        df = pd.read_csv("""mydj1/static/csv/isi_scopus.csv""")
        return df["cited"].sum()

    def avg_per_items():

        df = pd.read_csv("""mydj1/static/csv/isi_scopus.csv""")
        df["cited"] =  df["cited"].astype('int')
        df["isi"] = df["isi"].astype('int')
        avg = (df["cited"].sum())/(df["isi"].sum())
        print("avg ",avg)
        return avg
    
    def avg_per_year():
        
        df = pd.read_csv("""mydj1/static/csv/isi_scopus.csv""")

        mean = np.mean(df["cited"])
        print("mean ",mean)
        return mean
    
    def total_publication():
        df = pd.read_csv("""mydj1/static/csv/isi_scopus.csv""")

        _sum = np.sum(df["isi"].astype('int'))
        print("mean ",_sum)
        return _sum
    
    def h_index():
        df = pd.read_csv("""mydj1/static/csv/h_index.csv""")
        
        return df["h_index"]

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################

        #### Graph
        # 'tree_map' : tree_map(),
        'bar_chart1' : bar_chart1(),
        'bar_chart2' : bar_chart2(),
        'line_chart_publication' :line_chart_total_publications(),
        'line_chart_cited' : line_chart_cited_per_year(),
        'sum_cited' :sum_of_cited(),
        'avg_per_items' :avg_per_items(),
        'avg_per_year' :avg_per_year(),
        'h_index' : h_index(),
        'total_publication' :total_publication(),
    }

    return render(request,'importDB/ranking.html', context)   