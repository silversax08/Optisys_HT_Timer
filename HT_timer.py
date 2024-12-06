import os
import shutil
import pandas as pd
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import threading
import time
import pygame

# Hardcoded sound file path
SOUND_FILE = r"C:\Users\GarrettHawkins\Downloads\alarm_sound.mp3"

# Profiles
PROFILES = {
    "A": {"threshold": 230, "timer_minutes": 360, "columns": ["B"]},
    "M": {"threshold": 275, "timer_minutes": 120, "columns": ["B"]},
    "O": {"threshold": 275, "timer_minutes": 120, "columns": ["B", "C"]},
}

# Folder to monitor
MONITOR_FOLDER = r"C:\Users\GarrettHawkins\Downloads"

# Function to get the newest CSV file
def get_newest_csv(folder):
    csv_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.csv')]
    return max(csv_files, key=os.path.getmtime) if csv_files else None

# Function to play sound
def play_sound(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Timer function
def start_timer(duration, timer_label):
    end_time = datetime.now() + timedelta(seconds=duration)
    while datetime.now() < end_time:
        remaining_time = end_time - datetime.now()
        timer_label.config(text=f"Time Remaining: {str(remaining_time).split('.')[0]}")
        time.sleep(1)
    timer_label.config(text="Time's Up!")
    play_sound(SOUND_FILE)

# Monitoring function
def monitor_file(profile, timer_label):
    while True:
        newest_csv = get_newest_csv(MONITOR_FOLDER)
        if newest_csv:
            temp_csv = "temp_copy.csv"
            shutil.copy(newest_csv, temp_csv)
            try:
                data = pd.read_csv(temp_csv)
                last_row = data.iloc[-1]
                threshold = profile["threshold"]
                columns = profile["columns"]

                if "B" in columns and last_row.iloc[1] > threshold:
                    if "C" in columns:
                        if last_row.iloc[2] > threshold:
                            timer_duration = profile["timer_minutes"] * 60
                            threading.Thread(target=start_timer, args=(timer_duration, timer_label)).start()
                            break
                    else:
                        timer_duration = profile["timer_minutes"] * 60
                        threading.Thread(target=start_timer, args=(timer_duration, timer_label)).start()
                        break
            finally:
                os.remove(temp_csv)
        time.sleep(10)

# GUI Setup
def create_gui():
    root = tk.Tk()
    root.title("Heat Treat Oven Monitor")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Profile selection
    ttk.Label(frame, text="Select Profile:").grid(row=0, column=0, sticky=tk.W)
    profile_var = tk.StringVar(value="A")
    profile_dropdown = ttk.Combobox(frame, textvariable=profile_var, values=list(PROFILES.keys()), state="readonly")
    profile_dropdown.grid(row=0, column=1, sticky=tk.W)

    # Timer display
    timer_label = ttk.Label(frame, text="Timer not started", font=("Helvetica", 16))
    timer_label.grid(row=1, column=0, columnspan=2, pady=10)

    # Start Monitoring Button
    def start_monitoring():
        selected_profile = profile_var.get()
        profile = PROFILES[selected_profile]
        threading.Thread(target=monitor_file, args=(profile, timer_label), daemon=True).start()

    start_button = ttk.Button(frame, text="Start Monitoring", command=start_monitoring)
    start_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
