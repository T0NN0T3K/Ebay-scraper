# eBay scraping tool

## Setup

### Install dependencies 
```pip3 install -r requirements.txt```

### Telegram configuration
To receive telegram notifications:
1) Create a bot by writing to the BotFather on Telegram
2) BotFather will give you an API key: **save this API key for later**
3) Create a public channel and add the newly created bot as administrator
4) **Save the name of the channel** including the "@", for example: '@subito_bot'

### eBay configuration
1) Open an account on developer.ebay.com
2) Once account is active create a new Production keyset for scraping
3) **Save App ID for later**

To configure eBay search and Telegram, simply invoke the script with the proper parameters as following:

`python3 ebay-scraper.py --botToken [YOUR_API_TOKEN] --chatId [YOUR_CHANNEL_NAME] --apikey [YOUR_EBAY_APPID]`

## Usage
Write `python3 ebay-scraper.py --help` to see all the command line arguments. Keep in mind that the script *always* needs the argument --keyword in order to start the daemon. 

Here is a cheatsheet of the most common usages:

* Start a new default scraping session:
`python3 ebay-scraper.py --keyword "iPhone 13 128gb" --maxPrice 500 --minPrice 100`

* Modify the delay between a search and another
`python3 ebay-scraper.py --delay 120 --keyword "iPhone 13"`


