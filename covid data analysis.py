#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

from bs4 import BeautifulSoup as soup
from datetime import date,datetime
from urllib.request import Request, urlopen


# In[2]:


import plotly.graph_objects as go
import plotly.express as px 
import plotly.offline as py
# import gc   # garbage collection
import warnings
warnings.filterwarnings("ignore")


# ### Web scrapping
# Web scraping is the process of using bots to extract content and data from a website.

# In[3]:


today = datetime.now()
yest_str = "%s %d %d" %(date.today().strftime("%b"),today.day-1, today.year)
yest_str


# In[4]:


# sending req to the website
url = "https://www.worldometers.info/coronavirus/#countries"
req = Request(url, headers={'user-agent': "Mozilla/5.0"})

webpage = urlopen(req)
print(webpage)  # we are getting obj here

# we are getting page data as in html form by using the beautifulsoup
page_soup = soup(webpage,"html.parser")
page_soup


# ### Cleaning data

# In[5]:


# getting the table of country wise data
table = page_soup.find_all("table",{'id':"main_table_countries_yesterday"})

# we are getting data table row 
containers = table[0].find_all('tr',{'style':''})
title = containers[0]

del containers[0]

all_data = []
clean = True

for country in containers:
    country_data = []
    country_container = country.find_all("td")
    
    if country_container[1].text == 'China':
        continue
    for i in range(1,len(country_container)):
        final_feature = country_container[i].text
        if clean:
            if i != 1 and i != len(country_container)-1:
                final_feature = final_feature.replace(",","")
            
                if final_feature.find('+') != -1:
                    final_feature = final_feature.replace("+","")
                    final_feature = float(final_feature)
                elif final_feature.find('-') != -1:
                    final_feature = final_feature.replace("-","")
                    final_feature = float(final_feature) * -1
        
        # for the missing data
        if final_feature == 'N/A':
            final_feature = 0
        elif final_feature == "" or final_feature == " ":
            final_feature = -1
            
        country_data.append(final_feature)
     
    all_data.append(country_data)


# In[6]:


all_data


# In[7]:


df = pd.DataFrame(all_data)
df.drop([15,16,17,18,19,20] , inplace= True, axis = 1)  # we are deleting columns(axis = 1 means column)
df


# In[8]:


columns_labels = ["Country","Total Cases","New Cases","Total Deaths","New Deaths","Total Recovered","New Recovered","Active Cases",
          "Serious/Critical","Total Cases/1M","Deaths/1M","Total Tests","Test/1M","Population","Continent"
         ]

# givind a name to the columns
df.columns = columns_labels
df.head()


# In[9]:


# typecasting str to numeric form:
for label in df.columns:
    if label != 'Country' and label != 'Continent':
        df[label] = pd.to_numeric(df[label])
        print(df[label])


# In[10]:


# adding these three columns
df['%Inc Cases'] = df["New Cases"]/df['Total Cases'] * 100
df['%Inc Deaths'] = df["New Deaths"]/df['Total Deaths'] * 100
df['%Inc Recovered'] = df["New Recovered"]/df['Total Recovered'] * 100


# In[11]:


df.head()


# In[12]:


#getting these above three value at location 0
# List of labels. Note using [[]] returns a DataFrame.

cases = df[["Total Recovered","Active Cases","Total Deaths"]].loc[0]
cases_df = pd.DataFrame(cases).reset_index()

# cases_df


# In[13]:


# we will calculate incresed percentage value
cases_df.columns = ["Type","Total"]

cases_df["Percentage"] = np.round(100*cases_df["Total"]/np.sum(cases_df["Total"]),2)
cases_df["Virus"] = ["COVID-19" for i in range(len(cases_df))]

fig = px.bar(cases_df, x = "Virus", y = "Percentage", color="Type", hover_data=["Total"])
fig.show()


# In[14]:


# for the new cases

cases = df[["New Recovered","New Cases","New Deaths"]].loc[0]
cases_df = pd.DataFrame(cases).reset_index()

cases_df.columns = ["Type","Total"]

cases_df["Percentage"] = np.round(100*cases_df["Total"]/np.sum(cases_df["Total"]),2)
cases_df["Virus"] = ["COVID-19" for i in range(len(cases_df))]

fig = px.bar(cases_df, x = "Virus", y = "Percentage", color="Type", hover_data=["Total"])
fig.show()


# In[15]:


per = np.round(df[['%Inc Cases','%Inc Deaths','%Inc Recovered']].loc[0],2)
# per

per_df = pd.DataFrame(per)
# per_df

per_df.columns = ["Percentage"]   # give name to the columns

fig = go.Figure()

fig.add_trace(go.Bar(x = per_df.index, y = per_df['Percentage'], marker_color = ["red","Green","Blue"]))
fig.show()


# ### data with respect to Continent

# In[16]:


continent_df = df.groupby("Continent").sum().drop("All")  # drop the continent column
continent_df = continent_df.reset_index()
continent_df


# In[17]:


def continent_visulization(v_list):
    for label in v_list:
        c_df = continent_df[['Continent',label]]
        c_df['Percentage'] = np.round(100 * c_df[label]/np.sum(c_df[label]), 2)
        c_df['Virus'] = ['COVID-19' for i in range(len(c_df))]
        
        fig = px.bar(c_df, x = 'Virus', y = 'Percentage', color="Continent", hover_data=[label])
        fig.update_layout(title = {"text":label})   # giving a name to the each parameter
        fig.show()


# In[18]:


cases_list = ["Total Cases","Active Cases","New Cases","Serious/Critical","Total Cases/1M"]

death_list = ["Total Deaths","New Deaths","Deaths/1M"]

recovered_list = ["Total Recovered","New Recovered","%Inc Recovered"]


# In[19]:


continent_visulization(cases_list)
# continent_visulization(death_list)
# continent_visulization(recovered_list)


# ## Countries
# top 5 countries data

# In[20]:


df = df.drop([len(df)-1])
country_df = df.drop([0])

country_df


# In[21]:


LOOK_AT = 5 # by changing this value we can see data of more countries
country = country_df.columns[1:14]

fig = go.Figure()
c = 0
for i in country_df.index:
    if c < LOOK_AT:
        fig.add_trace(go.Bar(name = country_df['Country'][i], x = country, y = country_df.loc[i][1:14]))
    else:
        break
    c += 1
    
fig.update_layout(title = {"text":f'Top {LOOK_AT} Countries Affected'}, yaxis_type = 'log') 
fig.show()


# In[ ]:




