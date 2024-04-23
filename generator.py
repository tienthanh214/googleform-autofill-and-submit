def generate_form_request_dict(entries, with_comment: bool = True):
    """ Generate a dict of form request data from entries"""
    result = "{\n"
    for entry in entries:
        if with_comment:
            # gen name of entry
            result += f"    # {entry['container_name']}{': ' + entry.get('name', '') if entry.get('name') else ''} {'(required)' * entry['required']}\n"
            # gen all options (if any)
            if entry['options']:
                result += f"    #   Options: {entry['options']}\n"
            else:
                result += f"    #   Option: {get_form_type_value_rule(entry['type'])}\n"
        # gen entry id
        if entry['type'] == 'required':
            result += f'    "{entry["id"]}": "{entry.get("default_value", "")}",\n'
            continue

        result += f'    "entry.{entry["id"]}": "",\n'

    result += "}"
    return result

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
def get_form_type_value_rule(type_id):
    if type_id == 9:
        return "YYYY-MM-DD"
    if type_id == 10:
        return "HH:MM (24h format)"
    return "any text"