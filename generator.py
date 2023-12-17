def generate_form_request_dict(entries, with_comment: bool = True):
    """ Generate a dict of form request data from entries"""
    result = "{\n"
    for entry in entries:
        if with_comment:
            # gen name of entry
            result += f"    # {entry['container_name']}{': ' + entry['name'] if entry['name'] else ''} {'(required)' * entry['required']}\n"
            # gen all options (if any)
            if entry['options']:
                result += f"    #   Options: {entry['options']}\n"
            else:
                result += f"    #   Option: any text\n"
        # gen entry id
        result += f'    "entry.{entry["id"]}": "",\n'

    result += "}"
    return result

        