import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import threading
from ttkthemes import ThemedTk
import datetime
import logging

# Import your main script here
from rs_bot import start_bot, stop_bot, config as bot_config

# Create main window
root = ThemedTk()
root.geometry('+%d+%d' % (root.winfo_screenwidth() // 2 - 250, root.winfo_screenheight() // 2 - 500))

# Set the theme after root window is created
root.set_theme("equilux")

# Set window title
root.title('RS Chat Bot Settings')

# Set window icon
root.iconbitmap('rs_logo.ico')

# Prevent window from being resizable
root.resizable(True, True)

# Configure logging
logging.basicConfig(filename='runescape_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        min_sleep_time = min_sleep_time_entry.get()
        max_sleep_time = max_sleep_time_entry.get()
        min_typing_speed = min_typing_speed_entry.get()
        max_typing_speed = max_typing_speed_entry.get()
        max_tokens = max_tokens_entry.get()
        time_interval = time_interval_entry.get()
        model = model_entry.get()

        # Input validation
        error_messages = []

        if not min_sleep_time.isdigit():
            error_messages.append('Invalid input: Minimum sleep time must be a positive integer.')

        if not max_sleep_time.isdigit():
            error_messages.append('Invalid input: Maximum sleep time must be a positive integer.')

        if not is_float(min_typing_speed):
            error_messages.append('Invalid input: Minimum typing speed must be a positive number.')

        if not is_float(max_typing_speed):
            error_messages.append('Invalid input: Maximum typing speed must be a positive number.')

        if not max_tokens.isdigit() or int(max_tokens) > 16:
            error_messages.append('Invalid input: Max tokens must be a positive integer less than or equal to 16.')

        if not time_interval.isdigit():
            error_messages.append('Invalid input: Time interval must be a positive integer.')

        if len(error_messages) > 0:
            messagebox.showerror('Error', '\n'.join(error_messages))
            return

        min_sleep_time = int(min_sleep_time)
        max_sleep_time = int(max_sleep_time)
        min_typing_speed = float(min_typing_speed)
        max_typing_speed = float(max_typing_speed)
        max_tokens = int(max_tokens)
        time_interval = int(time_interval)

        if min_sleep_time > max_sleep_time:
            messagebox.showerror('Error', 'Minimum sleep time cannot be greater than maximum sleep time.')
            return

        if min_typing_speed > max_typing_speed:
            messagebox.showerror('Error', 'Minimum typing speed cannot be greater than maximum typing speed.')
            return

        config['Settings']['min_sleep_time'] = str(min_sleep_time)
        config['Settings']['max_sleep_time'] = str(max_sleep_time)
        config['Settings']['min_typing_speed'] = str(min_typing_speed)
        config['Settings']['max_typing_speed'] = str(max_typing_speed)
        config['Settings']['max_tokens'] = str(max_tokens)
        config['Settings']['time_interval'] = str(time_interval)
        config['Settings']['model'] = model

         # Save user prompts
        config['user_prompts'] = {}

        # Save prompt 1 and prompt 2
        config['user_prompts']['prompt_1'] = prompt_1_entry.get('1.0', 'end-1c')
        config['user_prompts']['prompt_2'] = prompt_2_entry.get('1.0', 'end-1c')

        # Save additional prompts
        prompt_count = 3
        for widget in reversed(prompts_frame.grid_slaves()):
            if isinstance(widget, tk.Text) and widget.grid_info()['row'] >= 6:  # Assuming additional prompts start from row 4
                prompt_text = widget.get('1.0', 'end-1c')
                config['user_prompts'][f'prompt_{prompt_count}'] = prompt_text
                prompt_count += 1

        # Save the system prompts
        config['system_prompts'] = {}
        config['system_prompts']['morning_prompt'] = system_prompt_morning_entry.get('1.0', 'end-1c')
        config['system_prompts']['afternoon_prompt'] = system_prompt_afternoon_entry.get('1.0', 'end-1c')
        config['system_prompts']['night_prompt'] = system_prompt_night_entry.get('1.0', 'end-1c')

        # Save the config file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        messagebox.showinfo('Saved', 'Configuration has been saved!')
        logging.info('Configuration has been saved.')
    except Exception as e:
        messagebox.showerror('Error', f'An error occurred while saving the configuration: {str(e)}')
        logging.error(f'Error occurred while saving configuration: {str(e)}')

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Define start bot function
def start():
    try:
        global start_time
        start_time = datetime.datetime.now()
        threading.Thread(target=start_bot, args=(bot_config,)).start()
        start_button['state'] = 'disabled'
        stop_button['state'] = 'normal'
        update_running_time()
        update_prompt_selection()
        logging.info('Bot started.')
    except Exception as e:
        messagebox.showerror('Error', f'An error occurred while starting the bot: {str(e)}')
        logging.error(f'Error occurred while starting the bot: {str(e)}')

# Define stop bot function
def stop():
    try:
        global start_time
        stop_bot()
        stop_button['state'] = 'disabled'
        start_button['state'] = 'normal'
        running_time_label.config(text='Running Time:')
        prompt_status_value.config(text='')

        start_time = None
        logging.info('Bot stopped.')
    except Exception as e:
        messagebox.showerror('Error', f'An error occurred while stopping the bot: {str(e)}')
        logging.error(f'Error occurred while stopping the bot: {str(e)}')

# Define update running time function
def update_running_time():
    if start_time is None:
        return

    try:
        elapsed_time = datetime.datetime.now() - start_time
        running_time = str(elapsed_time).split('.')[0]
        hours, minutes, seconds = running_time.split(':')
        running_time_formatted = f'{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}'
        running_time_value.config(text=running_time_formatted)
        root.after(1000, update_running_time)
    except Exception as e:
        logging.error(f'Error occurred while updating running time: {str(e)}')

# Define update prompt selection function
def update_prompt_selection():
    try:
        current_time = datetime.datetime.utcnow()
        time_interval = int(bot_config['Settings']['time_interval'])
        user_prompts = list(bot_config['user_prompts'].keys())
        prompt_index = (current_time.minute // time_interval) % len(user_prompts)
        
        # Change the format from 'prompt_n' to 'Prompt n'
        prompt_name = f'Prompt {prompt_index + 1}'
        
        prompt_status_value.config(text=prompt_name)
        root.after(200, update_prompt_selection)
    except Exception as e:
        logging.error(f'Error occurred while updating prompts: {str(e)}')

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, background="#FFFFDD", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Create a notebook widget for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create settings tab
settings_frame = ttk.Frame(notebook, style='Dark.TFrame')
notebook.add(settings_frame, text='Settings')

# Set the font
font = ('Helvetica', 10)
small_font = ('Helvetica', 8)

# Create a style for widgets
style = ttk.Style(settings_frame)
style.configure('Dark.TFrame', background='#333333')
style.configure('Dark.TLabel', background='#333333', foreground='white')
style.configure('Dark.TEntry', fieldbackground='#555555', foreground='white', insertbackground='white')
style.configure('Dark.TButton', background='#004acc', foreground='white')
style.configure('Dark.TButton.Start', background='#43a044')
style.configure('Dark.TButton.Stop', background='#d32f2f')
style.configure('Dark.TSeparator', background='white')

# Create frames
frame1 = ttk.Frame(settings_frame, style='Dark.TFrame')
frame1.grid(row=0, padx=10, pady=5, sticky='w')

frame2 = ttk.Frame(settings_frame, style='Dark.TFrame')
frame2.grid(row=1, padx=10, pady=5, sticky='w')

frame3 = ttk.Frame(settings_frame, style='Dark.TFrame')
frame3.grid(row=2, padx=10, pady=5, sticky='w')

frame4 = ttk.Frame(settings_frame, style='Dark.TFrame')
frame4.grid(row=3, padx=10, pady=5, sticky='w')

frame5 = ttk.Frame(settings_frame, style='Dark.TFrame')
frame5.grid(row=4, padx=10, pady=5, sticky='w')

frame6 = ttk.Frame(settings_frame, style='Dark.TFrame')
frame6.grid(row=5, padx=10, pady=5, sticky='w')

# Model field
model_label = ttk.Label(frame1, text='Model:', font=font, style='Dark.TLabel')
model_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Create a dropdown menu for model selection
model_entry = ttk.Combobox(frame1, values=['GPT-2', 'GPT-3.5-turbo', 'GPT-4'], font=font, state='readonly')
model_entry.set(bot_config['Settings']['model'])
model_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
Tooltip(model_entry, 'Select the AI model to use')

min_sleep_time_label = ttk.Label(frame1, text='Minimum Sleep Time:', font=font, style='Dark.TLabel')
min_sleep_time_entry = ttk.Entry(frame1, style='Dark.TEntry', width=25)
min_sleep_time_entry.insert(0, bot_config['Settings']['min_sleep_time'])
min_sleep_time_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
min_sleep_time_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
Tooltip(min_sleep_time_entry, 'The minimum time the bot waits between messages')

max_sleep_time_label = ttk.Label(frame1, text='Maximum Sleep Time:', font=font, style='Dark.TLabel')
max_sleep_time_entry = ttk.Entry(frame1, style='Dark.TEntry', width=25)
max_sleep_time_entry.insert(0, bot_config['Settings']['max_sleep_time'])
max_sleep_time_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
max_sleep_time_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
Tooltip(max_sleep_time_entry, 'The maximum time the bot waits between messages')

min_typing_speed_label = ttk.Label(frame1, text='Minimum Typing Speed:', font=font, style='Dark.TLabel')
min_typing_speed_entry = ttk.Entry(frame1, style='Dark.TEntry', width=25)
min_typing_speed_entry.insert(0, bot_config['Settings']['min_typing_speed'])
min_typing_speed_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
min_typing_speed_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
Tooltip(min_typing_speed_entry, 'The minimum typing speed of the bot')

max_typing_speed_label = ttk.Label(frame1, text='Maximum Typing Speed:', font=font, style='Dark.TLabel')
max_typing_speed_entry = ttk.Entry(frame1, style='Dark.TEntry', width=25)
max_typing_speed_entry.insert(0, bot_config['Settings']['max_typing_speed'])
max_typing_speed_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')
max_typing_speed_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')
Tooltip(max_typing_speed_entry, 'The maximum typing speed of the bot')

max_tokens_label = ttk.Label(frame1, text='Max Tokens:', font=font, style='Dark.TLabel')
max_tokens_entry = ttk.Entry(frame1, style='Dark.TEntry', width=25)
max_tokens_entry.insert(0, bot_config['Settings']['max_tokens'])
max_tokens_label.grid(row=5, column=0, padx=10, pady=5, sticky='w')
max_tokens_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')
Tooltip(max_tokens_entry, 'The maximum number of tokens the bot can use for a response')

time_interval_label = ttk.Label(frame1, text='Time Interval:', font=font, style='Dark.TLabel')
time_interval_entry = ttk.Entry(frame1, style='Dark.TEntry', width=25)
time_interval_entry.insert(0, bot_config['Settings']['time_interval'])
time_interval_label.grid(row=6, column=0, padx=10, pady=5, sticky='w')
time_interval_entry.grid(row=6, column=1, padx=10, pady=5, sticky='w')
Tooltip(time_interval_entry, 'The interval at which the bot alternates between prompt 1 and prompt 2')

# Create the About section
about_label = ttk.Label(frame6, text='About', font=font, style='Dark.TLabel')
about_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

about_text = """
The RS Chat Bot is an AI-powered chatbot developed by Cipher Proxy. It utilizes advanced natural language processing techniques to comprehend and generate responses that closely resemble human-like conversation. The chatbot offers extensive customization options, allowing users to tailor prompts and settings to simulate a wide range of conversational scenarios.

Version: 2.8
Developer: James Feura
"""

about_text_label = ttk.Label(frame6, text=about_text, font=small_font, wraplength=500, style='Dark.TLabel')
about_text_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

# Style for the text boxes
style.configure('Dark.TEntry', fieldbackground='#555555', foreground='white', insertbackground='white')

# Create prompts tab
prompts_frame = ttk.Frame(notebook, style='Dark.TFrame')
notebook.add(prompts_frame, text='Prompts')

# Load user prompts from the config and add them to the GUI
user_prompts = bot_config['user_prompts']
for i, prompt_key in enumerate(user_prompts.keys()):
    if prompt_key.startswith('prompt_'):
        prompt_label = ttk.Label(prompts_frame, text=f'{prompt_key}', font=font, style='Dark.TLabel')
        prompt_label.grid(row=i+4, column=0, padx=10, pady=5, sticky='w')

        prompt_entry = tk.Text(prompts_frame, height=4, width=30, font=small_font, bg='#555555', fg='white',
                               insertbackground='white')
        prompt_entry.insert('1.0', user_prompts[prompt_key])
        prompt_entry.grid(row=i+4, column=1, padx=10, pady=5, sticky='w')
        Tooltip(prompt_entry, f'The prompt used for {prompt_key}')

# Create labels and text widgets for prompts
prompt_1_label = ttk.Label(prompts_frame, text='Prompt 1:', font=font, style='Dark.TLabel')
prompt_1_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

prompt_1_entry = tk.Text(prompts_frame, height=4, width=30, font=small_font, bg='#555555', fg='white', insertbackground='white')
prompt_1_entry.insert('1.0', bot_config['user_prompts']['prompt_1'])
prompt_1_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
Tooltip(prompt_1_entry, 'The prompt used when the bot sends a conspiracy message')

prompt_2_label = ttk.Label(prompts_frame, text='Prompt 2:', font=font, style='Dark.TLabel')
prompt_2_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

prompt_2_entry = tk.Text(prompts_frame, height=4, width=30, font=small_font, bg='#555555', fg='white', insertbackground='white')
prompt_2_entry.insert('1.0', bot_config['user_prompts']['prompt_2'])
prompt_2_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
Tooltip(prompt_2_entry, 'The prompt used when the bot sends an advertisement message')

system_prompt_morning_label = ttk.Label(prompts_frame, text='Morning Prompt:', font=font, style='Dark.TLabel')
system_prompt_morning_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

system_prompt_morning_entry = tk.Text(prompts_frame, height=3, width=30, font=small_font, bg='#555555', fg='white', insertbackground='white')
system_prompt_morning_entry.insert('1.0', bot_config['system_prompts']['morning_prompt'])
system_prompt_morning_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
Tooltip(system_prompt_morning_entry, 'The prompt used during the morning')

system_prompt_afternoon_label = ttk.Label(prompts_frame, text='Afternoon Prompt:', font=font, style='Dark.TLabel')
system_prompt_afternoon_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

system_prompt_afternoon_entry = tk.Text(prompts_frame, height=3, width=30, font=small_font, bg='#555555', fg='white', insertbackground='white')
system_prompt_afternoon_entry.insert('1.0', bot_config['system_prompts']['afternoon_prompt'])
system_prompt_afternoon_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
Tooltip(system_prompt_afternoon_entry, 'The prompt used during the afternoon')

system_prompt_night_label = ttk.Label(prompts_frame, text='Night Prompt:', font=font, style='Dark.TLabel')
system_prompt_night_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')

system_prompt_night_entry = tk.Text(prompts_frame, height=3, width=30, font=small_font, bg='#555555', fg='white', insertbackground='white')
system_prompt_night_entry.insert('1.0', bot_config['system_prompts']['night_prompt'])
system_prompt_night_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')
Tooltip(system_prompt_night_entry, 'The prompt used during the night')

# Create labels for time
current_time_label = ttk.Label(frame5, text='Current Time:', font=font, style='Dark.TLabel')
current_time_value = ttk.Label(frame5, text='', font=font, style='Dark.TLabel')

running_time_label = ttk.Label(frame5, text='Running Time:', font=font, style='Dark.TLabel')
running_time_value = ttk.Label(frame5, text='00:00:00', font=font, style='Dark.TLabel')

# Create labels for prompt status
prompt_status_label = ttk.Label(frame5, text='Prompt Status:', font=font, style='Dark.TLabel')
prompt_status_value = ttk.Label(frame5, text='', font=font, style='Dark.TLabel')

# Grid settings
model_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
model_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

min_sleep_time_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
min_sleep_time_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

max_sleep_time_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
max_sleep_time_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

min_typing_speed_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
min_typing_speed_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

max_typing_speed_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')
max_typing_speed_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

max_tokens_label.grid(row=5, column=0, padx=10, pady=5, sticky='w')
max_tokens_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')

time_interval_label.grid(row=6, column=0, padx=10, pady=5, sticky='w')
time_interval_entry.grid(row=6, column=1, padx=10, pady=5, sticky='w')

current_time_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
current_time_value.grid(row=0, column=1, padx=10, pady=5, sticky='w')

running_time_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
running_time_value.grid(row=1, column=1, padx=10, pady=5, sticky='w')

prompt_status_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
prompt_status_value.grid(row=2, column=1, padx=10, pady=5, sticky='w')

# Create buttons frame
button_frame = ttk.Frame(frame5, style='Dark.TFrame')
button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

# Create buttons
save_button = ttk.Button(button_frame, text='Save Settings', command=save, style='Dark.TButton', width=14)
start_button = ttk.Button(button_frame, text='Start Bot', command=start, style='Dark.TButton', width=14)
stop_button = ttk.Button(button_frame, text='Stop Bot', command=stop, style='Dark.TButton', width=14)

save_button.grid(row=0, column=0, padx=5, pady=5)
start_button.grid(row=0, column=1, padx=5, pady=5)
stop_button.grid(row=0, column=2, padx=5, pady=5)

# Grid prompts
system_prompt_morning_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
system_prompt_morning_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

system_prompt_afternoon_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
system_prompt_afternoon_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

system_prompt_night_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
system_prompt_night_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

prompt_1_label.grid(row=4, column=0, padx=10, pady=5, sticky='w')
prompt_1_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

prompt_2_label.grid(row=5, column=0, padx=10, pady=5, sticky='w')
prompt_2_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')

# Add functions for adding or subtracting user functions here, there should be 2 as default.
def add_prompt():
    # Get the number of current prompts
    current_prompt_count = len(bot_config['user_prompts'])

    # Check if the maximum number of prompts has been reached
    if current_prompt_count >= 10:
        messagebox.showwarning('Maximum Prompts Reached', 'You have reached the maximum number of prompts.')
        return

    # Create a new prompt label
    prompt_label = ttk.Label(prompts_frame, text=f'Prompt {current_prompt_count + 1}:', font=font, style='Dark.TLabel')
    prompt_label.grid(row=current_prompt_count + 4, column=0, padx=10, pady=5, sticky='w')

    # Create a new prompt text widget
    prompt_entry = tk.Text(prompts_frame, height=4, width=30, font=small_font, bg='#555555', fg='white', insertbackground='white')
    prompt_entry.grid(row=current_prompt_count + 4, column=1, padx=10, pady=5, sticky='w')
    Tooltip(prompt_entry, f'The prompt used for Prompt {current_prompt_count + 1}')

    # Store the new prompt in the config
    bot_config['user_prompts'][f'prompt_{current_prompt_count + 1}'] = ''

    # Update the prompts layout
    prompts_frame.update()

def remove_prompt():
    # Get the number of current prompts
    current_prompt_count = len(bot_config['user_prompts'])

    # Check if the minimum number of prompts has been reached
    if current_prompt_count <= 2:
        messagebox.showwarning('Minimum Prompts Reached', 'You must have at least two prompts.')
        return

    # Remove the last prompt label and text widget from the layout
    prompt_label = prompts_frame.grid_slaves(row=current_prompt_count + 3, column=0)
    prompt_entry = prompts_frame.grid_slaves(row=current_prompt_count + 3, column=1)

    if prompt_label:
        prompt_label[0].grid_forget()
    if prompt_entry:
        prompt_entry[0].grid_forget()

    # Remove the last prompt from the config
    del bot_config['user_prompts'][f'prompt_{current_prompt_count}']

    # Update the prompts layout
    prompts_frame.update()

add_prompt_button = ttk.Button(prompts_frame, text='Add Prompt', command=add_prompt, style='Dark.TButton', width=14)
remove_prompt_button = ttk.Button(prompts_frame, text='Remove Prompt', command=remove_prompt, style='Dark.TButton', width=14)

add_prompt_button.grid(row=0, column=0, padx=5, pady=5)
remove_prompt_button.grid(row=0, column=1, padx=5, pady=5)

# Update current time label
def update_current_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_time_value.config(text=current_time)
    if 6 <= now.hour < 12:
        current_time_label.config(text='Gameclock (Morning):')
    elif 12 <= now.hour < 18:
        current_time_label.config(text='Gameclock (Afternoon):')
    else:
        current_time_label.config(text='Gameclock (Night):')
    root.after(1000, update_current_time)

update_current_time()
update_prompt_selection()

# Create logging tab
logging_frame = ttk.Frame(notebook, style='Dark.TFrame')
notebook.add(logging_frame, text='Logging')

# Create the log section
log_font = ("Corier", 12)
log_label = ttk.Label(logging_frame, text='Log', font=log_font, style='Dark.TLabel')
log_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# Create a text widget with custom styling for the log section
log_output = tk.Text(logging_frame, width=50, height=40, font=('Courier', 8), wrap='word', bg='black', fg='white', state='disabled')
log_output.grid(row=1, column=0, padx=10, pady=5, sticky='w')

# Create a scrollbar for the log_output text widget
log_scrollbar = ttk.Scrollbar(logging_frame, orient='vertical', command=log_output.yview)
log_scrollbar.grid(row=1, column=1, sticky='ns')
log_output.configure(yscrollcommand=log_scrollbar.set)

# Create a Clear Log button
def clear_logs():
    # Temporarily enable the widget, clear it, then disable it again
    log_output.configure(state='normal')
    log_output.delete('1.0', tk.END)
    log_output.configure(state='disabled')

clear_button = ttk.Button(logging_frame, text="Clear Log", command=clear_logs)
clear_button.grid(row=2, column=0, padx=10, pady=5)

# Create text tags for each log level
log_output.tag_configure('INFO', foreground='lightgreen')
log_output.tag_configure('DEBUG', foreground='white')
log_output.tag_configure('WARNING', foreground='yellow')
log_output.tag_configure('ERROR', foreground='red')
log_output.tag_configure('CRITICAL', foreground='red', underline=1)

# Variable to keep track of where we left off in the log file
last_log_position = 0

# Function to read and display log file
def read_log_file():
    global last_log_position
    log_output.configure(state='normal')  # Temporarily make the widget editable
    with open('runescape_bot.log', 'r') as log_file:
        log_contents = log_file.read()
        log_output.insert(tk.END, log_contents)
        last_log_position = log_file.tell()  # Remember where we left off
    log_output.configure(state='disabled')  # Make the widget read-only again
    log_output.see(tk.END)  # Scroll to the bottom of the text widget

def update_log_output():
    global last_log_position
    log_output.configure(state='normal')  # Temporarily make the widget editable
    with open('runescape_bot.log', 'r') as log_file:
        log_file.seek(last_log_position)  # Jump to where we left off
        new_logs = log_file.read()  # Read and append new logs
        log_output.insert(tk.END, new_logs)
        # If the text widget is too filled, remove the oldest logs
        if int(log_output.index('end-1c').split('.')[0]) > 500:
            log_output.delete('1.0', '2.0')  # Remove the first line
        last_log_position = log_file.tell()  # Remember where we left off

        # Apply tags to new logs based on log level
        for tag in ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']:
            start_index = '1.0'
            while True:
                start_index = log_output.search(tag, start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f'{start_index.split(".")[0]}.{int(start_index.split(".")[1]) + len(tag)}'
                log_output.tag_add(tag, start_index, end_index)
                start_index = end_index

    log_output.configure(state='disabled')  # Make the widget read-only again
    # Scroll to the bottom of the text widget if the scrollbar is at the bottom
    scrollbar_position = log_scrollbar.get()[1]
    if scrollbar_position == 1.0:
        log_output.see(tk.END)
    root.after(1000, update_log_output)

# Initial log file read
read_log_file()
root.after(1000, update_log_output)  # Start log update loop

root.configure(background='#303030',)
root.mainloop()