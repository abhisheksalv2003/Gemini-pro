import telebot
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from ta import add_all_ta_features
import requests
from datetime import datetime, timedelta

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('7523225309:AAFJ5i1Af7uXLBPF_cNEjNl5osvRpfzotUs')

# Alpha Vantage API key (free tier)
ALPHA_VANTAGE_API_KEY = '4JWGHYRSVDQW2BL9'

def fetch_forex_data(symbol='EURUSD', interval='5min'):
    base_url = 'https://www.alphavantage.co/query'
    function = 'FX_INTRADAY'
    
    params = {
        'function': function,
        'from_symbol': symbol[:3],
        'to_symbol': symbol[3:],
        'interval': interval,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'compact'
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'Time Series FX (' + interval + ')' not in data:
        raise ValueError("Error fetching data from Alpha Vantage API")
    
    df = pd.DataFrame(data['Time Series FX (' + interval + ')'])
    df = df.T
    df.index = pd.to_datetime(df.index)
    df.columns = ['Open', 'High', 'Low', 'Close']
    df = df.astype(float)
    return df

# Add technical indicators
def add_indicators(data):
    return add_all_ta_features(
        data, 
        open="Open", high="High", low="Low", close="Close",
        volume="Volume",  # Note: Alpha Vantage doesn't provide volume for forex
        fillna=True
    )

# Train model
def train_model(data):
    X = data.drop(['Open', 'High', 'Low', 'Close'], axis=1)
    y = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return model

# Predict next move
def predict_next_move(model, latest_data):
    prediction = model.predict(latest_data)
    return "Buy" if prediction[0] == 1 else "Sell"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Forex Trading Bot! Use /predict to get the next move prediction.")

@bot.message_handler(commands=['predict'])
def predict_command(message):
    try:
        # Fetch real-time forex data
        data = fetch_forex_data()
        data_with_indicators = add_indicators(data)
        
        model = train_model(data_with_indicators)
        
        latest_data = data_with_indicators.iloc[-1].drop(['Open', 'High', 'Low', 'Close'])
        prediction = predict_next_move(model, latest_data.values.reshape(1, -1))
        
        bot.reply_to(message, f"The predicted next move for EUR/USD is: {prediction}")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Start the bot
bot.polling() a 
