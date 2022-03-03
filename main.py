import requests
from twilio.rest import Client
import os

account_sid = os.environ["ACCOUNT_SID"]
auth_token = os.environ["AUTH_TOKEN"]
twilio_phone_num = os.environ["TWILIO_PHONE"]
target_num = os.environ["TARGET_PHONE"]

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
stock_api = os.environ["STOCK_API"]

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": stock_api
}

response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
yday_closing_price = data_list[0]["4. close"]
day_before_yday_closing_price = data_list[1]["4. close"]

closing_price_difference = float(yday_closing_price) - float(day_before_yday_closing_price)
percent_difference = round(closing_price_difference / float(day_before_yday_closing_price) * 100)

up_down = None
if closing_price_difference >= 0:
    up_down = "🔺"
else:
    up_down = "🔻"

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
news_api_key = os.environ["NEWS_API"]

if abs(percent_difference) > 1:
    news_params = {
        "qInTitle": COMPANY_NAME,
        "sortBy": "publishedAt",
        "apiKey": news_api_key
    }

    news_api = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_api.raise_for_status()
    tesla_news = news_api.json()["articles"]

    articles = tesla_news[:3]
    print(articles)
    articles_list = [f"{STOCK_NAME}: {up_down}{percent_difference}%\n Headline: {article['title']}. \nBrief: {article['description']}." for article in articles]
    print(articles_list)

    client = Client(account_sid, auth_token)
    for article in articles_list:
        message = client.messages \
            .create(
            body=article,
            from_=twilio_phone_num,
            to=target_num
        )
