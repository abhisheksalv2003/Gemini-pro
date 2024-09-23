import telebot
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import requests
from datetime import datetime, timedelta

# Telegram Bot Token
bot = telebot.TeleBot('6842258197:AAEcS--nOtRqLnFn4PDVKJsBO1AiAEh1E58')

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = 'OOG3865NPXVAVFEC'

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
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        
        if 'Error Message' in data:
            raise ValueError(f"API returned an error: {data['Error Message']}")
        
        if 'Time Series FX (' + interval + ')' not in data:
            raise ValueError(f"Expected data not found in API response. Response: {data}")
        
        df = pd.DataFrame(data['Time Series FX (' + interval + ')'])
        df = df.T
        df.index = pd.to_datetime(df.index)
        df.columns = ['Open', 'High', 'Low', 'Close']
        df = df.astype(float)
        return df
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error making request to Alpha Vantage: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Error processing Alpha Vantage data: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")

def add_indicators(data):
    # Calculate SMA
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['SMA_30'] = data['Close'].rolling(window=30).mean()
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Drop NaN values
    data.dropna(inplace=True)
    
    return data

def train_model(data):
    X = data.drop(['Open', 'High', 'Low', 'Close'], axis=1)
    y = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return model

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
        bot.reply_to(message, "Fetching real-time forex data...")
        data = fetch_forex_data()
        
        bot.reply_to(message, f"Adding technical indicators to {len(data)} data points...")
        data_with_indicators = add_indicators(data)
        
        bot.reply_to(message, "Training the model...")
        model = train_model(data_with_indicators)
        
        latest_data = data_with_indicators.iloc[-1].drop(['Open', 'High', 'Low', 'Close'])
        prediction = predict_next_move(model, latest_data.values.reshape(1, -1))
        
        bot.reply_to(message, f"The predicted next move for EUR/USD is: {prediction}")
    except ValueError as e:
        bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"An unexpected error occurred: {str(e)}")

# Start the bot
if __name__ == "__main__":
    print("Starting the Forex Trading Bot...")
    bot.polling()
