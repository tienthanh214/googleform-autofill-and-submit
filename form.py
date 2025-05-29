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

def split_form_into_pages(form_data_json):
    """
    Split the form's fields into logical pages (sections)
    based on the structure of FB_PUBLIC_LOAD_DATA_.
    """
    entries = form_data_json[1][1]
    pages = []
    current_page = []

    for entry in entries:
        if entry[3] == FORM_SESSION_TYPE_ID:
            if current_page:
                pages.append(current_page)
                current_page = []
        current_page.append(entry)

    if current_page:
        pages.append(current_page)

    return pages

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
                x[4][1][i][2] is the next page id (if this option is selected)
            x[4][2] field required (1 if required, 0 if not) (*)
            x[4][3] name of Grid Choice, Linear Scale (in array)
        x[5] is the next page id (if this is a page, then it will be null)
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

    pages = split_form_into_pages(v)
    page_count = len(pages)

    # Initialize map of page id -> page index (from 0 to page_count - 1)
    page_ids = {}
    for i, page in enumerate(pages):
        for entry in page:
            if entry[3] == FORM_SESSION_TYPE_ID:
                page_ids[entry[0]] = i
                break
            
    # Find default next page index for each page
    default_next_page_ids = [0 for _ in range(page_count)]
    for i, page in enumerate(pages):
        default_next_page_ids[i] = i + 1 # Default next page is the next page in the list
        for entry in page:
            if entry[5] is not None and entry[5] > 0:
                if entry[0] == entry[5]: # Case ignore all and submit immediately
                    default_next_page_ids[i] = -1
                    break
                if entry[5] not in page_ids:
                    print(f"Warning: Page id {entry[5]} not found in page ids. Defaulting to next page.")
                    continue
                default_next_page_ids[i] = page_ids[entry[5]]

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
                "next_page_id": {}
            }
            if sub_entry[1]:
                for option in sub_entry[1]:
                    if len(option) > 2 and option[2] is not None:
                        info['next_page_id'][option[0]] = page_ids.get(option[2], 0)
            if only_required and not info['required']:
                continue
            result.append(info)
        return result

    # Only parse entries that are questions, each page is a list of entries
    page_entries = []
    for page in pages:
        page_entries.append([])
        for entry in page:
            if entry[3] == FORM_SESSION_TYPE_ID:
                continue
            page_entries[-1].extend(parse_entry(entry))

    # Collect email addresses
    if v[1][10][6] > 1:
        page_entries.append([{
            "id": "emailAddress",
            "container_name": "Email Address",
            "type": "required",
            "required": True,
            "options": "email address",
            "next_page_id": {},
        }])

    return page_entries, default_next_page_ids

def fill_form_entries(page_entries, default_next_page_ids, fill_algorithm):
    """ Fill form entries page by page with fill_algorithm """
    current_page_id = 0
    entries = []
    while (True):
        print(f"Processing page {current_page_id} of {len(page_entries)}")
        next_page_id = default_next_page_ids[current_page_id]
        for entry in page_entries[current_page_id]:
            # Remove ANY_TEXT_FIELD from options to prevent choosing it
            options = (entry['options'] or [])[::]
            if ANY_TEXT_FIELD in options:
                options.remove(ANY_TEXT_FIELD)
            
            # Fill value for the entry
            entry['default_value'] = fill_algorithm(entry['type'], entry['id'], options, 
                required = entry['required'], entry_name = entry['container_name'])
            
            # Determine next page id if needed
            if entry['next_page_id'] and entry['default_value'] in entry['next_page_id']:
                next_page_id = entry['next_page_id'][entry['default_value']]

            entries.append(entry)
        print(f"Page {current_page_id} entries: {entries}")
        if next_page_id < 0:
            break  # Case ignore all and submit immediately
        current_page_id = next_page_id
        
    # Fill pageHistory
    if len(page_entries) > 0:
        page_entries.append([{
            "id": "pageHistory",
            "container_name": "Page History",
            "type": "required",
            "required": False,
            "options": "from 0 to (number of page - 1)",
            "default_value": ','.join(map(str,range(len(page_entries) + 1))),
            "next_page_id": {},
        }])
        
    # Fill email address if needed
    if page_entries[-1] and len(page_entries[-1]) == 1 and page_entries[-1][-1]['id'] == "emailAddress":
        email_entry = page_entries[-1][-1]
        email_entry['default_value'] = fill_algorithm(0, email_entry['id'], [], 
            required = email_entry['required'], entry_name = email_entry['container_name'])
        entries.append(email_entry)

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
    page_entries, default_next_page_ids = parse_form_entries(url, only_required = only_required)
    for page in page_entries:
        print(page)
        print("----------")
    if not page_entries:
        return None
    if fill_algorithm:
        entries = fill_form_entries(page_entries, default_next_page_ids, fill_algorithm)
    else:
        # Flatten the list of entries
        entries = []
        for page in page_entries:
            for entry in page:
                entries.append(entry)
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