import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
import speech_recognition as sr
import pyttsx3
import subprocess
import urllib.parse
import requests
import geocoder
import time
import platform
import os
import webbrowser
import myMusic

# Initialize the recognizer and the text-to-speech engine
r = sr.Recognizer()  # Speech recognition engine
engine = pyttsx3.init()  # Text-to-speech engine

# API keys
weather_api_key = "470d35de76964208c7f1334b41076ad5"
currency_api_key = '8e1e6af5ee2d1414b58d0f9c'
BASE_URL = f'https://v6.exchangerate-api.com/v6/{currency_api_key}/latest/'

# Function to convert currency using ExchangeRate-API
def convert_currency(amount, from_currency, to_currency):
    try:
        url = f"{BASE_URL}/{from_currency}"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data["result"] == "success":
            exchange_rate = data["conversion_rates"][to_currency]
            converted_amount = amount * exchange_rate
            return converted_amount, exchange_rate
        else:
            return None, None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None, None
    except KeyError as e:
        print(f"Key Error: {e}")
        return None, None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None, None

# Function to speak a given text using pyttsx3
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to add a message to the conversation display
def add_chat(message, sender="luna", speak_response=True):
    conversation_text.config(state=tk.NORMAL)
    conversation_text.insert(tk.END, f"{sender}: {message}\n", sender.lower())
    conversation_text.config(state=tk.DISABLED)
    conversation_text.see(tk.END)
    if speak_response and sender == "luna":
        speak(message)

# Function to process and execute commands based on user input
def process_command(c):
    c = c.lower()
    add_chat(c, sender="User", speak_response=False)
    if "open google" in c:
        add_chat("Opening Google")
        threading.Thread(target=open_browser, args=("https://www.google.com",)).start()
    elif "open youtube" in c:
        add_chat("Opening YouTube")
        threading.Thread(target=open_browser, args=("https://www.youtube.com",)).start()
    elif "open spotify" in c:
        add_chat("Opening Spotify")
        threading.Thread(target=open_browser, args=("https://www.spotify.com",)).start()
    elif c.startswith("play on spotify"):
        song = c.split("play on spotify ", 1)[1]
        if song in myMusic.music:
            speak(f"Playing {song} on Spotify")
            webbrowser.open(myMusic.music[song])
        else:
            song_encoded = urllib.parse.quote(song)
            add_chat(f"Playing {song} on Spotify")
            threading.Thread(target=open_browser, args=(f"https://open.spotify.com/search/{song_encoded}",)).start()
    elif "search google for" in c:
        query = c.split("search google for ", 1)[1]
        add_chat(f"Searching Google for {query}")
        threading.Thread(target=open_browser, args=(f"https://www.google.com/search?q={urllib.parse.quote(query)}",)).start()
    elif "search youtube for" in c:
        query = c.split("search youtube for ", 1)[1]
        add_chat(f"Searching YouTube for {query}")
        threading.Thread(target=open_browser, args=(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}",)).start()
    elif "open whatsapp" in c:
        if platform.system() == "Windows":
            add_chat("Opening WhatsApp")
            threading.Thread(target=open_browser, args=("https://web.whatsapp.com",)).start()
    elif "weather" in c:
        try:
            location = detect_location()
            if location:
                lat, lon = location.latlng
                weather_data = get_weather(lat, lon)
                if weather_data and "weather" in weather_data and "main" in weather_data:
                    weather_description = weather_data["weather"][0]["description"]
                    temp_celsius = weather_data["main"]["temp"]
                    add_chat(f"The weather in {location.city} is {weather_description}.")
                    add_chat(f"The temperature is {temp_celsius:.2f} degrees Celsius.")
                    add_chat("Have a great day!")
                else:
                    add_chat(f"Sorry, I couldn't fetch the weather information for {location.city}.")
            else:
                add_chat("Sorry, I couldn't detect your location.")
        except Exception as e:
            add_chat(f"Sorry, there was an error fetching weather information: {str(e)}")
    elif "convert" in c:
        parts = c.split("convert", 1)[1].strip().split(" ")
        amount = float(parts[0])
        from_currency = parts[1].upper()
        to_currency = parts[3].upper()
        converted_amount, exchange_rate = convert_currency(amount, from_currency, to_currency)
        if converted_amount is not None:
            add_chat(f"{amount} {from_currency} is {converted_amount:.2f} {to_currency}")
        else:
            add_chat(f"Failed to convert {amount} {from_currency} to {to_currency}. Please try again later.")
    elif "thank you" in c:
        add_chat("It's my pleasure!")
    elif "what is your name" in c:
        add_chat("I am luna, your personal assistant.")
    elif "who made you" in c:
        add_chat("I was created by Nitin Sharma. He's an amazing developer!")
    elif "how are you" in c:
        add_chat("I am doing great, thank you for asking.")
    elif "what can you do" in c:
        add_chat("I can open popular websites like Google, YouTube, Spotify, etcetera. I can search Google and YouTube for you. I can also tell you the weather and play music on Spotify. Just give me a command and I'll do my best to help you.")
    elif "exit" in c:
        add_chat("Exiting now, Goodbye!")
        root.quit()
    elif "tell me a joke" in c:
        add_chat("Why don't scientists trust atoms? Because they make up everything!")
    elif "what time is it" in c:
        current_time = time.strftime("%H:%M")
        add_chat(f"The current time is {current_time}.")
    elif "tell me about yourself" in c:
        add_chat("I am luna, your virtual assistant created to help you with various tasks.")
    elif "set a reminder" in c:
        add_chat("I'm sorry, I can't set reminders at the moment.")
    elif "sing a song" in c:
        add_chat("I'm not much of a singer, but how about I play some music for you instead?")
    elif "translate" in c:
        add_chat("I'm sorry, I currently don't have the ability to translate languages.")
    elif "tell me a fun fact" in c:
        add_chat("Did you know that honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!")
    elif "tell me a riddle" in c:
        add_chat("I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I? Answer: An echo.")
    else:
        add_chat("Sorry, I can't process that command. Please try again.")


# Function to open a web browser asynchronously
def open_browser(url):
    subprocess.Popen(["python", "-m", "webbrowser", "-t", url])

# Function to play a beep sound indicating the assistant is listening
def play_beep():
    if platform.system() == 'Windows':
        import winsound
        winsound.Beep(1000, 200)
    elif platform.system() == 'Darwin':
        os.system('afplay /System/Library/Sounds/Ping.aiff')

# Function to update UI when starting listening
def update_ui_listening():
    start_button.config(state=tk.DISABLED)

# Function to update UI when stopping listening
def update_ui_stopped_listening():
    start_button.config(state=tk.NORMAL)

# Function to start listening for voice commands
def start_listening():
    def listen_continuously():
        update_ui_listening()
        speak("Hello! I am luna, your personal assistant. How can I help you?")
        while True:
            try:
                play_beep()
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source, phrase_time_limit=3)  # Adjusted phrase_time_limit
                command = r.recognize_google(audio)
                process_command(command)
                time.sleep(0.5)
            except sr.UnknownValueError:
                add_chat("Sorry, I did not understand that. Say Exit or press quit to stop.")
            except sr.RequestError as e:
                add_chat(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                add_chat(f"An error occurred: {e}")
                update_ui_stopped_listening()

    threading.Thread(target=listen_continuously, daemon=True).start()

# Function to detect current location using geocoder
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return g
        else:
            print(f"Geocoder error: {g.status}")
            return None
    except Exception as e:
        print(f"Location detection error: {e}")
        return None

# Function to fetch weather data from OpenWeatherMap API
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching weather data: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return None
    except Exception as ex:
        print(f"Exception occurred: {ex}")
        return None

# Function to quit the application
def quit_application():
    global engine  # Ensure engine is accessible within this function
    speak("Exiting now, Goodbye!")
    # Stop the pyttsx3 engine gracefully
    engine.stop()
    root.quit()

# Create the main application window
root = tk.Tk()
root.title("luna")

# Set the style
style = ttk.Style()
style.configure('TFrame', background='#e0f7fa')
style.configure('TButton', font=('Helvetica', 10), padding=5, relief='flat', background='#00796b', foreground='#ffffff')
style.map('TButton', background=[('active', '#004d40')])
style.configure('TLabel', background='#e0f7fa', font=('Helvetica', 12))
style.configure('TScrolledText', font=('Helvetica', 12))

# Create a frame for the main content
main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

# Create a canvas for the background image
canvas = tk.Canvas(main_frame, width=800, height=600)
canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

try:
    # Load the background image
    background_image = tk.PhotoImage(file="background.png")
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
except tk.TclError as e:
    print(f"Error loading background image: {e}")

# Create a text widget for displaying the conversation
conversation_text = ScrolledText(main_frame, wrap=tk.WORD, height=20, font=('Helvetica', 12), bg='#ffffff', fg='#000000', relief='flat', borderwidth=0)
conversation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
conversation_text.tag_config("luna", foreground="#00796b", font=('Helvetica', 12, 'bold'))
conversation_text.tag_config("user", foreground="#004d40", font=('Helvetica', 12))
conversation_text.config(state=tk.DISABLED)

# Initial commands to display on startup
initial_commands = [
    "Welcome! I am luna, your personal assistant.",
    "You can ask me to open webistes like Google, YouTube, or Spotify.",
    "You can also ask me to search Google or YouTube for you.",
    "To play a song, say 'play on spotify <song name>'",
    "Additionally, I can provide weather information and convert currency.",
    "Start by pressing the 'Start Conversation' button."
]

# Function to display initial commands
def display_initial_commands():
    for cmd in initial_commands:
        add_chat(cmd, sender="luna", speak_response=False)

# Create a 'Start' button to initiate voice command listening
start_button = ttk.Button(main_frame, text="Start Conversation", style='Black.TButton', command=start_listening)
start_button.grid(row=1, column=0, pady=10)

# Create a 'Quit' button to exit the application
quit_button = ttk.Button(main_frame, text="Quit", style='Black.TButton', command=quit_application)
quit_button.grid(row=2, column=0, pady=10)

# Set the style for black text buttons
style.configure('Black.TButton', foreground='black', font=('Helvetica', 10))

# Display initial commands
display_initial_commands()

# Start the Tkinter main loop
root.mainloop()




''''
Can you make it such that once the user presses 'start conversation', Luna introduces herself then listens to a command. it then responds to that first command. After that, it should be continuously listening for the wake word after it has responded to the first command. I want there to be a wake word for example 'Hey Luna' that a user will speak that will activate Luna and it will start listening for further commands. can you implement this?

'''