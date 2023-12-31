import telebot
from google.generativeai import genai

# Create a Telegram bot.
bot = telebot.TeleBot("6197603731:AAFjEJ2h3TLjoVqUihD2PwGL75LJVq5ypcM")

# Configure the Generative AI API.
genai.configure(api_key="AIzaSyB8iM86iiPfGSVS2bcpd0xZrmsdW-ZzTaw")

# Create a Generative AI model.
model = genai.GenerativeModel("gemini-pro")

# Create a chat session with the model.
chat = model.start_chat()

# Handle incoming messages.
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text

    # Send the user input to the chat session.
    response = chat.send_message(user_input)

    # Send the response from the chat session to the user.
    bot.send_message(message.chat.id, response.text)

# Start the Telegram bot.
bot.polling()
