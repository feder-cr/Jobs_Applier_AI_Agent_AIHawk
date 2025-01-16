from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.selectors import LINKEDIN_SELECTORS

class LinkedInAutomation:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def login(self, username: str, password: str):
        self.driver.get("https://www.linkedin.com/login")
        self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["username_field"]).send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["password_field"]).send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["login_button"]).click()

    def search_jobs(self, job_title: str):
        self.driver.get("https://www.linkedin.com/jobs")
        search_field = self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["job_search_field"])
        search_field.send_keys(job_title)
        search_field.send_keys(Keys.RETURN)

    def apply_to_jobs(self):
        job_listings = self.driver.find_elements(By.CSS_SELECTOR, LINKEDIN_SELECTORS["job_listings"])
        for job in job_listings:
            try:
                job.click()
                apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, LINKEDIN_SELECTORS["apply_button"]))
                )
                apply_button.click()
                self.complete_application()
            except (TimeoutException, NoSuchElementException):
                continue

    def complete_application(self):
        while True:
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["next_button"])
                next_button.click()
            except NoSuchElementException:
                break
        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["submit_button"])
            submit_button.click()
        except NoSuchElementException:
            pass

    def logout(self):
        self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["profile_dropdown"]).click()
        self.driver.find_element(By.CSS_SELECTOR, LINKEDIN_SELECTORS["sign_out_button"]).click()
