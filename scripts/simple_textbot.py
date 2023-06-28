# Import necessary libraries
import time
import random
import sys
import pyautogui
from pynput.keyboard import Controller, Key

# Variables for easy customization
# Set hotkey to open chatbox. Here, Key.enter is used as an example
hotkey = Key.enter

# Window title of the game, used for focusing on the game window
window_title = "RuneScape"

# Minimum and maximum sleep time between messages (in seconds)
min_sleep_time = 1
max_sleep_time = 5

# Minimum and maximum typing speed to simulate human-like typing
min_typing_speed = 0.05
max_typing_speed = 0.15

# Pre-written text inputs to be randomly chosen for chat
text_inputs = [
    "Hello, World!",
    "How's it going?",
    "Nice weather, isn't it?",
    "Anyone up for a quest?",
    "Just chilling around",
]

# Initialize the keyboard controller from pynput library
keyboard = Controller()

# Function to press a hotkey to initiate chatbox
def press_hotkey():
    try:
        # Press and release the hotkey
        keyboard.press(hotkey)
        keyboard.release(hotkey)

        # Sleep for 1 second to ensure the chatbox opens
        time.sleep(1)
    except Exception as e:
        # If any error occurs, print it and exit the program
        print(f"An error occurred while pressing the hotkey: {str(e)}")
        sys.exit(1)

# Function to type a message into chat
def type_message(message):
    try:
        # For each character in the message
        for char in message:
            # Press and release the character
            keyboard.press(char)
            keyboard.release(char)

            # Sleep for a random time within the typing speed range
            time.sleep(random.uniform(min_typing_speed, max_typing_speed))

        # Press enter to send the message
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    except Exception as e:
        # If any error occurs, print it and exit the program
        print(f"An error occurred while typing the message: {str(e)}")
        sys.exit(1)

# Function to focus on the Runescape window
def focus_window():
    try:
        # Find the window with the given title
        window = pyautogui.getWindowsWithTitle(window_title)[0]

        # Bring the window to the foreground
        window.activate()
    except Exception as e:
        # If any error occurs, print it and exit the program
        print(f"An error occurred while trying to focus on the window: {str(e)}")
        sys.exit(1)

# Main loop to continually send messages
while True:
    try:
        # Randomly wait for a duration between min_sleep_time and max_sleep_time
        sleep_time = random.uniform(min_sleep_time, max_sleep_time)
        print(f"Sleeping for {sleep_time/60} minutes")
        time.sleep(sleep_time)

        # Focus on the game window
        focus_window()

        # Press the hotkey to open the chatbox
        press_hotkey()

        # Choose a random message from text_inputs and type it into the chatbox
        message = random.choice(text_inputs)
        print(f"Typing message: {message}")
        type_message(message)
    except KeyboardInterrupt:
        # If the user interrupts the program, print a message and break the loop
        print("Program terminated by user")
        break
    except Exception as e:
        # If any unexpected error occurs, print it and break the loop
        print(f"An unexpected error occurred: {str(e)}")
        break
