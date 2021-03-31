# StockSage

Stock market prediction is one of the main issues in the fintech industry and is of broad concern as many hedge funds rely on these Machine learning and data models to correctly predict the market sentiment so that they can book a defined amount of profit, in this we use sentiment analysis and machine learning models to predict twitter Sentiments and compare them to the market sentiments, and try to find a correlation if any present between the "Twitter Sentiments" and the "Market sentiments", for this we will be scrapping live tweets as well as historical tweets to analyze the mood of the tweets and compare it with the market price action data gathered either from Yahoo finance or Google finance, we will also try to predict the market price action based on the sentiment and will try to conclude if this can be an effective trading strategy in the market.

### We used 3 ML models to predict and compare the Stock Prices with the help of Twitter Sentiment
> LSTM
> XGBoost
> ARIMA

* We used TWINT library to Scrape the Twitter for collection of tweets and Yfinance for the stock data
