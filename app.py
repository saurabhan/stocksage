import csv, os, io, re
from flask import Flask, render_template,escape, request, Response
import pandas as pd
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from flask.helpers import make_response
from werkzeug.debug import DebuggedApplication
import twint
import datetime
import pathlib

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

app = Flask(__name__,
        static_folder='static',
        template_folder='templates')


df = pd.read_csv("./static/data/tweets_refined_with_Score.csv")
Images = os.path.join('static', 'images')

stocks = {
        "Bank Nifty" : "BankNifty",
        "Apple":"AAPL",
        "Microsoft":"MSFT",
        "Tesla":"TSLA",
        "Google":"GOOG"
        }

bb_value = {
        "Bank Nifty" : 0,
        "Apple":1,
        "Microsoft":1,
        "Tesla":1,
        "Google":0
        }
sentiment = SentimentIntensityAnalyzer()

@app.route('/')
def index():
    symbol  = request.args.get('stock', False)
    stocks = {
        "Bank Nifty" : "BankNifty",
        "Apple":"AAPL",
        "Microsoft":"MSFT",
        "Tesla":"TSLA",
        "Google":"GOOG"
        }
    
    for key, value in stocks.items():
        print(key ,value)
    
    default_stock = 'banknifty'
    if symbol != default_stock:
        default_stock = symbol
        ploturl = f"./static/images/{default_stock}.png"
    else:
        ploturl = f"./static/images/{default_stock}.png"
        
    print(bb_value)
    return render_template('stock.html',stocks=stocks, url=ploturl, symbol=symbol, bbvalue=bb_value)

@app.route("/updateTweets")
def get_tweet():
    stocks = {
        "Bank Nifty" : "BankNifty",
        "Apple":"AAPL",
        "Microsoft":"MSFT",
        "Tesla":"TSLA",
        "Google":"GOOG"
        }
    
    for key, value in stocks.items():
        symbol  = value
        print(value)
        file = pathlib.Path(f"./static/data/{value}.csv")
        if file.exists ():
            print ("File exist")
        else:
            print ("File not exist")
            c = twint.Config()
            c.Search = f"{symbol}"
            c.Custom['tweet']=['date','time', 'tweet']
            today = datetime.date.today()
            dateUntil = today + datetime.timedelta(days=-2)
            print(dateUntil)
            c.Since = dateUntil.strftime("%Y-%m-%d")
            c.Until = today.strftime("%Y-%m-%d")
            c.Pandas = True    
            c.Store_csv = True
            c.Hide_output = True
            c.Output =f'./static/data/{symbol}.csv'
            twint.run.Search(c)
    
    return render_template('stock.html',stocks=stocks, symbol=symbol)

@app.route("/getsentiment")
def get_sentiment():
    
    for key, value in stocks.items():
        file = pathlib.Path(f"./static/data/{value}.csv")
        if file.exists ():
            print ("File exist")
            def remove_pattern(input_txt, pattern):
                r = re.findall(pattern, input_txt)
                for i in r:
                    input_txt = re.sub(i, '', input_txt)        
                return input_txt

            def clean_tweets(tweets):
                #remove twitter Return handles (RT @xxx:)
                tweets = np.vectorize(remove_pattern)(tweets, "RT @[\w]*:") 
                
                #remove twitter handles (@xxx)
                tweets = np.vectorize(remove_pattern)(tweets, "@[\w]*")
                
                #remove URL links (httpxxx)
                tweets = np.vectorize(remove_pattern)(tweets, "https?://[A-Za-z0-9./]*")
                
                #remove special characters, numbers, punctuations (except for #)
                tweets = np.core.defchararray.replace(tweets, "[^a-zA-Z]", " ")
                
                return tweets
            
            df = pd.read_csv(file)
            df['tweet'] = clean_tweets(df['tweet'])
            scores = []
            data = df
            compound_list = []
            positive_list = []
            negative_list = []
            neutral_list = []
            for i in range(data['tweet'].shape[0]):
                compound = sentiment.polarity_scores(data['tweet'][i])["compound"]
                pos = sentiment.polarity_scores(data['tweet'][i])["pos"]
                neu = sentiment.polarity_scores(data['tweet'][i])["neu"]
                neg = sentiment.polarity_scores(data['tweet'][i])["neg"]
                
                scores.append({"Compound": compound,
                                "Positive": pos,
                                "Negative": neg,
                                "Neutral": neu
                            })
                
            sentiments_score = pd.DataFrame.from_dict(scores)
            df = df.join(sentiments_score)
            df['dt']= pd.to_datetime(df['date'] + ' ' + df['time'])
            df = df.resample('D', on='dt').mean()
            df['dt'] = df.index
            df.dropna(inplace=True)
            df.to_csv(f'./static/data/{value}_score.csv')
            if df.iat[2,0] > df.iat[1,0]:
                print("Bullish")
                bb_value[key] = 1
            else:
                print('Bearish')
                bb_value[key] = 0
            
            print(bb_value)
        else:
            print("not exists")
    return render_template('stock.html',stocks=stocks, bbvalue=bb_value)
    

    

if __name__ == "__main__":
    app.run()

