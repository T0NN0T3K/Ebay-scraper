from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import time


APP_ID = 'your_app_id_here'
DELAY = 60 # seconds

def search_items(keywords, max_price):
    try:
        api = Finding(appid=APP_ID, config_file=None)
        response = api.execute('findItemsAdvanced', {
            'keywords': keywords,
            'itemFilter': [
                {'name': 'MaxPrice', 'value': max_price},
                {'name': 'ListingType', 'value': 'FixedPrice'},
            ]
        })
        
        if hasattr(response.reply, 'ack'):
           print(f"Response status: {response.reply.ack}")
        
        if hasattr(response.reply, 'searchResult'):
            print(f"Results number: {response.reply.searchResult._count}")
            
            if hasattr(response.reply.searchResult, 'item'):
                return response.reply.searchResult.item
        
        print("No items found in the search.")
        return []
    
    except ConnectionError as e:
        print(f"Connection error: {e}")
        print(f"Error details: {e.response.dict()}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def notify(articolo):
    try:
        if isinstance(articolo, dict):
            titolo = articolo.get('title', ['Titolo non disponibile'])[0] if isinstance(articolo.get('title'), list) else articolo.get('title', 'Titolo non disponibile')
            prezzo = articolo.get('sellingStatus', {}).get('currentPrice', {}).get('value', 'Prezzo non disponibile')
            link = articolo.get('viewItemURL', 'Link non disponibile')
        else:
            titolo = getattr(articolo, 'title', ['Titolo non disponibile'])[0] if isinstance(getattr(articolo, 'title', None), list) else getattr(articolo, 'title', 'Titolo non disponibile')
            prezzo = getattr(getattr(articolo, 'sellingStatus', None), 'currentPrice', {}).get('value', 'Prezzo non disponibile')
            link = getattr(articolo, 'viewItemURL', 'Link non disponibile')
        
        print(f"New item: {titolo} - Price: {prezzo}")
        print(f"Link: {link}")
    except Exception as e:
        print(f"Error in the elaboration of item: {e}")

def main():
    while True:
        keywords = "iPhone 13"
        max_price = "500.00"

        articoli = search_items(keywords, max_price)
        if articoli:
            for articolo in articoli:
                notify(articolo)
        else:
            print("No new items to show.")
        print('------------------------------')
        time.sleep(DELAY)

if __name__ == "__main__":
    main()
