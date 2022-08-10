import requests
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import cchardet # speeds up BeautifulSoup
from time import sleep
from uuid import uuid4

URL_LIST = []
MAX_THREADS = 30


def name_parser(url):
    api = requests.get(url) # requesting an url
    soup = BeautifulSoup(api.text, 'lxml') # executing BeautifulSoup
    resList = soup.find_all("a",class_='address') # finding a tags with address class
    carName = []
    for res in resList:
        carName.append(res.get("title")) # adding results to a single list
    sleep(0.25)
    return carName


def price_parser(url):
    api = requests.get(url) # requesting an url
    soup = BeautifulSoup(api.text, 'lxml') # executing BeautifulSoup
    resList = soup.find_all("div", class_='price-ticket') # finding div tags with price-ticket class
    priceList = []
    for res in resList: 
        priceList.append(res.get("data-main-price")) # adding results to a single list
    sleep(0.25)
    return priceList



def price_fetcher():
    threads = min(MAX_THREADS, len(URL_LIST)) # finding minimum amount of threads needed for task
    carNameList = []
    priceList = []
    with ThreadPoolExecutor(max_workers=threads) as executor: # using for ThreadPoolExecutor for multithreading
        resName = executor.map(name_parser, URL_LIST)
        resPrice = executor.map(price_parser, URL_LIST)
        carNameList.extend(resName) 
        priceList.extend(resPrice)    
    carNameList = [i for sublist in carNameList for i in sublist] # unpacking nested lists of car names
    priceList = [i for sublist in priceList for i in sublist]# unpacking nested lists of prices
    excel_creator(carNameList,priceList)#,mileageList,transmissionList) # executing excel creator function to create an excel document


def excel_creator(carName,priceList):#, mileageList,transmissionList): 
    df = pd.DataFrame({'Car': carName,                    # Create a Pandas dataframe from data we received
                        'Price': priceList,
                                            })

    writer = pd.ExcelWriter('autoria.xlsx', engine='xlsxwriter') # Create Pandas Excel writer using xlsxwriter as our engine
    # Convert dataframe to an Xlsxwriter Excel object
    # Turn off defeault header and index to insert user defined header 
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False, index=False) 
    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    # Get the dimensions of the dataframe 
    (max_row, max_col) = df.shape
    # Create a list of column headers, to use in add_table
    column_settings = []
    for header in df.columns:
        column_settings.append({'header': header})

    worksheet.add_table(0,0, max_row, max_col - 1, {'columns': column_settings}) # Add the table
    worksheet.set_column(0, max_col - 1, 12) # Making columns wider
    #Close Pandas Excel writer and output Excel file.
    writer.save()
    print("Done!")




def url_extractor(max):
    for i in range(max):
        url = f'https://auto.ria.com/search/?indexName=auto,order_auto,newauto_search&categories.main.id=1&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page={i}&size=100'
        URL_LIST.append(url) # adding list of auto.ria urls
    price_fetcher()


def main():
    url_extractor(1) # executing url_extractor function



if __name__ == '__main__':
    main()