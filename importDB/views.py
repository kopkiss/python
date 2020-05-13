from django.shortcuts import render
from django.http import HttpResponse
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
from .models import PRPM_v_grt_pj_team_eis
from .models import PRPM_v_grt_pj_budget_eis
from .models import Prpm_v_grt_project_eis
from .models import PRPM_ranking
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
# from elsapy.elsclient import ElsClient
# from elsapy.elsprofile import ElsAuthor, ElsAffil
# from elsapy.elsdoc import FullDoc, AbsDoc
# from elsapy.elssearch import ElsSearch
# from pybliometrics.scopus import ScopusSearch
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import pdb


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

def home(requests):  # หน้า homepage หน้าแรก

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def graph1():
        # sql_cmd =  """  SELECT * FROM querygraph1 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR))  """
        # con_string = getConstring('sql')
        # df = pm.execute_query(sql_cmd, con_string)
        df = pd.read_csv("""mydj1/static/csv/query_graph1.csv""")

        fig = make_subplots(rows=1, cols=2,
                            column_widths=[0.7, 0.3],
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
                            header=dict(values=["<b>Year</b>","<b>Budget<b>"],
                                        fill = dict(color='#C2D4FF'),
                                        align = ['center'] * 5),
                            cells=dict(values=[df.budget_year, df.budget],
                                    fill = dict(color='#F5F8FF'),
                                    align = ['left'] * 5))
                            , row=1, col=2)

        fig.update_layout(title_text='<b>งบประมาณวิจัยต่อปี</b>',
                        height=500,width=1000,
                        xaxis_title="ปี พ.ศ",
                        yaxis_title="จำนวนเงิน (บาท)")
        
    
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

    def graph3():
        # sql_cmd =  """SELECT * FROM querygraph3 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""
        # con_string = getConstring('sql')
        # df = pm.execute_query(sql_cmd, con_string) 
        df = pd.read_csv("""mydj1/static/csv/query_graph3.csv""")

        # df.to_csv ("""mydj1/static/csv/query_graph3.csv""", index = False, header=True)

        fig = px.line(df, x="budget_year", y="budget", color="camp_owner",
        line_shape="spline", render_mode="svg",  template='plotly_dark' )

        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph4():
        # sql_cmd =  """SELECT * FROM querygraph4 
        #                 where year BETWEEN YEAR(NOW())-10 AND YEAR(NOW())-1
        #          """
        #         #  where year BETWEEN YEAR(NOW())-10 AND YEAR(NOW())
        # con_string = getConstring('sql')
        # df = pm.execute_query(sql_cmd, con_string) 

        df = pd.read_csv("""mydj1/static/csv/query_graph4.csv""")

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

        return df.iloc[0]
    
    def budget_per_year():
        
        sql_cmd =  """SELECT FUND_BUDGET_YEAR as budget_year, sum(SUM_BUDGET_PLAN) as sum
                    FROM importdb_prpm_v_grt_project_eis
                    WHERE FUND_BUDGET_YEAR = YEAR(date_add(NOW(), INTERVAL 543 YEAR)) 
                    group by 1"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        return df.iloc[0]
    

    def getRanking(): #แสดง คะแนน scopus ISI TCI
        
        sql_cmd =  """select year, sco, isi, tci from importdb_prpm_ranking  where year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        # print(df)
        return df.iloc[0]

    def getNumOfNetworks(): # จำนวนเครือข่ายที่เข้าร่วม
        
        sql_cmd =  """SELECT count(*) as n from importdb_prpm_r_fund_type where flag_used = "1" """

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
  
        return df.iloc[0]

    context={
        'plot1' : graph1(),
        'plot2': graph2(),
        # 'plot3': graph3(),
        # 'plot4': graph4(),
        # 'plot5': graph5(),
        # 'plot6': graph6(),
        'counts': counts(),
        'budget_per_year': budget_per_year(),
        'ranking' : getRanking(),
        'numofnetworks' :getNumOfNetworks(),
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
    return render(request,'prpmdump.html',context)

def dQueryReports(request):
    return render(request,'dQueryReports.html')

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
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color')))
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

    elif request.POST['row']=='Query5':   
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
        
            # ใส่ ข้อมูลในฐานข้อมูล  sco isi tci ด้วย ปีปัจจุบัน
            obj, created = PRPM_ranking.objects.get_or_create(year = year+543, defaults ={ 'sco': sco_df['record_count'][0], 'isi': isi_df['record_count'][0], 'tci': 0})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.sco =  sco_df['record_count'][0]
                obj.isi =  isi_df['record_count'][0]
                obj.tci =  4 
                obj.save()

            # ใส่ ข้อมูล sco isi tci ในฐานข้อมูล ด้วย ปีปัจจุบัน - 1 
            obj, created = PRPM_ranking.objects.get_or_create(year = year+543-1, defaults ={ 'sco': sco_df['record_count'][1], 'isi': isi_df['record_count'][1], 'tci': 0})  # ถ้ามี year ในdb จะคืนค่าเป็น obj , ถ้าไม่มี year จะบันทึกข้อมูล year และ defaults ใน row ใหม่
            if(obj):   # เอาค่า obj ที่คืนมาเช็คว่ามีหรือไม่  ถ้ามี ให้อับเดท ค่า sco = scopus
                obj.sco =  sco_df['record_count'][1]
                obj.isi =  isi_df['record_count'][1]
                obj.tci =  7
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
                            ORDER BY 1 DESC),

                            temp2 as (SELECT FUND_BUDGET_YEAR, sum(SUM_BUDGET_PLAN) as B from importdb_prpm_v_grt_project_eis
                            join importdb_prpm_r_fund_type on importdb_prpm_v_grt_project_eis.FUND_TYPE_ID = importdb_prpm_r_fund_type.FUND_TYPE_ID
                            where importdb_prpm_v_grt_project_eis.FUND_SOURCE_ID = 05  and importdb_prpm_r_fund_type.FUND_TYPE_GROUP = 2
                            Group BY FUND_BUDGET_YEAR
                            ORDER BY 1 DESC),

                            temp3 as (SELECT FUND_BUDGET_YEAR, sum(SUM_BUDGET_PLAN) as nnull from importdb_prpm_v_grt_project_eis
                            join importdb_prpm_r_fund_type on importdb_prpm_v_grt_project_eis.FUND_TYPE_ID = importdb_prpm_r_fund_type.FUND_TYPE_ID
                            where importdb_prpm_v_grt_project_eis.FUND_SOURCE_ID = 05  and importdb_prpm_r_fund_type.FUND_TYPE_GROUP is null
                            Group BY FUND_BUDGET_YEAR
                            ORDER BY 1 DESC)


                            select temp1.fund_budget_year, (temp1.A+IFNULL(temp3.nnull, 0)) as GovernmentAgencies, IFNULL(temp2.B, 0) as PrivateCompany
                            from temp1 
                            left join temp2 on temp1.fund_budget_year = temp2.fund_budget_year
                            left join temp3 on temp1.fund_budget_year = temp3.fund_budget_year

                            ORDER BY 1 DESC
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
    
    elif request.POST['row']=='Query8':   #ตาราง marker ของแหล่งทุน 
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
                
    elif request.POST['row']=='Query12':   # Query 9 รูปกราฟ ที่จะแสดงใน ตารางของ tamplate revenues.html
        try:
            ### 7 กราฟ ในหัวข้อ 1 - 7
            FUND_SOURCES = ["Campus","Department","Goverment","International","Matching_fund","National","Revenue"]

            for FUND_SOURCE in FUND_SOURCES:
                sql_cmd = """select year, """+FUND_SOURCE+""" from revenues 
                        where year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
            
                con_string = getConstring('sql')
                df = pm.execute_query(sql_cmd, con_string) 

                fig = go.Figure(data=go.Scatter(x=df["year"], y=df[FUND_SOURCE]), layout= go.Layout( xaxis={
                                                'zeroline': False,
                                                'showgrid': False,
                                                'visible': False,},
                                        yaxis={
                                                'showgrid': False,
                                                'showline': False,
                                                'zeroline': False,
                                                'visible': False,
                                        }))

                # fig.add_trace(go.Scatter(x=month, y=high_2007, name='High 2007',
                #          line=dict(color='firebrick', width=4,
                #               dash='dash') # dash options include 'dash', 'dot', and 'dashdot'
                    # ))

                fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
                fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

                plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
                
                if not os.path.exists("mydj1/static/img"):
                    os.mkdir("mydj1/static/img")
                fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE+""".png""")
            
            ### 2 กราฟย่อย ใน หัวข้อ 5.1 และ 5.2
            FUND_SOURCES2 = ["GovernmentAgencies","PrivateCompany"]

            for FUND_SOURCE2 in FUND_SOURCES2:
                sql_cmd = """select fund_budget_year as year, """+FUND_SOURCE2+""" from revenues_national_g_p  
                    where fund_budget_year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
            
                con_string = getConstring('sql')
                df = pm.execute_query(sql_cmd, con_string) 

                fig = go.Figure(data=go.Scatter(x=df["year"], y=df[FUND_SOURCE2]), layout= go.Layout( xaxis={
                                                'zeroline': False,
                                                'showgrid': False,
                                                'visible': False,},
                                        yaxis={
                                                'showgrid': False,
                                                'showline': False,
                                                'zeroline': False,
                                                'visible': False,
                                        }))
                fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
                fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

                plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
                
                if not os.path.exists("mydj1/static/img"):
                    os.mkdir("mydj1/static/img")
                fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE2+""".png""")
    
            whichrows = 'row12'

        except Exception as e :
            checkpoint = False
            print('Something went wrong :', e)          

    if checkpoint is True:
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
    return render(request,'dQueryReports.html',context)

def pageRevenues(request): # page Revenues

    selected_year = datetime.now().year+543 # กำหนดให้ ปี ใน dropdown เป็นปีปัจจุบัน
    def counts():
        sql_cmd =  """SELECT COUNT(*) as c
                    FROM importdb_prpm_v_grt_pj_team_eis;
                    """
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 

        return df.iloc[0]
    
    def budget_per_year():
        
        sql_cmd =  """SELECT FUND_BUDGET_YEAR as budget_year, sum(SUM_BUDGET_PLAN) as sum
                    FROM importdb_prpm_v_grt_project_eis
                    WHERE FUND_BUDGET_YEAR = YEAR(date_add(NOW(), INTERVAL 543 YEAR)) 
                    group by 1"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        return df.iloc[0]
    

    def getRanking(): #แสดง คะแนน scopus ISI TCI
        
        sql_cmd =  """select year, sco, isi, tci from importdb_prpm_ranking  where year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        print(df)
        return df.iloc[0]
    
    def getNumOfNetworks(): # จำนวนเครือข่ายที่เข้าร่วม
        
        sql_cmd =  """SELECT count(*) as n from importdb_prpm_r_fund_type where flag_used = "1" """

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
  
        return df.iloc[0]

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
    
    def get_budget_goverment_privatecomp(): # แสดง จำนวนของ ตารางย่อยเงินทุนในประเทศ หน่วยงานภาครัฐ และ หน่วยงานเอกชน
        sql_cmd =  """select * from revenues_national_g_p where fund_budget_year = """+filter_year

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        # percen ของ Goverment Agencies (nper) และ ของ privatecomp (pper)
        df["nper"] = df["GovernmentAgencies"].apply(lambda x: x/ df[["GovernmentAgencies","PrivateCompany"]].sum(axis=1)*100).round(2)  
        df["pper"] = df["PrivateCompany"].apply(lambda x: x/df[["GovernmentAgencies","PrivateCompany"]].sum(axis=1)*100).round(2)

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
        print("*donut*******")
        print(df)
        newdf["budget"] = 0.0  # สร้าง column ใหม่
        for n in range(0,7):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = df[0][n] 

        df = newdf.copy()   # copy เพื่อ ใช้ในการรวมจำนวนเงินทั้งหมด แสดงในกราฟ ตรงกลางของ donut
        # print("*donut*******")
        # s = pd.to_numeric(newdf["budget"], errors='coerce')
        # print( type(s))
        newdf["budget"] = newdf["budget"].apply(lambda x: x/newdf["budget"].sum()*100)
        # newdf = newdf.round()

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' ,color_discrete_sequence=px.colors.sequential.haline, hole=0.4 )
        fig.update_traces(textposition='inside', textfont_size=16)
        fig.update_layout(uniformtext_minsize=12 )
        fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ ด้านข้างซ้าย
        # fig.update_layout( width=1000, height=485)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))
        fig.update_layout( annotations=[dict(text="{:,.2f}".format(df.budget.sum()), x=0.50, y=0.5, font_size=20, font_color = "blue", showarrow=False)])
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

        'counts': counts(),
        'budget_per_year': budget_per_year(),
        'ranking' : getRanking(),
        'numofnetworks' : getNumOfNetworks(),
        'budget' : get_budget_amount(),
        'percentage': get_percentage(),
        'width': get_width(),
        'year' :range((datetime.now().year)+543-10,(datetime.now().year+1)+543),
        'filter_year': selected_year,
        'graph1' :graph1(),
        'national' : get_budget_goverment_privatecomp(),
        'campus' : campus_budget(),
        


    }
    
    
    
    return render(request, 'revenues.html', context)

def pageExFund(request): # page รายได้จากทุนภายนอกมหาวิทยาลัย

    def counts():
        sql_cmd =  """SELECT COUNT(*) as c
                    FROM importdb_prpm_v_grt_pj_team_eis;
                    """
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 

        return df.iloc[0]
    
    def budget_per_year():
        
        sql_cmd =  """SELECT FUND_BUDGET_YEAR as budget_year, sum(SUM_BUDGET_PLAN) as sum
                    FROM importdb_prpm_v_grt_project_eis
                    WHERE FUND_BUDGET_YEAR = YEAR(date_add(NOW(), INTERVAL 543 YEAR)) 
                    group by 1"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        return df.iloc[0]
    

    def getRanking(): #แสดง คะแนน scopus ISI TCI
        
        sql_cmd =  """select year, sco, isi, tci from importdb_prpm_ranking  where year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))"""

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        print(df)
        return df.iloc[0]
    
    def getNumOfNetworks(): # จำนวนเครือข่ายที่เข้าร่วม
        
        sql_cmd =  """SELECT count(*) as n from importdb_prpm_r_fund_type where flag_used = "1" """

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
  
        return df.iloc[0]

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
            sql_cmd =  """select * from q_ex_fund
                            where fund_source_id = 05
                            order by 6 desc """
        else:
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
        ###  4 top bar
        'counts': counts(),
        'budget_per_year': budget_per_year(),
        'ranking' : getRanking(),
        'numofnetworks' : getNumOfNetworks(),
        #### tables1 
         'choices' : choices,
         'selected_i' : selected_i,
        'df_Na_Fx_fund' : getNationalEXFUND(),
        #### tables1 
        'df_Inter_Fx_fund':getInterNationalEXFUND(),
    }

    return render(request, 'exFund.html', context)

def pageTCI(request):
    return render(request,'TCI.html')