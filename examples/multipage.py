""" Multiple pages Google Form Example 
        just add the field "pageHistory" to the request body
"""
import requests

URL = "https://docs.google.com/forms/d/e/1FAIpQLSezUGYpq5iV9fUXymNoGzogcZgAqHuNBY-dOLR6LSDy2yub1g/formResponse"

data = {
    # Your name (required)
    #   Option: any text
    "entry.1715763968": "Your name",
    # Your age 
    #   Option: any text
    "entry.2032428014": "22",
    # None: Quiz 1 (required)
    #   Options: ['A', 'B', 'C', 'D']
    "entry.192506880": "A",
    # None: Quiz 2 (required)
    #   Options: ['A', 'B', 'C', 'D']
    "entry.250707008": "B",
    # None: Quiz 3 (required)
    #   Options: ['A', 'B', 'C', 'D']
    "entry.434270429": "C",
    # None: Quiz 4 (required)
    #   Options: ['A', 'B', 'C', 'D']
    "entry.1803402697": "D",
    # Do something? (required)
    #   Options: ['Option 1', 'Option 2', 'Option 3']
    "entry.368358396": "Option 1",
    # Page History 
    #   Options: from 0 to (number of page - 1)
    "pageHistory": "0,1,2,3,4",
}

res = requests.post(URL, data=data, timeout=5)
if res.status_code == 200:
    print("Successfully submitted the form")
else:
    print("Error! Can't submit form", res.status_code)

