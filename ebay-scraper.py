from ebaysdk.finding import Connection as Finding
import time, argparse, asyncio, json, os
from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.error import RetryAfter, TimedOut

parser = argparse.ArgumentParser()

parser.add_argument('--apikey',dest='app_id',help="your eBay App ID api key here")
parser.add_argument('--botToken',dest='BOT_TOKEN',help="your telegram bot token here")
parser.add_argument('--channelId',dest='channel_id',help="your telegram public channel id here")
parser.add_argument('--keywords',dest='keyword',help="select keywords to search in the title")
parser.add_argument('--delay', dest='delay', help="delay for the daemon (default 120)")
parser.set_defaults(delay=120)   #default refresh every 2 minutes
parser.add_argument('--minPrice',dest='minPrice')
parser.set_defaults(minPrice=0)
parser.add_argument('--maxPrice',dest='maxPrice')
parser.set_defaults(maxPrice=100000)
parser.add_argument('--globalId',dest='globalId',help="select the ebay global ID of your country (default Italy 'EBAY-IT'")
parser.set_defaults(globalId="EBAY-IT")

args = parser.parse_args()

apiCredentials = dict()
apiFile = "telegram_api_credentials"
request = HTTPXRequest(connect_timeout=10, read_timeout=10)

def search_items(appid, keywords, min_price, max_price, globalId):
    try:
        api = Finding(appid=appid, config_file=None, siteid=globalId)
        response = api.execute('findItemsAdvanced', {
            'keywords': keywords,
            'itemFilter': [
                {'name': 'MinPrice', 'value': min_price},
                {'name': 'MaxPrice', 'value': max_price},
            ] 
        })   
        if hasattr(response.reply.searchResult, 'item'):
            return response.reply.searchResult.item
        print("No items found in the search.")
        return []
    
    except Exception as e:
        print(f"Error: {e}")
        return []

def notify(articolo):
    
    title = articolo.get('title', ['Titolo non disponibile'])[0] if isinstance(articolo.get('title'), list) else articolo.get('title', 'Titolo non disponibile')
    price = articolo.get('sellingStatus').get('currentPrice').get('value')
    link = articolo.get('viewItemURL', 'Link non disponibile')
    type = articolo.get('listingInfo').get('listingType')
    currency = articolo.get('sellingStatus').get('currentPrice').get('_currencyId')
    print(f"New item: {title} - Price: {price}{currency} - Type: {type}")
    print(f"Link: {link}")

async def send_telegram_message(bot, articolo):

    link = articolo.get('viewItemURL')
    price = articolo.get('sellingStatus').get('currentPrice').get('value')
    currency = articolo.get('sellingStatus').get('currentPrice').get('_currencyId')
    type = articolo.get('listingInfo').get('listingType')
    try:
        await bot.send_message(chat_id=apiCredentials["chatid"], text=f"Type: {type}\tPrice: {price}{currency}\t{link}")
    except RetryAfter as e:
        sleep_time = e.retry_after
        print(f"TIMEOUT -> Waiting time: {sleep_time}")
        time.sleep(sleep_time)
        await bot.send_message(chat_id=apiCredentials["chatid"], text=f"Type: {type}\t{price}{currency}\t{link}")
    except TimedOut as t:
        return
    
def id_listing(list):
    id_list = []
    if list:
        for item in list:
            id = item.get('itemId')
            id_list.append(id)
    else:
        return None
    return id_list

def save_api_credentials():
    '''A function to save the telegram api credentials into the telegramApiFile'''
    with open(apiFile, 'w') as file:
        file.write(json.dumps(apiCredentials))

def load_api_credentials():
    '''A function to load the telegram api credentials from the json file'''
    global apiCredentials
    global apiFile
    if not os.path.isfile(apiFile):
        return
    with open(apiFile) as file:
        apiCredentials = json.load(file)

def load_bot():
    try:
        bot = Bot(token=apiCredentials["token"])
        return bot
    except:
        print('First insert your correct (remember using ") eBay APP_ID, telegram bot token and telegram Channel id, type -h for help.')
        return None

async def main():

    load_api_credentials()

    if args.BOT_TOKEN is not None and args.channel_id is not None and args.app_id is not None:
        apiCredentials["token"] = args.BOT_TOKEN
        apiCredentials["chatid"] = args.channel_id
        apiCredentials["appid"] = args.app_id
        save_api_credentials()
        print('API Credientals saved.')
        bot = load_bot()
        await bot.send_message(chat_id=args.channel_id, text=f"Connection established.")

    bot = load_bot()
        
    if args.keyword and bot is not None:
        appid = apiCredentials["appid"]
        keywords = str(args.keyword)
        min_price = int(args.minPrice)
        max_price = int(args.maxPrice)
        globalId = str(args.globalId)
        articles = search_items(appid, keywords, min_price, max_price, globalId)
        idList = id_listing(articles)
        if articles:
            for articolo in articles:
                notify(articolo)
                await send_telegram_message(bot, articolo)
                time.sleep(1)
        else:
            print("No items to show")
        print('------------------------------')
        time.sleep(int(args.delay))

        while True:
            query = search_items(appid, keywords, min_price, max_price, globalId)
            if query:
                for item in query:
                    if item.get('itemId') not in idList:
                        print(str(item.get('itemId')))
                        notify(item)
                        await send_telegram_message(bot, item)
                        time.sleep(1)
            else:
                print("No new items to show.")
            print('------------------------------')
            time.sleep(int(args.delay))

if __name__ == "__main__":
    asyncio.run(main())
    
    
