""" Generator module for generating form request data """
import json


def generate_form_request_dict(entries, with_comment: bool = True):
    """ Generate a dict of form request data from entries """
    result = "{\n"
    entry_id = 0
    for entry in entries:
        if with_comment:
            # gen name of entry
            result += f"    # {entry['container_name']}{(': ' + entry['name']) if entry.get('name') else ''}{' (required)' * entry['required']}\n"
            # gen all options (if any)
            if entry['options']:
                result += f"    #   Options: {entry['options']}\n"
            else:
                result += f"    #   Option: {get_form_type_value_rule(entry['type'])}\n"
        # gen entry id
        entry_id += 1
        default_value = entry.get("default_value", "")
        default_value = json.dumps(default_value, ensure_ascii=False)
            
        if entry.get("type") == "required":
            result += f'    "{entry["id"]}": {default_value}'
        else:
            result += f'    "entry.{entry["id"]}": {default_value}'
        result += f"{(entry_id < len(entries)) * ','}\n"
    # remove the last comma
    result += "}"
    return result

def get_form_type_value_rule(type_id):
    ''' ------ TYPE ID ------ 
        0: Short answer
        1: Paragraph
        2: Multiple choice
        3: Dropdown
        4: Checkboxes
        5: Linear scale
        7: Grid choice
        9: Date
        10: Time
    '''
    if type_id == 9:
        return "YYYY-MM-DD"
    if type_id == 10:
        return "HH:MM (24h format)"
    return "any text"
