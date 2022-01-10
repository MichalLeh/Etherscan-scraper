import re
import pandas as pd

import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from selenium import webdriver

# Get address 'to' for given transaction
def getToAddress(soup):
    toAddressList = soup.find_all("a", {"id":"contractCopy"})

    for address in toAddressList:
        return address.text

# Get address 'from' for given transaction
def getFromAddress(soup):
    fromAddressList = soup.find_all("a", {"id":"addressCopy"})

    for address in fromAddressList:
        return address.text

# Get transaction fee in dollars
def getTransactionDollarFee(soup):
    fees = soup.find_all("span", {"id":"ContentPlaceHolder1_spanTxFee"})

    for fee in fees:
        fee = str(fee.text)
        # replace characters (for excel purposes)
        dollarFee = fee.split(" ")[2].replace("($", "").replace(")", "").replace(".", ",")

        if not dollarFee:
            dollarFee = fee.split(" ")[3].replace("($", "").replace(")", "").replace(".", ",")

        return dollarFee

# Get transaction fee in Eth
def getTransactionEthFee(soup):
    fees = soup.find_all("span", {"id":"ContentPlaceHolder1_spanTxFee"})

    for fee in fees:
        fee = str(fee.text)
        # replace characters (for excel purposes)
        fee = fee.split(" ")[0].replace(".", ",")
        return fee

# Get Eth value for given transaction
def getEthValue(soup):
    values = soup.find_all("span", {"class":"u-label u-label--value u-label--secondary text-dark rounded mr-1"})

    for value in values:
        value = value.text
        # replace characters (for excel purposes)
        value = value.split(" ")[0].replace("Ether", "").replace(".", ",")
        return value

# Get Eth price for given transaction
def getEthPrice(soup):
    ethPrice = soup.find_all("span", {"id":"ContentPlaceHolder1_spanClosingPrice"})

    for price in ethPrice:
        price = price.text
        # replace characters (for excel purposes)
        price = price.split(" ")[0].replace("\n$", "").replace(",", "").replace(".", ",")
        return price

# Get detailed transaction's data for given tx hash
def getTxInfo(txList):
    # create pandas dataframe
    df = pd.DataFrame(columns = ['Eth price', 'Eth value', 'Eth fee', 'Dollar fee', 'Address from', 'Address to'])

    for i in range(len(txList)):
        url = Request('https://etherscan.io/tx/' + txList[i], headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # append data into dataframe
        df = df.append({'Eth price':getEthPrice(soup), 'Eth value':getEthValue(soup), 'Eth fee':getTransactionEthFee(soup),
                   'Dollar fee':getTransactionDollarFee(soup), 'Address from':getFromAddress(soup), 'Address to':getToAddress(soup)},
                       ignore_index=True)

    return df

# Get wallets tx hashes
def getTx(soup):
    spans = soup.find_all("span", {"class":"hash-tag text-truncate"})
    txList = []

    for span in spans:
        txs = span.find_all('a')

        for tx in txs:
            if '/tx/' in str(tx):
                tx = str(tx['href']).replace("/tx/", "")
                txList.append(tx)

    return txList

# Get date of given transaction
def getDate(soup):
    dates = soup.find_all("span", {"rel":"tooltip"})
    i = 1
    datesList = []

    # get only "date" values, not "ago" values
    for date in dates:
        if i % 2 != 0:
            datesList.append(date.text)
        i+=1

    return datesList

# Get method of given transaction
def getMethod(soup):
    methods = soup.find_all("span", {"style":"min-width:68px;"})
    methodList = []

    for method in methods:
        method = str(method.text)
        methodList.append(method)

    return methodList

# Get url
def getBasicData(ethWalletAdress, pagesTotal):
    df = pd.DataFrame(columns = ['tx', 'date', 'method'])

    # loop through etherscan transactions pages; range is based on number of pages
    for page in range(1, pagesTotal):
        url = Request('https://etherscan.io/txs?a=' + ethWalletAdress + '&p=' + str(page), headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(url)
        html = webpage.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        txSublist = getTx(soup)
        dateSublist = getDate(soup)
        methodSublist = getMethod(soup)

        # append data into dataframe
        for tx, date, method in zip(txSublist, dateSublist, methodSublist):
            df = df.append({'tx':tx, 'datum':date, 'metoda':method}, ignore_index=True)

    return df

# your eth wallet address
ethWalletAdress = "your eth wallet address"
#
pagesTotal = 5 + 1
#  get general etherscan transactions data
dfGeneral = getBasicData(ethWalletAdress, pagesTotal)
# get more detailed transaction data
dfTransaction = getTxInfo(list(dfGeneral['tx']))
# # concat them together
dfData = pd.concat([dfGeneral, dfTransaction], axis=1)
# convert dataframe into excel
dfData.to_excel("J:\output.xlsx")
