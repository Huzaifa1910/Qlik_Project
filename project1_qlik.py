import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
# from airflow.hooks.mysql_hook import MySqlHook
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.utils.dates import days_ago
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd


default_args = {
    'owner': 'Huzaifa',
    'start_date': days_ago(0),
    'email': ['huzaifaghori000@gmail.com'],
    'email_on_failure': False,
    'email._on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

#define the DAG

dag = DAG(
    dag_id='qlik_project_scraping_to_dumping',
    default_args=default_args,
    description='This is my project from scraping a website to dumping data in the database',
    schedule_interval=timedelta(days=1)
)

def greet():
     print("hello world")

def scrap_the_web(country_code, ti):
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)
    driver = webdriver.Chrome()
    driver.maximize_window()
    url = 'https://www.qlik.com/us/partners/find-a-partner'
    driver.get(url)
    time.sleep(5)
    select = Select(driver.find_element(By.ID, "zl_countryCode"))
    select.select_by_value(country_code)
    time.sleep(5)
    button = driver.find_element(By.ID, 'zl_show-more-btn')
    while True:
        time.sleep(2)
        button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "zl_show-more-btn")))
        div = driver.find_element(By.ID, "zl_show-more")
        if div.value_of_css_property("display") == "none":
            print("done Scrapping")
            break
    page_source = driver.page_source
    ti.xcom_push(key='page_source', value=page_source)
    driver.quit()

def print_data(ti):
    page_source = ti.xcom_pull(task_ids='scrapping', key='page_source')
    soup = BeautifulSoup(page_source, 'html.parser')
    elements = soup.find('div', class_="zl_partner-tiles")
    data = elements.find_all('div', class_="zl_partner-tile zl_partner-tile-hover")
    data_list = []
    for i in range(len(data)):
        partner_name = data[i].find('div', class_="zl_partner-name zl_partner-name-hover").text
        partner_address = data[i].find('div', class_="zl_partner-address").get_text(separator = " ").strip()
        partner_category = data[i].find('div',class_="zl_partner-tier").text
        try:
            partner_tier = data[i].find('span',class_="zl_value").text
            if(partner_tier == ""):
                partner_tier = "None"   
        except:
                pass
        data_dict = (partner_name,partner_category,partner_address,partner_tier)
        # data_dict['name'] = partner_name
        # data_dict['address'] = partner_address
        # data_dict['category'] = partner_category
        # data_dict['tier'] = partner_tier
        data_list.append(data_dict)
    print('Done data')
    print(data_list)    
    ti.xcom_push(key='data', value=data_list)
        # print(f'Name: {partner_name},\nAddress: {partner_address},\nTier: {partner_tier}\nCategory: {partner_category}')
    # df = pd.DataFrame(data_list)
    # df.to_csv('qlik.csv',sep='\t')


def sql_dumping(ti):
    # create a connection to the database
    mydb = mysql.connector.connect(
    host="192.168.220.75",
    user="myuser",
    password="mypassword",
    database="qlikproject"
    )

    # create a cursor object
    mycursor = mydb.cursor()

    # define the data to be inserted
    # data = [
    #     ('partnerN', 'addressN', 'categoryN', 'tierN'),
    #     ('partnerN', 'addressN', 'categoryN', 'tierN'),
    #     ('partnerN', 'addressN', 'categoryN', 'tierO'), ('partnerN', 'addressN', 'categoryN', 'tierN'),
    #     ('partnerN', 'addressN', 'categoryN', 'tierN'),
    #     ('partnerN', 'addressN', 'categoryN', 'tierO')
    # ]
    data = ti.xcom_pull(task_ids='Getting_data', key='data')



    # define the SQL query to insert data into the table
    sql = "INSERT INTO partners (name, address, category, tier) VALUES (%s, %s, %s, %s)"

    # execute the query to insert data into the table
    mycursor.executemany(sql, data)

    # commit the changes to the database
    mydb.commit()

    # print the number of rows that were inserted
    print(mycursor.rowcount, "rows were inserted into the partners table.")


task1 = PythonOperator(
    task_id = 'scrapping',
    # python_callable = greet,
    python_callable = scrap_the_web,
    op_kwargs={'country_code':'US'},
    dag = dag
)

task2 = PythonOperator(
    task_id = 'Getting_data',
    python_callable = print_data,
    # op_kwargs={'driver':driver},
    dag = dag
)

# task = MySqlOperator(
#     task_id='my_task',
#     mysql_conn_id='my_local_db',
#     sql='SELECT * FROM partners;',
#     dag=dag
# )
task3 = PythonOperator(
    task_id = 'dumping_data',
    python_callable = sql_dumping,
    dag = dag
)


task1 >> task2 >> task3