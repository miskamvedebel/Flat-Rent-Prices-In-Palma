import requests
from bs4 import BeautifulSoup
import numpy
from lxml import html
import pandas as pd
import urllib
import time
import datetime
import re

def get_tree(website):
    tree = html.fromstring(requests.get(website).content)
    return tree
def get_tag_class(tree, tag, class_name):
    string = "//{}[@class={}]/text()".format(tag, class_name)
    res = tree.xpath(string)
    return res
def link_builder(rent_or_buy):
    if rent_or_buy == 'rent':
        website = "https://www.idealista.com/en/alquiler-viviendas/palma-de-mallorca-balears-illes/"                
    elif rent_or_buy == 'buy':
        website = "https://www.idealista.com/en/venta-viviendas/palma-de-mallorca-balears-illes/"
    tree = get_tree(website)
    last_page = get_tag_class(tree, "a", '""')[-1]
    pages = []
    for i in range(1,int(last_page)+1):
        pages.append("{}pagina-{}.htm".format(website, i))
    return pages, last_page  
#Finding all pages from the website
all_pages, last_page = link_builder('rent')

lp = list()
links = list()
details = list()
columns = ['Flat', 'Price']
df = pd.DataFrame(data=numpy.zeros((0,len(columns))), columns=columns)
for t in all_pages:
    df_temp = pd.DataFrame(data=numpy.zeros((0,len(columns))), columns=columns)
    page_content_tree = get_tree(t)
    df_temp['Flat'] = get_tag_class(page_content_tree, "a", '"item-link "')
    df_temp['Price'] = get_tag_class(page_content_tree, "span", '"item-price"')
    df = pd.concat([df, df_temp], ignore_index = True)
    soup = BeautifulSoup(urllib.request.urlopen(t))
    all_items_links = soup.find_all("a", class_="item-link ")
    all_div_tag = soup.find_all("div", class_="item-info-container")
    for l in all_items_links:
        tp = l.get("href")
        full_link_to_flat = "https://www.idealista.com"+tp
        id_ = tp.split('/')[3]
        links.append(full_link_to_flat)
        lp.append(id_)
    for tag in all_div_tag:
        a_tag = tag.find("a", class_="item-link ")
        a_tag_href = a_tag.get("href")
        details.append(a_tag_href)
        span_tag = tag.find_all("span", class_="item-detail")
        for span in span_tag:
            span_txt = span.text
            details.append(span_txt)
df["Id"] = lp
df["Link"] = links
df["Timestamp"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

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

df["Street"] = ''
df["Type"] = ''
df["Area"] = ''
df["City"] = ''
for i in range(0, len(df["Flat"])):
    row = df["Flat"][i].split(',')
    df['Street'][i] = row[0].split(" in ")[1]
    df['Type'][i] = row[0].split(" in ")[0]
    l = len(row)
    if l == 2:
        df["City"][i] = row[1]
    elif l == 3:
        df["Area"][i] = row[1]
        df["City"][i] = row[2]
    elif l == 4:
        df["Area"][i] = row[2]
        df["City"][i] = row[3]
    elif l == 5:
        df["Area"][i] = row[3]
        df["City"][i] = row[4]
    else:
        df["City"][i] = row[1]

for p in range (0, len(df["Price"])):
    df["Price"][p] = int(df["Price"][p].replace(',', ''))
for t in range (0, len(df["Flat_Det"])):
    if df["Type"][t] == 'Studio apartment ' or df["Type"][t].find('m²') != -1:
        df["Floor and other details"][t] = df["Square"][t]
        df["Square"][t] = df["Bedrooms"][t]
        df["Bedrooms"][t] = '0 bed'
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H%M%S')
filenamelocation = "C:/Users/maksim.lebedev/Desktop/idealista/idealista-rent-"+st+".csv"
df.to_csv(filenamelocation, index=False, sep=";")
