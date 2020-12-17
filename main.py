import requests
from twilio.rest import Client

# -------------------------------------CONSTANTS ---------------------------------------------------------
STOCK_NAME = "INTERESTED_STOCK_NAME"
COMPANY_NAME = "INTERESTED_COMPANY_NAME"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = "YOUR_STOCK_API_KEY"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

STOCK_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY
}

NEWS_PARAMS = {
    "q": f"{COMPANY_NAME}&",
    "apiKey": NEWS_API_KEY
}

# sms api credentials
ACCOUNT_SID = "YOUR_API_ID"
AUTH_TOKEN = "YOUR_API_TOKEN"
SENDER_PHONE_NUMBER = "SENDERS_PHONE_NUMBER"
RECIEVER_PHONE_NUMBER = "RECIEVER_PHONE_NUMBER"

STOCK_STATUS = ""

# ------------------------------------- fetch process---------------------------------------------

# fetch the company stock news (3 days)
news_response = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMS)
news_response.raise_for_status()
news_list = news_response.json()["articles"][:3]

# fetch stock value from alphavantage API
stock_response = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMS)
stock_response.raise_for_status()
stock_data = stock_response.json()

# slice yesterday and day-before-yesterday stock value from stock list
stock_close_list = [float(stock_value[1]["4. close"])
                    for stock_value in stock_data["Time Series (Daily)"].items()][1:3]
yesterday_stock_close_value = round(stock_close_list[0])
day_before_yesterday_stock_close_value = round(stock_close_list[1])

if yesterday_stock_close_value > day_before_yesterday_stock_close_value:
    STOCK_STATUS = "🔺"
else:
    STOCK_STATUS = "🔻"

# get the stock difference and stock difference percentage
stock_difference = abs(yesterday_stock_close_value - day_before_yesterday_stock_close_value)
stock_difference_percentage = round((stock_difference / yesterday_stock_close_value) * 100, 2)

# create a message list ton send message everyday
MESSAGE_LIST = []

for i in range(0, 3):
    msg_title = news_list[i]["title"]
    msg_description = news_list[i]["description"]
    MESSAGE_LIST.append(
        f"\n{COMPANY_NAME}: {STOCK_STATUS}{stock_difference_percentage}%\nHeadline:"
        f" {msg_title}\nBrief: {msg_description}")

# check if stock value differs from standard stock value %
STANDARD_STOCK_PERCENTAGE_DIFFERENCE = 5

if stock_difference_percentage > STANDARD_STOCK_PERCENTAGE_DIFFERENCE:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for MESSAGE in MESSAGE_LIST:
        message = client.messages \
            .create(
            body=MESSAGE,
            from_=SENDER_PHONE_NUMBER,
            to=RECIEVER_PHONE_NUMBER
        )
