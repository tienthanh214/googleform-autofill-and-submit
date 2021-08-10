# Task
Someone send us a Google-form, and we need to fill it everyday or maybe every hour to report something.

It seems to be boring, so I just think to write a script to build this auto-bot using **Python 3**
# Just build it
## Create and access URL
The URL of the Google form will look like this:
```
https://docs.google.com/forms/d/e/form-index/viewform
```
Just copy it and replace **viewform** to **formResponse**
```
https://docs.google.com/forms/d/e/form-index/formResponse
```

## Extract information

Open the Google form, then open DevTools (inspect) for inspecting the input element.

Each of the input elements which we need to fill data has format: ```name = "entry.id"```

Try to fill each input box to know its id

## Write the Python script

### Fill form
Create a dictionary in which keys are the name attributes of each input element, and values are the data you need to fill out

```py
def fill_form():
    name = get_name_by_day()
    date, hour = str(get_gmt_time()).split(' ')
    date = date.split('-')
    hour = hour.split(':')
    if (int(hour[0]) < 10):
        hour[0] = hour[0][1:]

    value = {
         # Text
        "entry.2112281434": name,
        # Dropdown menu
        "entry.1600556346": "Sài Gòn",
        # Date
        "entry.77071893_year": date[0],
        "entry.77071893_month": date[1],
        "entry.77071893_day": date[2],
        # Hour
        "entry.855769839": hour[0] + 'h',
        # Checkbox 
        "entry.819260047": ["Cà phê", "Bể bơi"],
        # One choice
        "entry.1682233942": "Okay"
    }
    print(value, flush = True)
    return value
```

### Submit form
Just use POST method in ```requests```
```python
def submit(url, data):
    try:
        requests.post(url, data = data)
        print("Submitted successfully!")
    except:
        print("Error!")

submit(url, fill_form())
```
Done!!!


