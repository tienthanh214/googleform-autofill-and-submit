import datetime
import json
import random

import requests

import form

URL = 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSdwcwvrOeBG200L0tCSUHc1MLebycACWIi3qw0UBK31GE26Yg/formResponse'

def fill_random_value(type_id, entry_id, options):
    ''' Fill random value for a form entry 
        Customize your own fill_algorithm here
        Note: please follow this func signature to use as fill_algorithm in form.get_form_submit_request '''
    # Customize for specific entry_id
    if entry_id == 'emailAddress':
        return 'your_email@gmail.com'
    # Random value for each type
    if type_id in [0, 1]: # Short answer and Paragraph
        return ''
    if type_id == 2: # Multiple choice
        return random.choice(options)
    if type_id == 3: # Dropdown
        return random.choice(options)
    if type_id == 4: # Checkboxes
        return random.sample(options, k=random.randint(1, len(options)))
    if type_id == 5: # Linear scale
        return random.choice(options)
    if type_id == 7: # Grid choice
        return random.choice(options)
    if type_id == 9: # Date
        return datetime.date.today().strftime('%Y-%m-%d')
    if type_id == 10: # Time
        return datetime.datetime.now().strftime('%H:%M')
    return ''

def generate_random_request_body(url: str, only_required = False):
    ''' Generate random request body data '''
    data = form.get_form_submit_request(
        url,
        only_required = only_required,
        fill_algorithm = fill_random_value,
        output = "return",
        with_comment = False
    )
    data = json.loads(data)
    # you can also override some values here
    return data

def submit(url: str, data: any):
    ''' Submit form to url with data '''
    url = form.get_form_response_url(url)
    print("Submitting to", url)
    print("Data:", data, flush = True)
   
    res = requests.post(url, data=data, timeout=5)
    if res.status_code != 200:
        print("Error! Can't submit form", res.status_code)
   

if __name__ == '__main__':
    try:
        payload = generate_random_request_body(URL, only_required = False)
        submit(URL, payload)
    except Exception as e:
        print("Error!", e)
        
