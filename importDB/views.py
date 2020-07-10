from django.shortcuts import render    # หมายถึง เป็นการเรียกจาก Template ที่เราสร้างไว้
from django.http import HttpResponse   # หมายถึง เป็นการ วาด HTML เอง
import pandas as pd
import numpy as np
import os
import json
import requests
from pprint import pprint

# เกี่ยวกับวันที่ 
from datetime import datetime
import time

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

    def graph8(filter_year):  # แสดงกราฟโดนัด ของจำนวน เงินทั้ง 11 หัวข้อ
        
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year"}, errors="raise")
        re_df =df[df["budget_year"]==int(filter_year)]
        newdf = pd.DataFrame({'BUDGET_TYPE' : ["สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)"
                                       ,"เงินงบประมาณแผ่นดิน"
                                       ,"เงินกองทุนวิจัยมหาวิทยาลัย"
                                       ,"เงินจากแหล่งทุนภายนอก ในประเทศไทย"
                                       ,"เงินจากแหล่งทุนภายนอก ต่างประเทศ"
                                       ,"เงินรายได้มหาวิทยาลัย"
                                       ,"เงินรายได้คณะ (เงินรายได้)"
                                       ,"เงินรายได้คณะ (กองทุนวิจัย)"
                                       ,"เงินกองทุนวิจัยวิทยาเขต"
                                       ,"เงินรายได้วิทยาเขต"
                                       ,"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง"     
                            ]})
        
        newdf["budget"] = 0.0

        for n in range(0,11):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = re_df[str(n)]

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' ,color_discrete_sequence=px.colors.sequential.haline, hole=0.5 ,)
        fig.update_traces(textposition='inside', textfont_size=14)
        # fig.update_traces(hoverinfo="label+percent+name",
        #           marker=dict(line=dict(color='#000000', width=2)))

        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        fig.update_layout( height=600)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))

        fig.update_layout( annotations=[dict(text="<b> &#3647; {:,.2f}</b>".format(newdf.budget.sum()), x=0.50, y=0.5,  font_color = "black", showarrow=False)]) ##font_size=20,
        # fig.update_traces(hovertemplate='%{name} <br> %{value}') 
         
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

    elif request.POST['row']=='Dump2':  #team
        try:
            
            sql_cmd =""" select * from research60.v_grt_pj_team_eis"""
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
            
            ###########################################################
            ##### save data ที่ไม่ได้ clean ลง ฐานข้อมูล mysql ####
            ############################################################
            uid2 = 'root'
            pwd2 = ''
            host2 = 'localhost'
            port2 = 3306
            db2 = 'mydj2'
            con_string = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

            pm.save_to_db('importdb_prpm_v_grt_pj_team_eis', con_string, df)

            ###########################################################
            ##### clean data ที่ sum(lu_percent) = 0 ให้ เก็บค่าเฉลี่ยแทน ####
            ############################################################
            
            for i in range(1,14):
                df2 = pd.read_csv(r"""mydj1/static/csv/clean_lu/edit_lu_percet_"""+str(i)+""".csv""")
                df.loc[df['psu_project_id'].isin(df2['psu_project_id']), ['lu_percent']] = 100/i
           
            pm.save_to_db('cleaned_prpm_team_eis', con_string, df)
            #############################################################
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

            ###########################################################
            ##### clean data ที่ budget_source_group_id = Null ให้ เก็บค่า 11 ####
            ############################################################
            df.loc[df['budget_source_group_id'].isna(), ['budget_source_group_id']] = 11
           
            pm.save_to_db('cleaned_prpm_budget_eis', con_string2, df)
            #############################################################   
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Dump4':   #FUND_TYPE
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
    
    elif request.POST['row']=='Dump5':   #assistant
        try:
            sql_cmd =  """SELECT 
                        *
                    FROM research60.v_grt_pj_assistant_eis
                    """

            con_string = getConstring('oracle')
            engine = create_engine(con_string, encoding="latin1" )
            df = pd.read_sql_query(sql_cmd, engine)
            # df = pm.execute_query(sql_cmd, con_string)
            

            ###################################################
            # save path
            con_string2 = getConstring('sql')
            pm.save_to_db('importdb_PRPM_v_grt_pj_assistant_eis', con_string2, df)

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

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

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

    if request.POST['row']=='Query1': # 12 types of budget 
        try:
            
            sql_cmd =  """with temp1 as ( 
                            select psu_project_id, budget_year, budget_source_group_id, sum(budget_amount) as budget_amount
                            from cleaned_prpm_budget_eis
                            where budget_group = 4 
                            group by 1, 2,3
                            order by 1
                        ),
                        
                        temp2 as (
                            select psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai,research_position_id,research_position_th ,lu_percent
                            from cleaned_prpm_team_eis
                            where psu_staff = "Y" 
                            order by 1
                        ),
                        
                        temp3 as (
                            select psu_project_id, fund_budget_year as submit_year
                            from importdb_prpm_v_grt_project_eis
                        ),
                        
                        temp4 as (
                
                            select t1.psu_project_id,t3.submit_year, t1.budget_year, budget_source_group_id, budget_amount, user_full_name_th, camp_name_thai,fac_name_thai, research_position_th,lu_percent, lu_percent/100*budget_amount as final_budget
                            from temp1 as t1
                            join temp2 as t2 on t1.psu_project_id = t2.psu_project_id
                            join temp3 as t3 on t1.psu_project_id = t3.psu_project_id
                            where 
								submit_year > 2553 and 
								research_position_id <> 2 
                            order by 2
                        ),

                        temp5 as (
												
								select  sg1.budget_source_group_id,sg1.budget_source_group_th, budget_year,camp_name_thai, fac_name_thai, sum(final_budget) as sum_final_budget
                                from temp4 
                                join importdb_budget_source_group as sg1 on temp4.budget_source_group_id = sg1.budget_source_group_id
                                group by 1,2,3,4,5
                                order by 1
						)
                                
                         select budget_year, budget_source_group_id,budget_source_group_th, sum(sum_final_budget) as sum_final_budget
                        from temp5
						where budget_year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 and YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                        group by 1,2,3 """

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)

            ############## build dataframe for show in html ##################
            index_1 = df["budget_year"].unique()
            df2 = pd.DataFrame(columns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],index = index_1)    
            for index, row in df.iterrows():
                df2[row['budget_source_group_id']][row["budget_year"]] = row['sum_final_budget']
            df2 = df2.fillna(0.0)
            df2 = df2.sort_index(ascending=False)
            df2 = df2.head(10).sort_index()
             
            
            ########## save to csv ตาราง เงิน 11 ประเภท ##########      
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df2.to_csv ("""mydj1/static/csv/12types_of_budget.csv""", index = True, header=True)

            ##################################################
            ################## save ตาราง แยกคณะ #############
            ##################################################
            sql_cmd =  '''with temp1 as ( 
                            select psu_project_id, budget_year, budget_source_group_id, sum(budget_amount) as budget_amount
                            from cleaned_prpm_budget_eis
                            where budget_group = 4 
                            group by 1, 2, 3
                            order by 1
                        ),
                        
                        temp2 as (
                            select psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai,research_position_id,research_position_th ,lu_percent
                            from cleaned_prpm_team_eis
                            where psu_staff = "Y" 
                            order by 1
                        ),
                        
                        temp3 as (
                            select psu_project_id, fund_budget_year as submit_year
                            from importdb_prpm_v_grt_project_eis
                        ),
                        
                        temp4 as (
                
                            select t1.psu_project_id,t3.submit_year, t1.budget_year, budget_source_group_id, budget_amount, user_full_name_th, camp_name_thai, 	
                                            fac_name_thai, research_position_th,lu_percent, lu_percent/100*budget_amount as final_budget
                            from temp1 as t1
                            join temp2 as t2 on t1.psu_project_id = t2.psu_project_id
                            join temp3 as t3 on t1.psu_project_id = t3.psu_project_id
                            where submit_year > 2553 and research_position_id <> 2 
                            order by 2
                        ),

                        temp5 as (select  sg1.budget_source_group_id,sg1.budget_source_group_th, budget_year,camp_name_thai, fac_name_thai, sum(final_budget) as sum_final_budget
                                from temp4
                                join importdb_budget_source_group as sg1 on temp4.budget_source_group_id = sg1.budget_source_group_id
                                group by 1,2,3,4,5
                                order by 1)
                                
                        select budget_year, budget_source_group_id,budget_source_group_th, camp_name_thai, fac_name_thai,sum(sum_final_budget) as sum_final_budget
                        from temp5
                        where budget_year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 and YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                        group by 1,2,3,4,5'''

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            df.to_csv ("""mydj1/static/csv/budget_of_fac.csv""", index = False, header=True)
            
            ##### timestamp ####
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            print ("Saved")

            whichrows = 'row1'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query2': # รายได้ในประเทศ รัฐ/เอกชน
        try:
            # sql_cmd =  """with temp1 as ( 
            #                 select psu_project_id, budget_year, budget_source_group_id, sum(budget_amount) as budget_amount
            #                 from cleaned_prpm_budget_eis
            #                 where budget_group = 4 
            #                 group by 1, 2
            #                 order by 1
            #             ),
                        
            #             temp2 as (
            #                 select psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai,research_position_id,research_position_th ,lu_percent
            #                 from cleaned_prpm_team_eis
            #                 where psu_staff = "Y" 
            #                 order by 1
            #             ),
                        
            #             temp3 as (
            #                 select A.psu_project_id, A.fund_budget_year as submit_year, A.fund_type_id, A.fund_type_th, B.fund_type_group, C.fund_type_group_th
			# 											from importdb_prpm_v_grt_project_eis as A
			# 											join importdb_prpm_r_fund_type as B on A.fund_type_id = B.fund_type_id
			# 											join fund_type_group as C on B.fund_type_group = C.fund_type_group_id
            #             )
												
                
            #         select t1.psu_project_id,fund_type_group, fund_type_group_th,t3.submit_year, t1.budget_year, budget_source_group_id, budget_amount, user_full_name_th, camp_name_thai,fac_name_thai, research_position_th,lu_percent, lu_percent/100*budget_amount as final_budget
            #         from temp1 as t1
            #         join temp2 as t2 on t1.psu_project_id = t2.psu_project_id
            #         join temp3 as t3 on t1.psu_project_id = t3.psu_project_id
            #         where  budget_year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 and YEAR(date_add(NOW(), INTERVAL 543 YEAR))
			# 				and submit_year > 2553 
			# 				and research_position_id <> 2 
            #         order by 3
                                                                    
            #  """
            sql_cmd = """with temp1 as ( 
                            select psu_project_id, budget_year, budget_source_group_id, sum(budget_amount) as budget_amount
                            from cleaned_prpm_budget_eis
                            where budget_group = 4 
																	and budget_source_group_id = 3
                            group by 1, 2,3 
                            order by 1
                        ),
                        
                        temp2 as (
                            select psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai,research_position_id,research_position_th ,lu_percent
                            from cleaned_prpm_team_eis
                            where psu_staff = "Y" 
                            order by 1
                        ),
                        
                        temp3 as (
                            select A.psu_project_id, A.fund_budget_year as submit_year, A.fund_type_id, A.fund_type_th, B.fund_type_group, C.fund_type_group_th
														from importdb_prpm_v_grt_project_eis as A
														left join importdb_prpm_r_fund_type as B on A.fund_type_id = B.fund_type_id
														left join fund_type_group as C on B.fund_type_group = C.fund_type_group_id
                        )
											
												
									  select t1.budget_year,fund_type_group, fund_type_group_th, camp_name_thai,fac_name_thai,lu_percent, lu_percent/100*budget_amount as final_budget
                    from temp1 as t1
                    join temp2 as t2 on t1.psu_project_id = t2.psu_project_id
                    join temp3 as t3 on t1.psu_project_id = t3.psu_project_id
                    where  budget_year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 and YEAR(date_add(NOW(), INTERVAL 543 YEAR))
							and submit_year > 2553 
							and research_position_id <> 2
							
                    order by 1
						
								"""

            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            
            ########## save to csv ตาราง เงิน 11 ประเภท ##########      
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")

            df.to_csv("""mydj1/static/csv/gover&comp.csv""", index = True, header=True)

        
            ##### timestamp ####
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

            print ("Saved")

            whichrows = 'row2'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query3': # Query รูปกราฟ ที่จะแสดงใน ตารางของ tamplate revenues.html
        try:
            ### 11 กราฟ ในหัวข้อ 1 - 11
            FUND_SOURCES = ["0","1","2","3","4","5","6","7","8","9","10","11"]  # ระบุหัว column ทั้ง 11 ห้วข้อใหญ๋
    
            df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""", index_col=0)

            now = datetime.now()
            now_year = now.year+543
            # temp = 0 
            # for i, index in enumerate(df.index):  # temp เพื่อเก็บ ว่า ปีปัจจุบัน อยุ่ใน row ที่เท่าไร
            #     if index == now_year:
            #         temp = i+1
            
            # for FUND_SOURCE in FUND_SOURCES:
            #     df2 = df[FUND_SOURCE][:temp-1].to_frame()   # กราฟเส้นทึบ
            #     df3 = df[FUND_SOURCE][temp-2:temp].to_frame()  # กราฟเส้นประ
            #     df4 = df['11'].to_frame() # กราฟ ของ อื่นๆ (สีเทา)
                
            #     # กราฟสีเทา
            #     fig = go.Figure(data=go.Scatter(x=df4.index, y=df4['11']
            #                             ,line=dict( width=2 ,color='#D5DBDB') )
            #     ,
            #     layout= go.Layout( xaxis={
            #                                     'zeroline': False,
            #                                     'showgrid': False,
            #                                     'visible': False,},
            #                             yaxis={
            #                                     'showgrid': False,
            #                                     'showline': False,
            #                                     'zeroline': False,
            #                                     'visible': False,
            #                             })
            #                 )

            #     # กราฟ เส้นประ
            #     fig.add_trace(go.Scatter(x=df3.index, y=df3[FUND_SOURCE]
            #                             ,line=dict( width=2, dash='dot',color='royalblue') )
            #                         )

            #     # กราฟ สีน้ำเงิน
            #     fig.add_trace(go.Scatter(x=df2.index, y=df2[FUND_SOURCE] ,line=dict( color='royalblue' ))
            #                         )
            
            #     fig.update_layout(showlegend=False)
            #     fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
            #     fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))
            #     plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
                
                
            #     df4 = df[FUND_SOURCE][:temp].to_frame() # เพื่อดึงตั้งแต่ row 0
                
            #     if FUND_SOURCE == "11":
            #         FUND_SOURCE = "13"  # เปลี่ยนเป็น 13 เพราะ 11 คือ เงินภายใน จากหน่วยงานรัฐ เดียวจะซ้ำกัน
            #         df4 = df4.rename(columns={"11": "13"})
                   
            #     # save to csv
            #     if not os.path.exists("mydj1/static/csv"):
            #             os.mkdir("mydj1/static/csv")       
            #     df4.to_csv ("""mydj1/static/csv/table_"""+FUND_SOURCE+""".csv""", index = True, header=True)
                
            #     # write an img
            #     if not os.path.exists("mydj1/static/img"):
            #         os.mkdir("mydj1/static/img")
            #     fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE+""".png""")

                

            # ##########################################
            # ### 2 กราฟย่อย ใน หัวข้อ 3.1 รัฐ และ 3.2 เอกชน
            # ###########################################
            # df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""", index_col=0)

            # df2 = df[df['fund_type_group'] == 1]
            # df2 = df2.groupby(["budget_year"])['final_budget'].sum()
            # df2 = df2.to_frame()

            # df3 = df[df['fund_type_group'] == 2]
            # df3 = df3.groupby(["budget_year"])['final_budget'].sum()
            # df3 = df3.to_frame()

            # df = pd.merge(df2,df3,on='budget_year',how='left')
            # df = df.fillna(0)
            # df = df.rename(columns={"final_budget_x": "11", "final_budget_y": "12"})

            # for i, index in enumerate(df.index): #  ต้องรู้ index เพราะว่า ข้อมูลอาจมีน้อยกว่า 10 ปีย้อนหลัง คือ มีเเค่ 3 ปีเริ่มต้น
            #     if index == now_year:
            #         temp = i+1

            # FUND_SOURCES2 = ["11","12"]
            # for FUND_SOURCE2 in FUND_SOURCES2:
                
            #     df2 = df[FUND_SOURCE2][:temp-1].to_frame()   # กราฟเส้นทึบ
            #     df3 = df[FUND_SOURCE2][temp-2:temp].to_frame()  # กราฟเส้นประ

            #     fig = go.Figure(data=go.Scatter(x=df2.index, y=df2[FUND_SOURCE2],line=dict( color='royalblue')), layout= go.Layout( xaxis={
            #                                     'zeroline': False,
            #                                     'showgrid': False,
            #                                     'visible': False,},
            #                             yaxis={
            #                                     'showgrid': False,
            #                                     'showline': False,
            #                                     'zeroline': False,
            #                                     'visible': False,
            #                             }))

            #     #### กราฟเส้นประ ###
            #     fig.add_trace(go.Scatter(x=df3.index, y=df3[FUND_SOURCE2]
            #             ,line=dict( width=2, dash='dot',color='royalblue') )
            #         )

            #     fig.update_layout(showlegend=False)
            #     fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
            #     fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

            #     plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
                
            #     if not os.path.exists("mydj1/static/img"):
            #         os.mkdir("mydj1/static/img")
            #     fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE2+""".png""")
                
            #      # save to csv
            #     if not os.path.exists("mydj1/static/csv"):
            #             os.mkdir("mydj1/static/csv")       
            #     df[FUND_SOURCE2].to_csv ("""mydj1/static/csv/table_"""+FUND_SOURCE2+""".csv""", index = True, header=True)
            

            ##########################################
            ### 2 กราฟย่อย รวมเงินจากภายนอก และรวมเงินจากภายใน
            ###########################################
                    
            df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
            df.reset_index(level=0, inplace=False)
            df = df.rename(columns={"Unnamed: 0" : "budget_year","0": "col0", "1": "col1", "2": "col2",
                        "3": "col3", "4": "col4", "5": "col5",
                        "6": "col6", "7": "col7", "8": "col8",
                        "9": "col9", "10": "col10", "11": "col11"}
                        , errors="raise")
            
            list_in=['col0','col1','col3','col4','col10']
            list_out=['col2','col5','col6','col7','col8','col9']

            result_sum = pd.DataFrame()
            for y in range(now_year-9,now_year):
                
                df2 = df[df["budget_year"]== int(y)]
                    
                result_in = df2[list_in].sum(axis=1)
                
                result_out = df2[list_out].sum(axis=1)
                
                result_in = result_in.iloc[0]
                
                result_out = result_out.iloc[0]

                
                re_df = {'year' : y, 
                        'sum1' : result_in, 
                         'sum2' : result_out,  
                        }
                result_sum = result_sum.append(re_df, ignore_index=True)
                
            print(result_sum)
            result_sum['year'] = result_sum['year'].astype()
            whichrows = 'row3'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e) 
        
    elif request.POST['row']=='Query4': #ตารางแหล่งทุนภายนอก exFund.html
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

            whichrows = 'row4'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query5': #ตาราง marker * และ ** ของแหล่งทุน
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

            whichrows = 'row5'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query6': # ISI SCOPUS Citation
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
        whichrows = 'row6'

    elif request.POST['row']=='Query7': # Head Page
        try:
            ### จำนวนของนักวิจัย
            sql_cmd =  """SELECT COUNT(*) as count
                    FROM importdb_prpm_v_grt_pj_team_eis;
                    """
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            final_df=pd.DataFrame({'total_of_guys':df['count'].astype(int) }, index=[0])

            ### รายได้งานวิจัย 
            
            df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""", index_col=0)
            # df = df.rename(columns={"Unnamed: 0" : "budget_year"}, errors="raise")
            
            df = df.loc[(df.index == int(datetime.now().year+543))]
                    
            final_df["total_of_budget"] = df.sum(axis=1)[int(datetime.now().year+543)]
            
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

            whichrows = 'row7'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
    
    elif request.POST['row']=='Query8': # web of science Research Areas   
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

        whichrows = 'row8'
    
    elif request.POST['row']=='Query9': # web of science catagories    
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

        whichrows = 'row9'

    elif request.POST['row']=='Query10': # Citation ISI and H-index  
        dt = datetime.now()
        year = dt.year
        cited, h_index = cited_isi()

        if(cited is None): 
                print("Get Citation ERROR 1 time, call cited_isi() again....")
                cited, h_index = cited_isi()
                if(cited is None): 
                    print("Get Citation ERROR 2 times, break....")
                else:
                    print("finished Get Citation")
        else:
            print("finished Get Citation")

        try:   
            
            # ใส่ ข้อมูลในฐานข้อมูล  sco isi tci ด้วย ปีปัจจุบัน
            obj, created = PRPM_ranking_cited_isi.objects.get_or_create(year = year+543, defaults ={ 'cited': cited['cited'][0]})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.cited =  cited['cited'][0]
                obj.save()

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

            whichrows = 'row10'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
        
    elif request.POST['row']=='Query11': # ISI SCOPUS and Citation of ISI to CSV  
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

            whichrows = 'row11'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)  
        
    elif request.POST['row']=='Query12': # Graph 1
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
            whichrows = 'row12'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
        
    elif request.POST['row']=='Query13': #graph 2
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

            whichrows = 'row13'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query14': #graph3
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
            whichrows = 'row14'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)
        
    elif request.POST['row']=='Query15': #graph4
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

            whichrows = 'row15'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)

    elif request.POST['row']=='Query16': # Filled area chart กราฟหน้าแรก รูปแรก
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

            whichrows = 'row16'

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
    def get_head_page(): # get 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    if request.method == "POST":
        filter_year =  request.POST["year"]   #รับ ปี จาก dropdown 
        print("post = ",request.POST )
        selected_year = int(filter_year)      # ตัวแปร selected_year เพื่อ ให้ใน dropdown หน้าต่อไป แสดงในปีที่เลือกไว้ก่อนหน้า(จาก year)
    
    
    def graph1():  # แสดงกราฟโดนัด ของจำนวน เงินทั้ง 11 หัวข้อ
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year"}, errors="raise")
        re_df =df[df["budget_year"]==int(selected_year)]
        newdf = pd.DataFrame({'BUDGET_TYPE' : ["สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)"
                                       ,"เงินงบประมาณแผ่นดิน"
                                       ,"เงินกองทุนวิจัยมหาวิทยาลัย"
                                       ,"เงินจากแหล่งทุนภายนอก ในประเทศไทย"
                                       ,"เงินจากแหล่งทุนภายนอก ต่างประเทศ"
                                       ,"เงินรายได้มหาวิทยาลัย"
                                       ,"เงินรายได้คณะ (เงินรายได้)"
                                       ,"เงินรายได้คณะ (กองทุนวิจัย)"
                                       ,"เงินกองทุนวิจัยวิทยาเขต"
                                       ,"เงินรายได้วิทยาเขต"
                                       ,"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง"
                                       ,"ไม่ระบุ"    
                            ]})
        
        newdf["budget"] = 0.0
        # for n in range(0,11):
        for n in range(0,12):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = re_df[str(n)]

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' ,color_discrete_sequence=px.colors.sequential.haline, hole=0.5 ,)
        fig.update_traces(textposition='inside', textfont_size=14)
        # fig.update_traces(hoverinfo="label+percent+name",
        #           marker=dict(line=dict(color='#000000', width=2)))

        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        fig.update_layout( height=600)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))

        fig.update_layout( annotations=[dict(text="<b> &#3647; {:,.2f}</b>".format(newdf.budget.sum()), x=0.50, y=0.5,  font_color = "black", showarrow=False)]) ##font_size=20,
        # fig.update_traces(hovertemplate='%{name} <br> %{value}') 
         
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div


    def get_budget_amount(): #แสดง จำนวนของเงิน 11 ประเภท ในตาราง
        
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year","0": "col0", "1": "col1", "2": "col2",
                    "3": "col3", "4": "col4", "5": "col5",
                    "6": "col6", "7": "col7", "8": "col8",
                    "9": "col9", "10": "col10", "11": "col11"}
                    , errors="raise")
        
        re_df = df[df["budget_year"]==int(selected_year)]
        # print(re_df)
        return re_df

    def get_budget_gov(): # แสดงเงินภายในประเทศ รัฐ 

        df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""")
        df['budget_year'] = df['budget_year'].astype('str')
        df = df.groupby(['fund_type_group','budget_year'])['final_budget'].sum()
        df = df.to_frame()
        
        try :
            temp_gov = """ fund_type_group == "1" and budget_year == '"""+str(selected_year)+"""'"""
            gov = df.query(temp_gov)['final_budget'][0]
        
        except Exception as e :
            gov = 0

        return gov

    def get_budget_comp(): # แสดงเงินภายในประเทศ เอกชน

        df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""")
        df['budget_year'] = df['budget_year'].astype('str')
        df = df.groupby(['fund_type_group','budget_year'])['final_budget'].sum()
        df = df.to_frame()
        try:
            temp_comp = """ fund_type_group == "2" and budget_year == '"""+str(selected_year)+"""'"""
            comp = df.query(temp_comp)['final_budget'][0]

        except Exception as e :
            comp = 0
        
        return comp

    def get_budget_campas():  # แสดงเงินวิทยาเขต
        df = pd.read_csv("""mydj1/static/csv/budget_of_fac.csv""")

        index_df = df["camp_name_thai"].unique()

        df = df[(df["budget_year"] == selected_year)]
        df = df[["camp_name_thai","fac_name_thai","sum_final_budget"]]
        df = df.groupby(["camp_name_thai"])['sum_final_budget'].sum()
        df = df.to_frame() 
        
        for i in index_df:
            try:
                print(df["sum_final_budget"][i])
            except Exception as e :
                df.loc[i] = [0]
        
        re_df = pd.DataFrame(
                            {'col0' : [df["sum_final_budget"]["วิทยาเขตหาดใหญ่"]], 
                            'col1' : [df["sum_final_budget"]["วิทยาเขตปัตตานี"]],
                            'col2' : [df["sum_final_budget"]["วิทยาเขตภูเก็ต"]],
                            'col3' : [df["sum_final_budget"]["วิทยาเขตสุราษฎร์ธานี"]],
                            'col4' : [df["sum_final_budget"]["วิทยาเขตตรัง"]],
                            })

        return re_df
    
    def get_sum_budget(): #แสดง จำนวนของเงินรวม ภายนอก ภายใน
        
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year","0": "col0", "1": "col1", "2": "col2",
                    "3": "col3", "4": "col4", "5": "col5",
                    "6": "col6", "7": "col7", "8": "col8",
                    "9": "col9", "10": "col10", "11": "col11"}
                    , errors="raise")
        
        df = df[df["budget_year"]==int(selected_year)]
        
        list_in=['col0','col1','col3','col4','col10']
        list_out=['col2','col5','col6','col7','col8','col9']

        result_in = df[list_in].sum(axis=1)
        result_out = df[list_out].sum(axis=1)

        result_in = result_in.iloc[0]
        result_out = result_out.iloc[0]
        
        re_df = pd.DataFrame(
                            {'in' : result_in, 
                            'out' : result_out,  
                            }, index=[0])
        
        return re_df

    def get_date_file():
        file_path = """mydj1/static/csv/12types_of_budget.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################
        'budget' : get_budget_amount(),
        'sum' : get_sum_budget(),
        'gov': get_budget_gov(),
        'comp': get_budget_comp(),
        'year' :range((datetime.now().year+1)+533,(datetime.now().year+1)+543),
        'filter_year': selected_year,
        'campus' : get_budget_campas(),
        'graph1' :graph1(),
        'date' : get_date_file(),
    
    }
    
    return render(request, 'importDB/revenues.html', context)

def revenues_graph_old(request, value):  # รับค่า value มาจาก url

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

def revenues_graph(request, value):  # รับค่า value มาจาก url

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def graph(source):
        df = pd.read_csv("""mydj1/static/csv/table_"""+source+""".csv""", index_col=0)
        
        dff2 = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""", index_col=0)
        now = datetime.now()
        now_year = now.year+543
        temp = 0 
        for i, index in enumerate(df.index):  # temp เพื่อเก็บ ว่า ปีปัจจุบัน อยุ่ใน row ที่เท่าไร
            if index == now_year:
                temp = i+1

        df2 = df[:temp-1]   # กราฟเส้นทึบ
        df3 = df[temp-2:temp]  # กราฟเส้นประ
        df4 = dff2['11'].to_frame()
        
        # กำหนดค่าเริ่มต้น ว่าจะต้องมี กี่ row, col และมี กราฟ scatter + table 
        fig = make_subplots(rows=1, cols=2,
                            column_widths=[0.7, 0.3],
                            specs=[[{"type": "scatter"},{"type": "table"}]]
                            )
        
        ### สร้าง กราฟเส้นสีเทา ####    
        # fig.add_trace(go.Scatter(x=df4.index, y=df4['11']
        #                                 ,line=dict( width=2 ,color='#D5DBDB') )
        #     )

        ### สร้าง กราฟเส้นทึบ ####
        
        fig.add_trace(go.Scatter(x=df2.index, y=df2[source],line=dict( color='royalblue')))
        
        ### สร้าง กราฟเส้นประ ####
        fig.add_trace(go.Scatter(x=df3.index, y=df3[source]
                ,line=dict( width=2, dash='dot',color='royalblue') )
            )
        
        labels = { "0":"สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)"
                    ,"1":"เงินงบประมาณแผ่นดิน"
                    ,"2":"เงินกองทุนวิจัยมหาวิทยาลัย"
                    ,"3":"แหล่งทุนภายนอก ในประเทศไทย"
                    ,"4":"แหล่งทุนภายนอก ต่างประเทศ"
                    ,"5":"เงินรายได้มหาวิทยาลัย"
                    ,"6":"เงินรายได้คณะ (เงินรายได้)"
                    ,"7":"เงินรายได้คณะ (กองทุนวิจัย)"
                    ,"8":"เงินกองทุนวิจัยวิทยาเขต"
                    ,"9":"เงินรายได้วิทยาเขต"
                    ,"10":"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง"
                    ,"11":"แหล่งทุนภาครัฐ"
                    ,"12":"แหล่งทุนภาคเอกชน"
                    ,"13":"-ไม่ระบุแหล่งงบประมาณ-"}
 
        fig.update_layout(showlegend=False)
        fig.update_layout(title_text=f"<b>รายได้งานวิจัยจาก {labels[source]} 10 ปี ย้อนหลัง </b>",
                        height=500,width=1000,
                        xaxis_title="ปี พ.ศ",
                        yaxis_title="จำนวนเงิน (บาท)",
                        font=dict(
                            size=14,
                        ))
        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear',
                # tick0 = 2554,
                dtick = 1
            )
        )

        ### ตาราง ####
        df[source] = df[source].apply(moneyformat)
        
        fig.add_trace(
            go.Table(
                columnwidth = [100,200],
                header=dict(values=["<b>Year</b>","<b>Budget\n<b>"],
                            fill = dict(color='#C2D4FF'),
                            align = ['center'] * 5),
                cells=dict(values=[df.index, df[source]],
                        fill = dict(color='#F5F8FF'),
                        align = ['center','right'] * 5))
                , row=1, col=2)
              
        fig.update_layout(autosize=True)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)

        
        return  plot_div

    source = value

    context={
        'plot1' : graph(source),
    }
        
    return render(request,'importDB/revenues_graph.html', context)

def revenues_table(request):  # รับค่า value มาจาก url
    
    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def get_table(year,source):
        
        if(source < 11 or source == 13):  # เฉพาะ หน่วยงาน ทุกหน่วยงาน (รวมอื่นๆ) ยกเว้น รัฐ และ เอกชน
            s = source
            if s == 13: # ถ้า source = 13 ให้เปลี่ยนเป็น 11 เพราะ หน่วยงาน-->อื่นๆ อยู่ใน budget_source_group_id = 11
                source = 11 
            df = pd.read_csv("""mydj1/static/csv/budget_of_fac.csv""")
            df = df[(df["budget_year"]==year) & (df["budget_source_group_id"]==source)]
            df[["camp_name_thai","fac_name_thai","sum_final_budget"]]
            df['sum_final_budget'] = df['sum_final_budget'].apply(moneyformat)
            df.reset_index(level=0, inplace=True)
            nonlocal check 
            check = True    # กำหนดให้เป็น True เพื่อที่จะรู้ว่า ไม่ใช้ รัฐ และ เอกชน  

            return df
        else :   # เฉพาะ หน่วยงาน รัฐ และ เอกชน
            source2 = 1 if source==11 else 2
            df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""")
            df = df[(df["budget_year"]==year) & (df["fund_type_group"]==source2)]
            df= df[['camp_name_thai', 'fac_name_thai','final_budget' ]]

            df = df.groupby(['camp_name_thai','fac_name_thai'] )['final_budget'].sum()
            df = df.to_frame() 

            return df
    
    labels = { "0":"สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)","1":"เงินงบประมาณแผ่นดิน","2":"เงินกองทุนวิจัยมหาวิทยาลัย"
                    ,"3":"เงินจากแหล่งทุนภายนอก ในประเทศไทย","4":"เงินจากแหล่งทุนภายนอก ต่างประเทศ","5":"เงินรายได้มหาวิทยาลัย",
                    "6":"เงินรายได้คณะ (เงินรายได้)","7":"เงินรายได้คณะ (กองทุนวิจัย)","8":"เงินกองทุนวิจัยวิทยาเขต",
                    "9":"เงินรายได้วิทยาเขต","10":"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง",
                    "11" : "เงินทุนภายนอกจากหน่วยงานภาครัฐ", "12" : "เงินทุนภายนอกจากหน่วยงานภาคเอกชน",
                    "13" : "อื่นๆ"}

    temp=[]
    for k, v in enumerate(request.POST.keys()):  # รับ key ของตัวแปร dictionary จาก ปุ่ม view มาใส่ในตัวแปร source เช่น source = Goverment
        if(k==1):
            temp = v.split("/")
    year = temp[0] # เก็บค่า ปี
    source = temp[1]  # เก็บหน่วยงาน 

    check = False  # เอาไว้เช็คว่า True = รายได้ 1-10  และ False = รายได้ 11-12 (รัฐ เอกชน)

    context={
        'a_table' : get_table(int(year),int(source)) ,    
        'year' : year,
        'source' : labels[source],
        'check': check
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

def pageRanking(request): # pange Ranking ISI/SCOPUS

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
        #         tick0 = 2554,
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

    def get_date_file():
        file_path = """mydj1/static/csv/isi_scopus.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)

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
        'date' : get_date_file(),
    }

    return render(request,'importDB/ranking.html', context)   

# %%
print("hello")

