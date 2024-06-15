# 🚀 Google Form AutoFill and Submit
Vietnamese version [here](https://tienthanh214.github.io/computer%20science/autofill-and-submit-ggform/)

Someone send us a Google-form, and we need to fill it everyday or maybe every hour to report something. It seems to be boring, so I just think to write a script to automate the process using **Python 3**

This is a simple and lightweight script to automatically fill and submit a Google form with random data. The script is customizable, allowing you to fill the form with the data you need.

It's also include a request body *generator* for those who prefer to manually input data, you can simply copy and paste a Google form URL, eliminating the need for manual inspection.

*This document will guide you through the process of creating a Python script to automatically fill and submit a Google form.*

## Table of Contents
- [🚀 Google Form AutoFill and Submit](#-google-form-autofill-and-submit)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Access and get the URL](#access-and-get-the-url)
  - [Extract information](#extract-information)
    - [Automatically](#automatically)
    - [Manually](#manually)
    - [Note](#note)
  - [Write the Python script](#write-the-python-script)
    - [Fill form](#fill-form)
    - [Submit form](#submit-form)
- [AutoFill and Submit](#autofill-and-submit)
  - [Run the Script](#run-the-script)
  - [Customize the Script](#customize-the-script)
- [Limitations](#limitations)

## Features
- [x] Supports multiple pages Google forms
- [x] Supports Google Forms that collect email addresses (Responder input)
- [x] Automatically generates the request body using the `form.py` script
- [x] Auto-fills the form with random values (customizable) and submits it

## Prerequisites
- Python 3.x
- `requests` library (`pip install requests` or `pip install -r requirements.txt`)

# Getting Started
If you only want to fill and submit a Google form with random data, or customize the script to fill the form with the data you need, you can skip to the [AutoFill and Submit](#autofill-and-submit) section.

Below are the steps to create a Python script to fill and submit a Google form. If you want to skip the manual inspection step, you can use the `form.py` script to automatically generate the request body (as described in the [Extract information Automatically](#automatically) section).

## Access and get the URL
The URL of the Google form will look like this:
```
https://docs.google.com/forms/d/e/form-index/viewform
```
Just copy it and replace **viewform** to **formResponse**
```
https://docs.google.com/forms/d/e/form-index/formResponse
```

## Extract information
### Automatically
Just copy the Google form URL and run [form.py](form.py) script. The script will return a *dictionary* which contains the name attributes of each input element and the data you need to fill out. 
```bash
python form.py <your-gg-form-url>
```
The result will be printed to the console (by default), or saved to a file if the `-o` option is used.

For more information, please use the help command
```bash
python form.py -h
```

Example:
```bash
python form.py 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSdwcwvrOeBG200L0tCSUHc1MLebycACWIi3qw0UBK31GE26Yg/formResponse' -o results.txt
```

### Manually
Open the Google form, then open DevTools (inspect) for inspecting the input element.

Each of the input elements which we need to fill data has format: ```name = "entry.id"```

Try to fill each input box to know its id

### Note
- If the form requires email, please add the `emailAddress` field
- For multiple pages forms, please add the `pageHistory` field with a comma-separated list of page numbers (starting from 0). For example, a 4-page form would have `"pageHistory": "0,1,2,3"`

## Write the Python script

### Fill form
Create a dictionary in which keys are the name attributes of each input element, and values are the data you need to fill out

```py
# example
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
        "entry.819260047": ["Cafe", "Fences"],
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

# AutoFill and Submit
## Run the Script
Run the `main.py` script with the Google form URL as an argument to automatically fill and submit the form with ***random data***
```bash
python main.py <your-gg-form-url>
```
For example:
```bash
python main.py 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSdwcwvrOeBG200L0tCSUHc1MLebycACWIi3qw0UBK31GE26Yg/viewform'
```
Use `-r`/`--required` to only fill the form with required fields
```bash
python main.py 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSdwcwvrOeBG200L0tCSUHc1MLebycACWIi3qw0UBK31GE26Yg/viewform' -r
```
## Customize the Script
The [main.py](main.py) script is a simple example of how to use the `form.py` script to automatically fill and submit a Google form. You can customize the `fill_form` function to fill the form with the data you need.

# Limitations
Please note that this script currently operates only with Google Forms that do not require user authentication.
