from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import TimeoutException
import datetime
import threading, pyautogui 
import time 
app = Flask(__name__)

# GECKODRIVER
GECKODRIVER_PATH = "D:\\GECKODRIVER\\geckodriver.exe"

scheduled_posts = []

# SERVER OPTIONS
firefox_service = FirefoxService(GECKODRIVER_PATH)
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

def schedule_post(username, password, photo, caption, datetime_input):
    
    scheduled_time = datetime.datetime.strptime(datetime_input, "%Y-%m-%dT%H:%M")
    time_difference = (scheduled_time - datetime.datetime.now()).total_seconds()

    #Time Difference
    if time_difference > 0:
        threading.Timer(time_difference, post_scheduled, args=[username, password, photo, caption]).start()

def post_scheduled(username, password, photo, caption):
    driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
    try:
        
        driver.get("https://www.instagram.com/accounts/login/")

        #USERNAME
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.NAME, "username")))

        
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").submit()

        #Wait for login
        WebDriverWait(driver, 80).until(EC.url_contains("instagram.com"))

        #CREATE BUTTON
        create_post_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Create']")))
        create_post_button.click()

        # Wait for Upload
        new_post_modal = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Create new post')]")))

        #SELECT FROM COMPUTER
        select_from_computer_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Select from computer')]")))
        select_from_computer_button.click()

        time.sleep(2)

        file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))

        #Automating file upload using pyautogui
        pyautogui.write(photo.filename)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')
        #first "Next" button
        next_button_1 = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Next')]")))
        next_button_1.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'Next')]")))

        #second "Next" button
        next_button_2 = driver.find_element(By.XPATH, "//div[contains(text(), 'Next')]")
        next_button_2.click()

        #Add caption
        caption_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Write a caption')]")))

        caption_input.clear()
        caption_input.click()
        
        pyautogui.write(caption)

        time.sleep(5)

        #SHARE BUTTON
        share_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Share')]")
        share_button.click()

        # CONFIRMATION DIALOGUE
        try:
            confirmation_message = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Your post has been shared.')]")))
            print("Confirmation Message:", confirmation_message.text)
        except TimeoutException:
            print("Timed out waiting for the upload to complete")

    except NoSuchWindowException:
        print("Window is closed or not available.")
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('intersens2.html')

@app.route('/schedule', methods=['POST'])
def schedule_post_route():
    username = request.form['username']
    password = request.form['password']
    photo = request.files['photo']
    caption = request.form['caption']
    datetime_input = request.form['datetime']

    schedule_post(username, password, photo, caption, datetime_input)

    return redirect(url_for('timer_page', datetime=datetime_input))


@app.route('/timer-page')
def timer_page():
    return render_template('timer_page.html')

if __name__ == '__main__':
    app.run(debug=True)
