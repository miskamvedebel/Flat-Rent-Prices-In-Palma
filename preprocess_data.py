# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import time
import datetime

#Setting Path for files
path = 'C:\\Users\\maksim.lebedev\\Desktop\\idealista\\'
lst = os.listdir(path)
#Creating DataSet
df = pd.read_csv(path+str(lst[0]), sep = ';', encoding = "latin1")
lst.remove(lst[0])
for f in lst:
    df = pd.concat([df, pd.read_csv(path+f, sep = ';', encoding = "latin1")], ignore_index = True) 

df = df.drop(['Flat_Det'], axis = 1 )
#Counting Number of flats that are repeated more than once
df["Id"].value_counts()[df["Id"].value_counts()>1].count() #Having 4246 flats repeated

#Creating new features Date  - Date To
df_min = df.groupby(['Id'], as_index = False).min()
df_max = df[['Id', 'Timestamp']].groupby(['Id'], as_index = False).max()
flats = pd.merge(df_min, df_max, how = 'inner', on = 'Id', suffixes = ('_from', '_to'))
del(df_min, df_max, f, lst)

#Counting days flat stayed in website:
flats['TimeOnSite'] = 0
for i in range(0, len(flats['Timestamp_to'])):
    flats['TimeOnSite'][i] = datetime.datetime.strptime(flats['Timestamp_to'][i], '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(flats['Timestamp_from'][i], '%Y-%m-%d %H:%M:%S').date()
flats['DateFrom'] = [datetime.datetime.strptime(flats['Timestamp_from'][i], '%Y-%m-%d %H:%M:%S').date() for i in range(0, len(flats['Timestamp_from']))]
flats['DateTo'] = [datetime.datetime.strptime(flats['Timestamp_to'][i], '%Y-%m-%d %H:%M:%S').date() for i in range(0, len(flats['Timestamp_to']))]
flats.to_csv('C:\\Users\\maksim.lebedev\\Documents\\GitHub\\Flat-rent-Prices-In-Palma\\flats.csv', 
             sep = ';')
fname = 'C:\\Users\\maksim.lebedev\\Documents\\GitHub\\Flat-rent-Prices-In-Palma\\flats.csv'
flats = pd.read_csv( fname, sep = ';', encoding = 'latin1')
#Visalizing data:
import seaborn as sns
import matplotlib.pyplot as plt
flats[['Id','DateFrom']].groupby(['DateFrom'], as_index = False).count().mean()
flats['Bedrooms'] = flats.Bedrooms.str.extract('(\d)').astype(int)

#Excluding outliers:
X = flats[(flats['DateFrom']!=min(flats.DateFrom))&(flats['DateFrom']!=max(flats.DateFrom))]
X = X[['Id','DateFrom']].groupby(['DateFrom'], as_index = False).count()
fig = plt.figure(figsize=(20,15))
ax1 = fig.add_subplot(111)
sns.barplot(x = 'DateFrom', y = 'Id' ,data = X, ax = ax1)
plt.xticks(rotation = 45)
#Calculating moving average
ma = pd.rolling_mean(X, window = 5, min_periods = 1)

pr_max_3 = flats[flats['Bedrooms']<=3]
X_pr = pr_max_3.groupby(['DateFrom','Bedrooms'], as_index = False)['Price'].mean()
