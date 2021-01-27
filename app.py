from bs4 import BeautifulSoup
import requests, folium, decimal
import pandas as pd
from itertools import chain, islice
from flask import Flask, render_template, request
from flask_apscheduler import APScheduler
import mysql.connector
mydb = mysql.connector.connect(host="localhost", user="root", password="Gitsamdhr@16", database="inventory")
app = Flask(_name_)
scheduler=APScheduler()
data={}
my_cursor = mydb.cursor()
def web_scraping():
    sql = "DELETE from country"
    my_cursor.execute(sql)
    mydb.commit()
    source = requests.get("https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data#covid19-container").text
    soup = BeautifulSoup(source, 'lxml')
    gdp_table = soup.find('table', attrs={"class": "wikitable"})
    gdp_table_data = gdp_table.tbody.find_all("tr")
    headings = []

    for td in gdp_table_data[0].find_all("th"):
        headings.append(td.text.replace('\n', ' ').strip())

    for i in range(2, 230, 1):
        data_sm = {}
        for table, heading in zip(gdp_table_data[i].find("a"), headings):
            data_sm[heading] = table
        for table, heading in zip(gdp_table_data[i].find_all("td"), headings[1:2]):
            data_sm[heading] = table.text
        data[i] = data_sm

    for ele in data:
        sql = 'INSERT INTO country  (Location,Cases) VALUES (%s, %s)'
        val = (str(data[ele][headings[0]]), str(data[ele][headings[1]]))
        my_cursor.execute(sql,val)
        mydb.commit()


m=folium.Map(location=[40.837097000000000000000000000000,-72.886398600000000000000000000000],zoom_start=12)
tooltip="Click for location details"
my_cursor.execute("SELECT cast(Final_JOINED.Latitude as FLOAT),cast(Final_JOINED.Longitude as FLOAT) FROM Final_JOINED;")
result = my_cursor.fetchall()
df = pd.DataFrame(pd.read_csv('Database_inventory.csv'))
df=df.dropna(subset=['Longitude'])

df=df.dropna(subset=['Latitude'])
locate = {}

for i, j, k, l in zip(df['Latitude'], df['Longitude'], df['Location'], df['Cases']):
    temp = []
    temp.extend((i, j))
    locate['loc'] = temp
    substring = ","
    z = l.split(',')
    count = len(z)
    if count == 3:
        marker = folium.Marker(location=locate['loc'], popup=str(k), tooltip=str(l),
        icon=folium.Icon(color='red', icon_color='white')).add_to(m)
        marker.add_to(m)
    elif count == 2:
        marker = folium.Marker(location=locate['loc'], popup=str(k), tooltip=str(l),
        icon=folium.Icon(color='orange', icon_color='white')).add_to(m)
        marker.add_to(m)
    else:
        marker = folium.Marker(location=locate['loc'], popup=str(k), tooltip=str(l),
        icon=folium.Icon(color='blue', icon_color='white')).add_to(m)
        marker.add_to(m)
m.save('templates\map.html')
@app.route('/')
def home():
    return render_template('map.html')
if _name_ =='_main_':
    web_scraping()
    scheduler.add_job(id='Scheduled Task',func=web_scraping,trigger='interval',seconds=10)
    scheduler.start()
    app.run(port='5000')
