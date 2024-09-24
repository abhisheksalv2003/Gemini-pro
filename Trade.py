import telebot
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

# Telegram Bot Token
bot = telebot.TeleBot('6842258197:AAEcS--nOtRqLnFn4PDVKJsBO1AiAEh1E58')

# MT5 खाता जानकारी
MT5_ACCOUNT = 181675175
MT5_PASSWORD = " @Arjun123"
MT5_SERVER = "Exness-MT5Trial6"

def initialize_mt5():
    if not mt5.initialize(login=MT5_ACCOUNT, password=MT5_PASSWORD, server=MT5_SERVER):
        print("MT5 initialization failed")
        mt5.shutdown()
        return False
    return True

def fetch_forex_data(symbol='EURUSD', timeframe=mt5.TIMEFRAME_M5, num_candles=1000):
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select {symbol}")
        return None
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def add_indicators(data):
    # Calculate SMA
    data['SMA_10'] = data['close'].rolling(window=10).mean()
    data['SMA_30'] = data['close'].rolling(window=30).mean()
    
    # Calculate RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    exp1 = data['close'].ewm(span=12, adjust=False).mean()
    exp2 = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Drop NaN values
    data.dropna(inplace=True)
    
    return data

def train_model(data):
    X = data[['SMA_10', 'SMA_30', 'RSI', 'MACD', 'Signal_Line']]
    y = np.where(data['close'].shift(-1) > data['close'], 1, 0)
    
    X_train, X_test, y_train, y_test = train_test_split(X[:-1], y[:-1], test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return model

def predict_next_move(model, latest_data):
    prediction = model.predict(latest_data)
    return "खरीदें" if prediction[0] == 1 else "बेचें"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "फॉरेक्स ट्रेडिंग बॉट में आपका स्वागत है! अगली चाल की भविष्यवाणी प्राप्त करने के लिए /predict का उपयोग करें।")

@bot.message_handler(commands=['predict'])
def predict_command(message):
    try:
        if not initialize_mt5():
            bot.reply_to(message, "MT5 को शुरू करने में विफल। कृपया अपने खाते की जानकारी की जांच करें।")
            return

        bot.reply_to(message, "वास्तविक समय के फॉरेक्स डेटा प्राप्त कर रहा हूं...")
        data = fetch_forex_data()
        
        if data is None:
            bot.reply_to(message, "डेटा प्राप्त करने में विफल। कृपया बाद में पुनः प्रयास करें।")
            return
        
        bot.reply_to(message, f"{len(data)} डेटा बिंदुओं में तकनीकी संकेतक जोड़ रहा हूं...")
        data_with_indicators = add_indicators(data)
        
        bot.reply_to(message, "मॉडल को प्रशिक्षित कर रहा हूं...")
        model = train_model(data_with_indicators)
        
        latest_data = data_with_indicators.iloc[-1][['SMA_10', 'SMA_30', 'RSI', 'MACD', 'Signal_Line']]
        prediction = predict_next_move(model, latest_data.values.reshape(1, -1))
        
        bot.reply_to(message, f"EUR/USD के लिए अगली चाल की भविष्यवाणी है: {prediction}")
    except Exception as e:
        bot.reply_to(message, f"एक अप्रत्याशित त्रुटि हुई: {str(e)}")
    finally:
        mt5.shutdown()

# बॉट शुरू करें
if __name__ == "__main__":
    print("फॉरेक्स ट्रेडिंग बॉट शुरू हो रहा है...")
    bot.polling()
    
