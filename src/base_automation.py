from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BaseAutomation:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def login(self, login_url: str, username_selector: str, password_selector: str, login_button_selector: str, username: str, password: str):
        self.driver.get(login_url)
        self.driver.find_element(By.CSS_SELECTOR, username_selector).send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, password_selector).send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, login_button_selector).click()

    def search_jobs(self, search_url: str, search_field_selector: str, job_title: str):
        self.driver.get(search_url)
        search_field = self.driver.find_element(By.CSS_SELECTOR, search_field_selector)
        search_field.send_keys(job_title)
        search_field.send_keys(Keys.RETURN)

    def logout(self, profile_dropdown_selector: str, sign_out_button_selector: str):
        self.driver.find_element(By.CSS_SELECTOR, profile_dropdown_selector).click()
        self.driver.find_element(By.CSS_SELECTOR, sign_out_button_selector).click()
