from asyncio import tasks
from json.tool import main
from urllib import response
import aiohttp
from async_timeout import asyncio
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
bitrue_list = []
binance_list = []

@app.route('/')
def home():
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    asyncio.run(gather_data_bitrue())
    asyncio.run(gather_data_binance())
    crypto_list = bitrue_list + binance_list
    return render_template('main.html', crypto_list = crypto_list)


@app.route('/bitrue')
def biture():
    return render_template('main.html', crypto_list = bitrue_list)


@app.route('/binance')
def binance():
    return render_template('main.html', crypto_list = binance_list)


async def parsing_bitrue_lockUp(headers, session):
    # BTR Lockups
    url = 'https://www.bitrue.com/arcade-web/increaseAct/lockCoinInvestList?appName=Netscape&appCodeName=Mozilla&appVersion=5.0+(Linux%3B+Android+6.0%3B+Nexus+5+Build%2FMRA58N)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F101.0.4951.67+Mobile+Safari%2F537.36&userAgent=Mozilla%2F5.0+(Linux%3B+Android+6.0%3B+Nexus+5+Build%2FMRA58N)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F101.0.4951.67+Mobile+Safari%2F537.36&cookieEnabled=true&platform=Win32&userLanguage=en&vendor=Google+Inc.&onLine=true&product=Gecko&productSub=20030107&mimeTypesLen=0&pluginsLen=0&javaEnbled=false&windowScreenWidth=1172&windowScreenHeight=850&windowColorDepth=24&bitrueLanguage=en_US&token='

    try:
        response_lockups = await session.get(url=url, headers=headers)
        response_lockups = await response_lockups.json()
    except:
        print('Ошибка чтения BTR Lockups с сайта!')
        return

    list_crypto = response_lockups['data']['fixRecords']
    for crypto in list_crypto:
        name_crypto = crypto["baseCoin"].upper()
        bitrue_list.append(
            {
                "baseCoin": name_crypto,
                "lockCoin": crypto["lockCoin"].upper(),
                "procent": crypto["rate"],
                "period": crypto["period"],
                "image": f"https://cdn.bitrue.com/icon/icon_{name_crypto}.png",
                "nameBroker": "Bitrue",
                "url": "https://www.bitrue.com/"
            }
        )
    print('Обработана страница BTR Lockups')


async def parsing_bitrue_piggy(headers, session):
    url = 'https://www.bitrue.com/arcade-web/increaseAct/campaignList?appName=Netscape&appCodeName=Mozilla&appVersion=5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/101.0.4951.67+Safari/537.36&userAgent=Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/101.0.4951.67+Safari/537.36&cookieEnabled=true&platform=Win32&userLanguage=en&vendor=Google+Inc.&onLine=true&product=Gecko&productSub=20030107&mimeTypesLen=2&pluginsLen=5&javaEnbled=false&windowScreenWidth=1920&windowScreenHeight=1080&windowColorDepth=24&bitrueLanguage=en_US&token=MDMwNjQ0MzUtZGYyYy00MGI5LWFkNjktYjc4Y2RlY2JhYzhmMTY1MzYzNTE3NDUyMA=='
    
    # piggy
    try:
        response_piggy = await session.get(url=url, headers=headers)
        response_piggy = await response_piggy.json()
    except:
        print('Ошибка чтения Power Piggy с сайта!')
        return
    
    list_crypto = response_piggy['data']['campaignList']
    for crypto in list_crypto:
        name_crypto = crypto["baseCoin"].upper()
        bitrue_list.append(
            {
                "baseCoin": name_crypto,
                "lockCoin": name_crypto,
                "procent": crypto['current']['rate'],
                "period": 'Any time',
                "image": f"https://cdn.bitrue.com/icon/icon_{name_crypto}.png",
                "nameBroker": "Bitrue",
                "url": "https://www.bitrue.com/"
            }
        )
    print('Обработана страница Powwer Piggy')


async def parsing_bitrue_farms(headers, session):
    url = 'https://www.bitrue.com/arcade-web/agencyInvest/new/queryFarmingList?match=0&pageNo=1&pageSize=100&appName=Netscape&appCodeName=Mozilla&appVersion=5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/101.0.4951.67+Safari/537.36&userAgent=Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Chrome/101.0.4951.67+Safari/537.36&cookieEnabled=true&platform=Win32&userLanguage=en&vendor=Google+Inc.&onLine=true&product=Gecko&productSub=20030107&mimeTypesLen=4&pluginsLen=3&javaEnbled=false&windowScreenWidth=1920&windowScreenHeight=1080&windowColorDepth=24&bitrueLanguage=en_US&token=MDMwNjQ0MzUtZGYyYy00MGI5LWFkNjktYjc4Y2RlY2JhYzhmMTY1MzYzNTE3NDUyMA=='

    # Farms
    try:
        response_farms = await session.get(url=url, headers=headers)
        response_farms = await response_farms.json()
    except:
        print('Ошибка чтения Farms с сайта!')
        return
    
    list_crypto = response_farms['data']['data']
    for crypto in list_crypto:
        name_crypto = crypto['lockCoins'][0]['coinName'].upper()
        bitrue_list.append(
            {
                "baseCoin": crypto['rewardCoins'][0]['coinName'],
                "lockCoin": crypto['lockCoins'][0]['coinName'],
                "procent": str(round(float(crypto['lockDays'][0]['rate']) * 100, 2)),
                "period": crypto['lockDays'][0]['lockday'],
                "image": f"https://cdn.bitrue.com/icon/icon_{name_crypto}.png",
                "nameBroker": "Bitrue",
                "url": "https://www.bitrue.com/"
            }
        )
    print('Обработана страница Farms')


async def parsing_binance(headers, search_type, session):

    url = f'https://www.binance.com/bapi/earn/v1/friendly/finance-earn/homepage/product/guaranteed?searchType={search_type}&pageSize=100&pageIndex=1&orderby=APY_DESC'
    try:
        # 'https://www.binance.com/bapi/earn/v1/friendly/finance-earn/homepage/product/guaranteed?searchType=BEGINNER&pageSize=100&pageIndex=1&orderby=APY_DESC'
        # 'https://www.binance.com/bapi/earn/v1/friendly/finance-earn/homepage/product/guaranteed?searchType=NEW_LISTING&pageSize=100&pageIndex=1&orderby=APY_DESC'
        # 'https://www.binance.com/bapi/earn/v1/friendly/finance-earn/homepage/product/guaranteed?searchType=BC_ZONE&pageSize=100&pageIndex=1&orderby=APY_DESC'
        # 'https://www.binance.com/bapi/earn/v1/friendly/finance-earn/homepage/product/guaranteed?searchType=POLKA_ZONE&pageSize=100&pageIndex=1&orderby=APY_DESC'
        # 'https://www.binance.com/bapi/earn/v1/friendly/finance-earn/homepage/product/guaranteed?searchType=SOL_ZONE&pageSize=100&pageIndex=1&orderby=APY_DESC'

        response_binance = await session.get(url=url, headers=headers)
        response_binance = await response_binance.json()
    except:
        print('Ошибка чтения данных с сайта Binance!')
        return

    list_crypto = response_binance['data']['list']
    for crypto in list_crypto:
        name_crypto = crypto["asset"]
        if  crypto["apy"] != None and ',' in crypto["apy"]:
            procent = str(round(float(crypto["apy"].split(',')[0]), 2) * 100)
        else:
            try:
                procent = str(round(float(crypto["apy"]), 2) * 100)
            except Exception as ex:
                print(f"[INFO] Error:", ex)
                continue
        binance_list.append({
            "baseCoin": name_crypto,
            "lockCoin": name_crypto,
            "procent":procent,
            "period": crypto["duration"],
            "image": f"https://cdn.bitrue.com/icon/icon_{name_crypto}.png",
            "nameBroker": "Binance",
            "url": "https://www.bitrue.com/"
            }
        )
    print(f'Completed parsind binance {search_type}')

async def gather_data_bitrue():
    headers = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Mobile Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(parsing_bitrue_piggy(headers, session)),
            asyncio.create_task(parsing_bitrue_farms(headers, session)),
            asyncio.create_task(parsing_bitrue_lockUp(headers, session))
        ]
        await asyncio.gather(*tasks)

async def gather_data_binance():
    headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Mobile Safari/537.36"
    }
    search_types = ['POPULAR', 'BEGINNER', 'NEW_LISTING', 'BC_ZONE', 'POLKA_ZONE', 'SOL_ZONE']
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(parsing_binance(headers, search_type, session)) for search_type in search_types
        ]
        await asyncio.gather(*tasks)

# def main():
#     # asyncio.run(gather_data_bitrue())
#     # asyncio.run(gather_data_binance())
#     print('Parsing completed!')


if __name__ == '__main__':
    app.run(debug = True)