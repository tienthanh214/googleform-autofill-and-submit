""" Get entries from form 
    Version 1: 
        - support submit almost all types of google form fields
        - only support single page form
        - not support upload file (because it's required to login)
    Date: 2023-12-17
"""

import json
import re

import requests

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdwcwvrOeBG200L0tCSUHc1MLebycACWIi3qw0UBK31GE26Yg/viewform" 

ALL_DATA_FIELDS = "FB_PUBLIC_LOAD_DATA_"

""" --------- Helper functions ---------  """

def get_form_response_url(url: str):
    url = url.replace('/viewform', '/formResponse')
    if not url.endswith('/formResponse'):
        if not url.endswith('/'):
            url += '/'
        url += 'formResponse'
    return url


def extract_script_variables(name :str, html: str):
    pattern = re.compile(r'var\s' + name + r'\s=\s(.*?);')
    match = pattern.search(html)
    if not match:
        return None
    value_str = match.group(1)
    return json.loads(value_str)

def get_fb_public_load_data(url: str):
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Error! Can't get form data", response.status_code)
        return None
    return extract_script_variables(ALL_DATA_FIELDS, response.text)

def parse_form_entries(url: str):
    """
    In window.FB_PUBLIC_LOAD_DATA_ (as v) 
    - v[1][1] is the form entries array
    - for x in v[1][1]:
        x[0] is the entry id of the entry container
        x[1] is the entry name (*)
        x[3] is the entry type 
        x[4] is the array of entry (usually length of 1, but can be more if Grid Choice, Linear Scale)
            x[4][0] is the entry id (we only need this to make request) (*)
            x[4][1] is the array of entry value (if null then text)
                x[4][1][i][0] is the i-th entry value option (*)
            x[4][2] field required (1 if required, 0 if not) (*)
            x[4][3] name of Grid Choice, Linear Scale (in array)

    """
    url = get_form_response_url(url)
        
    v = get_fb_public_load_data(url)
    if not v or not v[1] or not v[1][1]:
        print("Error! Can't get form entries")
        return None
    
    def parse_entry(entry):
        entry_name = entry[1]
        entry_type_id = entry[3]
        result = []
        for sub_entry in entry[4]:
            info = {
                "id": sub_entry[0],
                "container_name": entry_name,
                "type": entry_type_id,
                "required": sub_entry[2] == 1,
                "name": ' - '.join(sub_entry[3]) if (len(sub_entry) > 3 and sub_entry[3]) else entry_name,
                "options": [x[0] for x in sub_entry[1]] if sub_entry[1] else None,
            }
            result.append(info)
        return result

    parsed_entries = []
    for entry in v[1][1]:
        parsed_entries += parse_entry(entry)
        
    return parsed_entries


if __name__ == "__main__":
    entries = parse_form_entries(form_url)
    print(entries)