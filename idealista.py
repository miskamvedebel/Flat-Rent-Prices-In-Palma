import requests
from bs4 import BeautifulSoup
import numpy
from lxml import html
import pprint
import pandas as pd
import urllib
import time
import datetime
import re
import copy

to_rent_idealista = "alquiler-viviendas"
website = "https://www.idealista.com/en/"+to_rent_idealista+"/palma-de-mallorca-balears-illes/"
idealista_page = requests.get(website)
tree = html.fromstring(idealista_page.content)
items = tree.xpath('//a[@class="item-link "]/text()')
prices = tree.xpath('//span[@class="item-price"]/text()')
#print(list(zip(items, prices)))

pages = tree.xpath('//a[@class=""]/text()')
last_page_num = pages[-1]
link_mask = "pagina-"+last_page_num+".htm"
last_page_link = website + link_mask

#Finding all pages from the website
all_pages = []

for i in range(1,int(last_page_num)+1):
    website_mask = "https://www.idealista.com/en/alquiler-viviendas/palma-de-mallorca-balears-illes/pagina-"+str(i)+".htm"
    all_pages.append(website_mask)

#List of item - all pages

all_items = list()
all_items_flats = list()
all_items_prices = list()
lp = list()
links = list()
details = list()
p = 0

for t in all_pages:

    p=p+1 #Page counter
    page_content = requests.get(t)
    page_content_tree = html.fromstring(page_content.content)
    items_1 = page_content_tree.xpath('//a[@class="item-link "]/text()')
    prices_1 = page_content_tree.xpath('//span[@class="item-price"]/text()')
    all_items_flats.append(items_1)
    all_items_prices.append(prices_1)
    all_items.append(list(zip(items_1,prices_1)))

    #Getting items links and id
    idlst = urllib.request.urlopen(t)
    soup = BeautifulSoup(idlst)
    all_items_links = soup.find_all("a", class_="item-link ")
    for l in all_items_links:
        tp = l.get("href")
        full_link_to_flat = "https://www.idealista.com"+tp
        id_ = tp[13:21]
        links.append(full_link_to_flat)
        lp.append(id_)
    all_div_tag = soup.find_all("div", class_="item-info-container")
    for tag in all_div_tag:
        a_tag = tag.find("a", class_="item-link ")
        a_tag_href = a_tag.get("href")
        details.append(a_tag_href)
        span_tag = tag.find_all("span", class_="item-detail")
        for span in span_tag:
            span_txt = span.text
            details.append(span_txt)
#Creating empty data set
columns = ['Flat', 'Price', 'Id', 'Link']
df = pd.DataFrame(data=numpy.zeros((0,len(columns))), columns=columns)

for i in range(0,p):
    df_i = pd.DataFrame(all_items_flats[i], columns=["Flat"])
    df_i["Price"] = all_items_prices[i]
    df = df.append(df_i, ignore_index=True)
df["Id"] = lp
df["Link"] = links
df["Timestamp"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

tsmp = time.time()
st = datetime.datetime.fromtimestamp(tsmp).strftime('%Y-%m-%d %H%M%S')
filenamelocation = "C:/Users/maksim.lebedev/Desktop/idealista/idealista-rent-"+st+".csv"

regex = re.compile('/en/inmueble/*/')

numbers = [details.index(n) for n in details if re.match(regex, n)]

columns_details = ['Flat', 'Bedrooms', 'Square', 'Floor and other details']
df_det = pd.DataFrame(data=numpy.zeros((0,len(columns_details))), columns=columns_details)
len_n = len(numbers)
len_c = len(numbers)
flats = list()
bedrooms = list()
square = list()
other_details = list()
other_details_1 = list()
for d in range(0, len_n-1):
    s = numbers[d]
    if numbers[d+1]-numbers[d] == 4:
        flats.append(details[s])
        bedrooms.append(details[s+1])
        square.append(details[s+2])
        other_details.append(details[s+3])
    elif numbers[d+1]-numbers[d] == 5:
        flats.append(details[s])
        bedrooms.append(details[s + 1])
        square.append(details[s + 2])
        other_details.append(details[s + 3])
        other_details_1.append(details[s + 4])
    else:
        flats.append(details[s])
        bedrooms.append(details[s + 1])
        square.append(details[s + 2])
        other_details.append("Not Available")

#finding last element
diff = len(details)-numbers[-1]
s = numbers[-1]
if diff == 4:
    flats.append(details[s])
    bedrooms.append(details[s + 1])
    square.append(details[s + 2])
    other_details.append(details[s + 3])
elif diff == 5:
    flats.append(details[s])
    bedrooms.append(details[s + 1])
    square.append(details[s + 2])
    other_details.append(details[s + 3])
    other_details_1.append(details[s + 4])
else:
    flats.append(details[s])
    bedrooms.append(details[s + 1])
    square.append(details[s + 2])
    other_details.append("Not Available")

df["Flat_Det"] = flats
df["Bedrooms"] = bedrooms
df["Square"] = square
df["Floor and other details"] = other_details
street = list()
area = list()
number = list()
street1 = list()
city = list()
ftype = list()
for i in range(0, len(df["Flat"])):
    row = df["Flat"][i].split(',')
    if len(row) == 2:
        street.append(row[0])
        ftype.append(row[0].split("in")[0])
        city.append(row[1])
        street1.append("")
        number.append("")
        area.append("")
    elif len(row) == 3:
        street.append(row[0])
        ftype.append(row[0].split("in")[0])
        area.append(row[1])
        city.append(row[2])
        street1.append("")
        number.append("")
    elif len(row) == 4:
        street.append(row[0])
        ftype.append(row[0].split("in")[0])
        number.append(row[1])
        area.append(row[2])
        city.append(row[3])
        street1.append("")
    elif len(row) == 5:
        street.append(row[0])
        ftype.append(row[0].split("in")[0])
        street1.append(row[1])
        number.append(row[2])
        area.append(row[3])
        city.append(row[4])
    else:
        street.append(row[0])
        ftype.append(row[0].split("in")[0])
        city.append(row[1])
        street1.append("")
        number.append("")
        area.append("")
df["Street"] = street
df["Area"] = area
df["City"] = city
df["Type"] = ftype
for p in range (0, len(df["Price"])):
    df["Price"][p] = int(df["Price"][p].replace(',', ''))
for t in range (0, len(df["Flat_Det"])):
    if df["Type"][t] == 'Studio apartment ' or df["Type"][t].find('m²') != -1:
        df["Floor and other details"][t] = df["Square"][t]
        df["Square"][t] = df["Bedrooms"][t]
        df["Bedrooms"][t] = '0 bed'
df.to_csv(filenamelocation, index=False, sep=";")
df["Price"] = pd.to_numeric(df["Price"])
avg = df.groupby(["Area"])["Price"].mean()