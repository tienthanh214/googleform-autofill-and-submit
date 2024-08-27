""" Get entries from form 
    Version 2: 
        - support submit almost all types of google form fields
        - only support single page form
        - not support upload file (because it's required to login)
    Date: 2023-12-17
"""

import argparse
import json
import re

import requests

import generator

# constants
ALL_DATA_FIELDS = "FB_PUBLIC_LOAD_DATA_"
FORM_SESSION_TYPE_ID = 8
ANY_TEXT_FIELD = "ANY TEXT!!"

""" --------- Helper functions ---------  """

def get_form_response_url(url: str):
    ''' Convert form url to form response url '''
    url = url.replace('/viewform', '/formResponse')
    if not url.endswith('/formResponse'):
        if not url.endswith('/'):
            url += '/'
        url += 'formResponse'
    return url

def extract_script_variables(name :str, html: str):
    """ Extract a variable from a script tag in a HTML page """
    pattern = re.compile(r'var\s' + name + r'\s=\s(.*?);')
    match = pattern.search(html)
    if not match:
        return None
    value_str = match.group(1)
    return json.loads(value_str)

def get_fb_public_load_data(url: str):
    """ Get form data from a google form url """
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Error! Can't get form data", response.status_code)
        return None
    return extract_script_variables(ALL_DATA_FIELDS, response.text)

# ------ MAIN LOGIC ------ #

def parse_form_entries(url: str, only_required = False):
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
    - v[1][10][6]: determine the email field if the form request email
        1: Do not collect email
        2: required checkbox, get verified email
        3: required responder input
    """
    url = get_form_response_url(url)
        
    v = get_fb_public_load_data(url)
    if not v or not v[1] or not v[1][1]:
        print("Error! Can't get form entries. Login may be required.")
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
                "name": ' - '.join(sub_entry[3]) if (len(sub_entry) > 3 and sub_entry[3]) else None,
                "options": [(x[0] or ANY_TEXT_FIELD) for x in sub_entry[1]] if sub_entry[1] else None,
            }
            if only_required and not info['required']:
                continue
            result.append(info)
        return result

    parsed_entries = []
    page_count = 0
    for entry in v[1][1]:
        if entry[3] == FORM_SESSION_TYPE_ID:
            page_count += 1
            continue
        parsed_entries += parse_entry(entry)

    # Collect email addresses
    if v[1][10][6] > 1:
        parsed_entries.append({
            "id": "emailAddress",
            "container_name": "Email Address",
            "type": "required",
            "required": True,
            "options": "email address",
        })
    if page_count > 0:
        parsed_entries.append({
            "id": "pageHistory",
            "container_name": "Page History",
            "type": "required",
            "required": False,
            "options": "from 0 to (number of page - 1)",
            "default_value": ','.join(map(str,range(page_count + 1)))
        })
        
    return parsed_entries

def fill_form_entries(entries, fill_algorithm):
    """ Fill form entries with fill_algorithm """
    for entry in entries:
        if entry.get('default_value'):
            continue
        # remove ANY_TEXT_FIELD from options to prevent choosing it
        options = (entry['options'] or [])[::]
        if ANY_TEXT_FIELD in options:
            options.remove(ANY_TEXT_FIELD)
        
        entry['default_value'] = fill_algorithm(entry['type'], entry['id'], options, 
            required = entry['required'], entry_name = entry['container_name'])
    return entries

# ------ OUTPUT ------ #
def get_form_submit_request(
    url: str,
    output = "console",
    only_required = False,
    with_comment = True,
    fill_algorithm = None,
):
    ''' Get form request body data '''
    entries = parse_form_entries(url, only_required = only_required)
    if fill_algorithm:
        entries = fill_form_entries(entries, fill_algorithm)
    if not entries:
        return None
    result = generator.generate_form_request_dict(entries, with_comment)
    if output == "console":
        print(result)
    elif output == "return":
        return result
    else:
        # save as file
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
            print(f"Saved to {output}", flush = True)
            f.close()
    return None



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Form Autofill and Submit")
    parser.add_argument("url", help="Google Form URL")
    parser.add_argument("-o", "--output", default="console", help="Output file path (default: console)")
    parser.add_argument("-r", "--required", action="store_true", help="Only include required fields")
    parser.add_argument("-c", "--no-comment", action="store_true", help="Don't include explain comment for each field")
    args = parser.parse_args()
    get_form_submit_request(args.url, args.output, args.required, not args.no_comment)