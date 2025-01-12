# This file contains CSS and XPath selectors for LinkedIn and Easy Apply pages

# LinkedIn Selectors
LINKEDIN_SELECTORS = {
    "login_button": "button[class*='sign-in-form__submit-button']",
    "username_field": "input[id='username']",
    "password_field": "input[id='password']",
    "job_search_field": "input[placeholder='Search jobs']",
    "job_search_button": "button[class*='search-global-typeahead__button']",
    "job_listings": "ul.jobs-search__results-list li",
    "apply_button": "button.jobs-apply-button",
    "next_button": "button[aria-label='Continue to next step']",
    "submit_button": "button[aria-label='Submit application']",
    "profile_dropdown": "div[class*='profile-rail-card__actor-link']",
    "sign_out_button": "a[href*='logout']"
}

# Easy Apply Selectors
EASY_APPLY_SELECTORS = {
    "easy_apply_button": "button.jobs-apply-button--top-card",
    "upload_resume_button": "input[type='file']",
    "submit_application_button": "button[aria-label='Submit application']",
    "next_step_button": "button[aria-label='Continue to next step']",
    "review_application_button": "button[aria-label='Review your application']",
    "profile_dropdown": "div[class*='profile-rail-card__actor-link']",
    "sign_out_button": "a[href*='logout']"
}
