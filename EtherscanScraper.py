import re
import pandas as pd

import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urljoin

from etherscan import Etherscan
from datetime import datetime

# variables
ethWalletAdress = "your wallet address"
etherscanApiKey = "your api key"
# init etherscan API
etherscan = Etherscan(etherscanApiKey)

# Get methods of transactions
def getMethod(df):
    methodList = []
    # get dataframe's row count
    rowCount = len(df.index)
    # count the number of your etherscan wallet pages; 50 - default number of records shown
    pageCount = round(rowCount/50) + 1

    for page in range(1, pageCount):
        url = Request('https://etherscan.io/txs?a=' + ethWalletAdress + '&p=' + str(page), headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(url)
        html = webpage.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        methods = soup.find_all("span", {"style":"min-width:68px;"})

        for method in methods:
            method = str(method.text)
            methodList.append(method)

    #  add new column into dataframe and append reversed list to it
    df['Method'] = methodList[::-1]

    return df

# Get etherscan transaction data
def getTransactionData(ethWalletAdress, etherscanApiKey):
    # init etherscan
    etherscan = Etherscan(etherscanApiKey)
    # load api data into list
    allTransactionsList = etherscan.get_normal_txs_by_address(address=ethWalletAdress, startblock=0, endblock=99999999, sort="asc")
    #  declare pandas dataframe
    df = pd.DataFrame(columns = ['TX', 'Date', 'Address From', 'Address To', 'Eth Value', 'Eth Fee'])
    # loop through list
    for tx in allTransactionsList:
        # formula for eth value
        ethValue = int(tx['value'])/1000000000000000000
        # formula for transaction fee in eth
        ethFee = (int(tx['gasPrice']) * int(tx['gasUsed']))/1000000000*0.000000001
        # convert timestamp into date
        date = datetime.fromtimestamp(int(tx['timeStamp']))
        # append into dataframe
        df = df.append({'TX':tx['hash'], 'Date': date, 'Address From': tx['from'], 'Address To': tx['to'],
                       'Eth Value': ethValue, 'Eth Fee': ethFee }, ignore_index=True)

    df = getMethod(df)

    return df

df = getTransactionData(ethWalletAdress, etherscanApiKey)
# export dataframe into excel
df.to_excel("J:\output.xlsx")
