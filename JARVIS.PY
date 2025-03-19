import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import tkinter as tk
from tkinter import Canvas, PhotoImage
from random import choice
import time
import pygame
import subprocess
import psutil
import platform
import pyautogui
import threading
import cv2
import queue
import numpy as np
import requests
import json
import screeninfo

# Configuration
USER_NAME = "HASHMI SIR"
BOT_NAME = "JARVIS"
BROWSER_PATH = "C:\\Users\\MD HASHMI\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
JARVIS_VERSION = "2.1"
CASCADE_PATH = "haarcascade_frontalface_default.xml"

# API Keys
NEWS_API_KEY = (12345)  #From NewsAPI.org
WEATHER_API_KEY =  (1234) #From OpenWeatherMap.org
AI_API_KEY = (1234) #From OpenAI

# Initial HSV color ranges
COLOR_RANGES = {
    "pen": (np.array([90, 50, 50]), np.array([130, 255, 255])),  # Blue pen
    "book": (np.array([10, 50, 50]), np.array([40, 255, 255]))   # Brown/orange book
}

# Video and Audio file paths for intro
video_path = "C:\\Users\\MD HASHMI\\Downloads\\jarvisvideo.MOV"
audio_path = "C:\\Users\\MD HASHMI\\Downloads\\jarvisaudio.mp3"
image_path = "C:\\Users\\MD HASHMI\\OneDrive\\Desktop\\Coding\\Python\\JARVIS.AI\\jarvis.png"  # Updated path

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
if face_cascade.empty():
    print(f"Error: Could not load Haar Cascade from {CASCADE_PATH}")

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    print("Text-to-speech initialized successfully.")
except Exception as e:
    print(f"Error initializing text-to-speech: {str(e)}")
    engine = None

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize pygame for music and intro audio
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Warning: Pygame mixer failed to initialize - {str(e)}")

# GUI Setup
try:
    # Create root window first
    root = tk.Tk()
    
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Set fixed GUI resolution to 960x1080 (right half of 1920x1080, full height)
    gui_width, gui_height = 960, 1080
    
    # Position GUI on right half of the screen
    x_pos = screen_width - gui_width  # Right half, but adjust if screen is too narrow
    y_pos = (screen_height - gui_height) // 2  # Center vertically
    
    # Ensure GUI fits within screen
    if x_pos < 0:
        gui_width = screen_width  # Use full screen width if right half exceeds screen
        x_pos = 0
    if y_pos < 0 or (y_pos + gui_height) > screen_height:
        gui_height = screen_height  # Use full screen height if it exceeds
        y_pos = 0  # Position at top
    
    root.overrideredirect(True)  # Remove window decorations
    root.geometry(f"{gui_width}x{gui_height}+{x_pos}+{y_pos}")
    root.configure(bg="#000000")
    print(f"Tkinter window initialized successfully at 960x1080 on right half of screen (adjusted for {screen_width}x{screen_height}).")
except Exception as e:
    print(f"Error initializing Tkinter: {str(e)}")
    root = None

# Load JARVIS image for GUI
if root:
    try:
        jarvis_img = PhotoImage(file=image_path)  # Updated path
        jarvis_label = tk.Label(root, image=jarvis_img, bg="#000000")
        jarvis_label.place(x=0, y=0, width=gui_width, height=gui_height)
        print("JARVIS image loaded successfully.")
    except Exception as e:
        tk.Label(root, text="JARVIS", font=("Arial", 120, "bold"), fg="#00ffcc", bg="#000000").place(relx=0.5, rely=0.5, anchor="center")
        print(f"Warning: Could not load jarvis.png - {str(e)}")

    wave_canvas = Canvas(root, width=450, height=150, bg="#000000", highlightthickness=0)  # Adjusted for 960x1080
    wave_canvas.place(relx=0.5, rely=0.85, anchor="center")
    status_label = tk.Label(root, text="", font=("Arial", 30), fg="#00ffcc", bg="#000000")  # Larger font for bigger window
    status_label.place(relx=0.5, rely=0.70, anchor="center")

# Track states
listening = False
processing = False
speaking = False
browser_process = None
camera_open = False
cap = None
speech_queue = queue.Queue()
camera_event = threading.Event()
camera_closed_by_key = False
detection_mode = False

# Function to play introductory video and image
def play_intro():
    # Get screen resolution
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width
    screen_height = screen.height
    window_width = screen_width // 2
    window_height = screen_height

    # Function to play audio
    def play_audio():
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

    # Start audio in a separate thread
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()

    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    # Set window position to the right half of the screen
    cv2.namedWindow("JARVIS Intro", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("JARVIS Intro", window_width, window_height)
    cv2.moveWindow("JARVIS Intro", screen_width // 2, 0)

    # Play video
    start_time = time.time()
    video_duration = 17  # Duration in seconds
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or (time.time() - start_time > video_duration):
            break
        frame = cv2.resize(frame, (window_width, window_height))
        cv2.imshow("JARVIS Intro", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.music.stop()

    # Display JARVIS image using Tkinter (ensure it shows reliably)
    if root:
        try:
            # Load the image using PhotoImage (Tkinter)
            jarvis_img_tk = PhotoImage(file=image_path)  # Updated path
            # Create a temporary label for the intro window
            intro_window = tk.Toplevel(root)
            intro_window.overrideredirect(True)  # Remove window decorations
            intro_window.geometry(f"{window_width}x{window_height}+{screen_width // 2}+0")  # Position on right half
            intro_window.configure(bg="#000000")
            intro_label = tk.Label(intro_window, image=jarvis_img_tk, bg="#000000")
            intro_label.place(x=0, y=0, width=window_width, height=window_height)
            print("JARVIS image displayed successfully after intro.")
            # Ensure the window updates and stays visible for 3 seconds
            intro_window.update()
            intro_window.after(3000, intro_window.destroy)  # Close after 3 seconds
        except Exception as e:
            print(f"Error displaying JARVIS image after intro: {str(e)}")

# Function to speak text with wave animation
def speak(text):
    global speaking
    if not root or not engine:
        print(f"Cannot speak: GUI or speech engine not initialized - {text}")
        return
    
    def do_speak():
        nonlocal text
        print(f"{BOT_NAME}: {text}")
        status_label.config(text=f"{BOT_NAME}: {text}")
        speaking = True
        
        try:
            def animate_wave():
                wave_canvas.delete("all")
                for i in range(0, 450, 10):
                    height = choice([20, 30, 40, 50, 60]) if speaking else 10
                    wave_canvas.create_line(i, 75, i, 75 - height, fill="#00ffcc", width=3)
                    wave_canvas.create_line(i, 75, i, 75 + height, fill="#00ffcc", width=3)
                root.update()
                if speaking:
                    root.after(50, animate_wave)
            
            animate_wave()
            engine.say(text)
            engine.runAndWait()
            speaking = False
            animate_wave()
        except Exception as e:
            print(f"Speech error: {str(e)}")
            speaking = False
            animate_wave()

    if threading.current_thread() == threading.main_thread():
        do_speak()
    else:
        speech_queue.put(text)

# Process queued speech
def process_speech_queue():
    try:
        while not speech_queue.empty():
            text = speech_queue.get_nowait()
            speak(text)
    except Exception as e:
        print(f"Error processing speech queue: {str(e)}")

# Listen to voice input with improved sensitivity
def listen():
    global listening, processing
    try:
        with sr.Microphone() as source:
            print("Listening for command...")
            listening = True
            # Increase ambient noise adjustment duration for better accuracy
            recognizer.adjust_for_ambient_noise(source, duration=2)
            # Increase timeout and phrase time limit for better recognition
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            listening = False
            processing = True
            try:
                query = recognizer.recognize_google(audio).lower()
                print(f"{USER_NAME}: {query}")
                status_label.config(text=f"{USER_NAME}: {query}")
                processing = False
                return query
            except sr.UnknownValueError:
                processing = False
                print("Couldn’t catch that.")
                speak("Sorry, sir, I didn’t catch that. Could you repeat?")
                return None
            except sr.RequestError:
                processing = False
                speak("I'm having trouble connecting to the speech service.")
                return None
    except Exception as e:
        print(f"Microphone error: {str(e)}")
        return None

# Camera Functions with improved closing
def open_camera(detection=False):
    global camera_open, cap, detection_mode, camera_closed_by_key
    if camera_open:
        speak("Camera already open, sir.")
        return
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Error: Could not open camera, sir.")
        return
    
    camera_open = True
    detection_mode = detection
    camera_closed_by_key = False
    camera_event.clear()
    speak("Opening camera" + (" with detection" if detection else "") + ", sir.")
    threading.Thread(target=run_camera, daemon=True).start()

def run_camera():
    global camera_open, cap, detection_mode, camera_closed_by_key
    last_spoken_time = 0
    speech_interval = 2
    
    while camera_open and not camera_event.is_set():
        ret, frame = cap.read()
        if not ret:
            camera_open = False
            speech_queue.put("Error: Could not read camera frame, sir.")
            break
        
        frame = cv2.flip(frame, 1)
        
        if detection_mode:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            detections = {"pen": False, "book": False, "face": False}
            for obj_name, (lower, upper) in COLOR_RANGES.items():
                mask = cv2.inRange(hsv, lower, upper)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)
                detections[obj_name] = detect_objects(frame, mask, obj_name)
            
            detections["face"] = detect_faces(frame, gray)
            
            current_time = time.time()
            if any(detections.values()) and (current_time - last_spoken_time) > speech_interval:
                detected_items = [k for k, v in detections.items() if v]
                speech_queue.put(f"Detected: {', '.join(detected_items)}, sir.")
                last_spoken_time = current_time
            elif not any(detections.values()):
                cv2.putText(frame, "No objects detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("JARVIS Camera Feed", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera_closed_by_key = True
            camera_open = False
            break
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    camera_open = False
    detection_mode = False

def close_camera():
    global camera_open, detection_mode, camera_closed_by_key
    if camera_open:
        camera_event.set()
        time.sleep(0.5)  # Increased sleep to ensure proper closing
        camera_open = False
        detection_mode = False
        while not speech_queue.empty():
            speech_queue.get()
        speak("Camera closed, sir.")
    else:
        speak("Camera is not open, sir.")

# Detection Functions (unchanged)
def detect_objects(frame, mask, object_name):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detected = False
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            if object_name == "pen" and 0.1 < aspect_ratio < 1.0:
                label = "Pen"
            elif object_name == "book" and 0.5 < aspect_ratio < 2.0 and area > 2000:
                label = "Book"
            else:
                continue
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            detected = True
    
    return detected

def detect_faces(frame, gray):
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    detected = False
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        detected = True
    
    return detected

# API Functions (unchanged)
def get_news():
    url = f"https://newsapi.org/v2/everything?q=New+Delhi&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt&pageSize=3"
    try:
        response = requests.get(url)
        data = response.json()
        if data["status"] == "ok" and data["articles"]:
            headlines = [article["title"] for article in data["articles"]]
            return "Here are the latest news headlines from New Delhi, sir: " + "; ".join(headlines)
        else:
            return "Sorry, sir, I couldn’t fetch the news for New Delhi right now."
    except Exception as e:
        return f"Error fetching news, sir: {str(e)}"

def get_weather(city="New Delhi"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            return f"The weather in {city} is {temp} degrees Celsius with {weather}, sir."
        else:
            return f"Sorry, sir, I couldn’t get the weather for {city}."
    except Exception as e:
        return f"Error fetching weather, sir: {str(e)}"

def ask_ai(question):
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": question,
        "max_tokens": 100
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if "choices" in result and result["choices"]:
            return result["choices"][0]["text"].strip()
        else:
            return "Sorry, sir, I couldn’t process that with AI."
    except Exception as e:
        return f"Error with AI, sir: {str(e)}"

# Other Functions (unchanged)
def play_music():
    try:
        if not os.path.exists("background.mp3"):
            speak("No music file found. Please add 'background.mp3' to the script directory, sir.")
            return
        pygame.mixer.music.load("background.mp3")
        pygame.mixer.music.play()
        speak("Playing music, sir.")
        time.sleep(15)
    except Exception as e:
        speak(f"Error playing music: {str(e)}")

def stop_music():
    try:
        pygame.mixer.music.stop()
        speak("Music stopped, sir.")
    except Exception as e:
        speak(f"Error stopping music: {str(e)}")

def adjust_volume(direction):
    current_volume = pygame.mixer.music.get_volume()
    if direction == "up" and current_volume < 1.0:
        pygame.mixer.music.set_volume(min(1.0, current_volume + 0.1))
        speak(f"Volume increased to {int(pygame.mixer.music.get_volume() * 100)}%, sir.")
    elif direction == "down" and current_volume > 0.0:
        pygame.mixer.music.set_volume(max(0.0, current_volume - 0.1))
        speak(f"Volume decreased to {int(pygame.mixer.music.get_volume() * 100)}%, sir.")
    else:
        speak("Volume is already at its limit, sir.")

def get_system_status():
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return f"System status: CPU usage at {cpu_usage}%, memory usage at {memory.percent}%, disk space used at {disk.percent}%."

def set_reminder(query):
    def reminder_task(minutes):
        try:
            speak(f"Reminder set for {minutes} minutes from now, sir.")
            time.sleep(minutes * 60)
            speak("Reminder: Your time is up, sir.")
        except Exception as e:
            speak(f"Error in reminder task: {str(e)}")
    
    try:
        words = query.split()
        for i, word in enumerate(words):
            if word.isdigit():
                minutes = int(word)
                speak(f"Setting reminder for {minutes} minutes, sir.")
                reminder_thread = threading.Thread(target=reminder_task, args=(minutes,), daemon=True)
                reminder_thread.start()
                return
        speak("Please specify the time in minutes, sir (e.g., 'set a reminder in 5 minutes').")
    except Exception as e:
        speak(f"Error setting reminder: {str(e)}")

def take_screenshot():
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        speak("Screenshot taken, sir.")
        print(f"Screenshot saved to {os.path.abspath(filename)}")
    except Exception as e:
        speak(f"Error taking screenshot: {str(e)}")

def get_battery_status():
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "plugged in" if battery.power_plugged else "not plugged in"
            return f"Battery status: {percent}% remaining, {plugged}."
        return "Battery status not available on this device."
    except Exception as e:
        return f"Error fetching battery status: {str(e)}"

def open_website(url):
    global browser_process
    try:
        if browser_process and psutil.pid_exists(browser_process.pid):
            browser_process.terminate()
            time.sleep(1)
        browser_process = subprocess.Popen([BROWSER_PATH, url])
        speak(f"Opening {url}, sir.")
        return True
    except Exception as e:
        speak(f"Error opening website: {str(e)}")
        return False

def close_website():
    global browser_process
    if browser_process and psutil.pid_exists(browser_process.pid):
        browser_process.terminate()
        speak("Website closed, sir.")
        browser_process = None
    else:
        speak("No website is currently open, sir.")

# Process commands with improved recognition
def process_command(query):
    global camera_open, camera_closed_by_key
    if not query:
        return

    print(f"Recognized query: {query}")

    # Normalize query for better matching (handle variations)
    query = query.strip().lower()

    if "exit" in query or "close jarvis" in query:  # Added alternative for exit
        speak(f"Goodbye, {USER_NAME}.")
        if browser_process:
            close_website()
        if camera_open:
            close_camera()
        root.destroy()
        exit()

    elif "open camera detection" in query:
        open_camera(detection=True)

    elif "open camera" in query:
        open_camera(detection=False)

    elif "close camera" in query or "stop camera" in query:  # Added alternative for closing camera
        close_camera()

    elif "news" in query or "new delhi news" in query:
        news = get_news()
        speak(news)

    elif "weather" in query or "new delhi weather" in query:
        city = "New Delhi"
        for word in query.split():
            if word not in ["weather", "tell", "me", "the", "in", "sir", "new", "delhi"]:
                city = word.capitalize()
                break
        weather = get_weather(city)
        speak(weather)

    elif "ask ai" in query or "tell me about" in query:
        question = query.replace("ask ai", "").replace("tell me about", "").strip()
        if question:
            ai_response = ask_ai(question)
            speak(f"AI says: {ai_response}, sir.")
        else:
            speak("Please ask a question, sir.")

    elif "stop music" in query:
        stop_music()

    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}, sir.")

    elif "search" in query:
        search_terms = query.replace("search", "").strip()
        if "youtube" in query.lower():
            search_query = search_terms.replace("youtube", "").strip().replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={search_query}"
            if open_website(url):
                speak(f"Searching YouTube for {search_query.replace('+', ' ')}, sir.")
        elif "google" in query.lower():
            search_query = search_terms.replace("google", "").strip().replace(" ", "+")
            url = f"https://www.google.com/search?q={search_query}"
            if open_website(url):
                speak(f"Searching Google for {search_query.replace('+', ' ')}, sir.")
        elif "wikipedia" in query.lower():
            search_query = search_terms.replace("wikipedia", "").strip().replace(" ", "_")
            url = f"https://en.wikipedia.org/wiki/Special:Search?search={search_query}"
            if open_website(url):
                speak(f"Searching Wikipedia for {search_query.replace('_', ' ')}, sir.")
        else:
            speak("Where should I search, sir? YouTube, Google, or Wikipedia?")

    elif "open" in query:
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "wikipedia": "https://www.wikipedia.org",
            "github": "https://www.github.com",
            "twitter": "https://www.twitter.com",
            "netflix": "https://www.netflix.com",
            "linkedin": "https://www.linkedin.com",
            "amazon": "https://www.amazon.com"
        }
        for site, url in sites.items():
            if site in query.lower():
                speak(f"Opening {site}, sir.")
                if open_website(url):
                    speak(f"{site.capitalize()} is open, sir.")
                return
        speak("Which website should I open, sir? YouTube, Google, Wikipedia, GitHub, Twitter, Netflix, LinkedIn, or Amazon?")

    elif "close" in query.lower():
        if "website" in query or "the website" in query:
            close_website()
        elif "youtube" in query:
            close_website()
            speak("YouTube closed, sir.")
        elif "google" in query:
            close_website()
            speak("Google closed, sir.")
        elif "wikipedia" in query:
            close_website()
            speak("Wikipedia closed, sir.")
        elif "github" in query:
            close_website()
            speak("GitHub closed, sir.")
        elif "twitter" in query:
            close_website()
            speak("Twitter closed, sir.")
        elif "netflix" in query:
            close_website()
            speak("Netflix closed, sir.")
        elif "linkedin" in query:
            close_website()
            speak("LinkedIn closed, sir.")
        elif "amazon" in query:
            close_website()
            speak("Amazon closed, sir.")
        elif "camera" in query:
            close_camera()
        else:
            speak("Which website or camera should I close, sir?")

    elif "shutdown" in query:
        speak("Shutting down the system in 10 seconds.")
        os.system("shutdown /s /t 10")

    elif "play music" in query:
        play_music()

    elif "volume up" in query:
        adjust_volume("up")

    elif "volume down" in query:
        adjust_volume("down")

    elif "system status" in query:
        status = get_system_status()
        speak(status)

    elif "set a reminder" in query or "set reminder" in query:
        set_reminder(query)

    elif "date" in query:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {current_date}, sir.")

    elif "take screenshot" in query:
        take_screenshot()

    elif "battery status" in query:
        battery = get_battery_status()
        speak(battery)

    else:
        speak("I'm not sure how to assist with that, sir. Please try another command.")

# Main function
def main():
    global camera_closed_by_key
    if not root:
        print("GUI failed to initialize. Exiting.")
        return
    
    # Play intro video and display image
    play_intro()
    
    root.update()
    print("GUI updated with initial display.")
    
    speak(f"Welcome, {USER_NAME}. JARVIS version {JARVIS_VERSION} is now active. How may I assist you today, sir?")
    
    while True:
        if not speech_queue.empty():
            process_speech_queue()
        
        query = listen()
        if query:
            process_command(query)
        
        if camera_closed_by_key:
            while not speech_queue.empty():
                speech_queue.get()
            speak("Camera closed, sir.")
            camera_closed_by_key = False
        
        root.update()
        time.sleep(0.01)  # Reduced sleep for better responsiveness

if __name__ == "__main__":
    main()