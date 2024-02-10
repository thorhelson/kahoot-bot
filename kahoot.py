import asyncio
import aiohttp
import random
import string
from tkinter import Tk, Label, Listbox, Scrollbar, Button, Frame, Entry
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time

# Function to open Kahoot in Chrome and enter the code
def setup_browser():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

    # Initialize the WebDriver instance
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def open_kahoot_in_chrome(code, listbox, root, wait_time, nickname, ):
    # Setup browser inside the function to ensure thread safety
    driver = setup_browser()
    
    # Open a new tab
    driver.execute_script("window.open('');")
    
    # Switch to the new tab (assumes it is the last one opened)
    driver.switch_to.window(driver.window_handles[-1])
    
    # Navigate to Kahoot in the new tab and perform actions
    driver.get("https://kahoot.it/")
    # Wait for the page to load
    time.sleep(wait_time)
    
    try:
        input_field = driver.find_element(By.ID, "game-input")
        input_field.send_keys(code)
        
        submit_button = driver.find_element(By.CLASS_NAME, "button__Button-sc-vzgdbz-0")
        submit_button.click()
        
        time.sleep(1.5)
        
        nickname_field = driver.find_element(By.ID, "nickname")
        nickname_field.send_keys(nickname)
        
        submit_button = driver.find_element(By.CLASS_NAME, "button__Button-sc-vzgdbz-0")
        submit_button.click()
        
        time.sleep(1)

        error_detected = False
        error_classes = ["gATPEc", "haUqev", "two-factor-cards__square-button"]
        for error_class in error_classes:
            if driver.find_elements(By.CLASS_NAME, error_class):
                error_detected = True
                message = f"Error joining with code: {code}"
                root.after(0, lambda: listbox.insert('end', message))
                driver.quit()
                break
        
        if not error_detected:
            message = f"Success with code: {code}"
            root.after(0, lambda: listbox.insert('end', message))
            time.sleep(1000000)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        time.sleep(1000000)
        


    
def generate_random_number(length):
    return ''.join(random.choices(string.digits, k=length))

async def fetch(session, url):
    async with session.get(url) as response:
        return response.status, await response.text(), url.split('/')[-1]

async def request_with_random_number(root, listbox, stop_event, wait_time, nickname):
    async with aiohttp.ClientSession() as session:
        while not stop_event.is_set():
            random_number_length = random.randint(5, 8)
            random_number = generate_random_number(random_number_length)
            url = f"https://kahoot.it/reserve/session/{random_number}"
            status, text, code = await fetch(session, url)
            print(f"Code: {random_number}, Response: {status}")
            if status == 200:
                root.after(0, listbox.update_idletasks)
                #Search Time
                time.sleep(5 + wait_time)
                Thread(target=lambda: open_kahoot_in_chrome(code, listbox, root, wait_time, nickname)).start()



# The rest of the setup_gui and start_async_request functions remain the same
def start_async_request(loop, root, listbox, stop_event, wait_time, nickname):
    asyncio.set_event_loop(loop) 
    loop.run_until_complete(request_with_random_number(root, listbox, stop_event, wait_time, nickname))


def setup_gui():
    root = Tk()
    root.title("Kahoot Bot")
    frame = Frame(root)
    frame.pack(fill='both', expand=True)
    

    # Wait time entry
    wait_time_label = Label(frame, text="Wait Time (seconds):")
    wait_time1_label = Label(frame, text="(dont set below 1)")
    wait_time_label.pack(side='top', pady=(5,0))
    wait_time1_label.pack(side='top', pady=(5,0))
    wait_time_entry = Entry(frame)
    wait_time_entry.pack(side='top', pady=(0,5))
    wait_time_entry.insert(0, "2")  # Default wait time
    
    nickname_label = Label(frame, text="Nickname:")
    nickname_label.pack(side='top', pady=(5,0))
    nickname_entry = Entry(frame)
    nickname_entry.pack(side='top', pady=(0,5))
    nickname_entry.insert(0, "Hacker")

    # Listbox for messages
    listbox = Listbox(frame, height=20, width=50)
    listbox.pack(side='left', fill='y')
    scrollbar = Scrollbar(frame, orient='vertical')
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side='right', fill='y')
    listbox.config(yscrollcommand=scrollbar.set)

    stop_event = asyncio.Event()

    def on_start():
        # Get wait time and nickname from entries
        wait_time = float(wait_time_entry.get())
        nickname = nickname_entry.get()
        loop = asyncio.new_event_loop()
        t = Thread(target=start_async_request, args=(loop, root, listbox, stop_event, wait_time, nickname))
        t.start()

    start_button = Button(frame, text="Start Searching", command=on_start)
    start_button.pack(side='top', pady=5)

    def on_stop():
        stop_event.set()
        listbox.insert('end', 'Search stopped.')

    stop_button = Button(frame, text="Stop Searching", command=on_stop)
    stop_button.pack(side='top', pady=5)

    root.protocol("WM_DELETE_WINDOW", lambda: on_stop() or root.destroy())

    root.mainloop()


if __name__ == "__main__":
    setup_gui()
