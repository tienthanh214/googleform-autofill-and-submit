import argparse
import datetime
import json
import random

import requests

import form


def fill_random_value(type_id, entry_id, options, required = False, entry_name = ''):
    ''' Fill random value for a form entry 
        Customize your own fill_algorithm here
        Note: please follow this func signature to use as fill_algorithm in form.get_form_submit_request '''
    # Customize for specific entry_id
    if entry_id == 'emailAddress':
        return 'your_email@gmail.com'
    if entry_name == "Short answer":
        return 'Random answer!'
    # Random value for each type
    if type_id in [0, 1]: # Short answer and Paragraph
        return '' if not required else 'Ok!'
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

def generate_request_body(url: str, only_required = False):
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

def main(url, only_required = False):
    try:
        payload = generate_request_body(url, only_required = only_required)
        submit(url, payload)
        print("Done!!!")
    except Exception as e:
        print("Error!", e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit google form with custom data')
    parser.add_argument('url', help='Google Form URL')
    parser.add_argument('-r', '--required', action='store_true', help='Only include required fields')
    args = parser.parse_args()
    main(args.url, args.required)
