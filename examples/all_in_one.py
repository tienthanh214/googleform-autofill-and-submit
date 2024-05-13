import datetime

import requests

URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSdwcwvrOeBG200L0tCSUHc1MLebycACWIi3qw0UBK31GE26Yg/formResponse"

def get_gmt_time(delta = 7):
    ''' get local time Vietnam (+7)
        help run correctly on any server'''
    date = datetime.datetime.now()
    tz = datetime.timezone(datetime.timedelta(hours = delta))
    return date.astimezone(tz)

start_day = datetime.datetime(2021, 8, 10,  tzinfo = datetime.timezone(datetime.timedelta(hours = 7)))
today = get_gmt_time()
names = ["Jug", "Hex", "John", "Anna"]

def get_name_by_day():
    return names[(today - start_day).days % 4]

def fill_form():
    name = get_name_by_day()
    date, hour = str(get_gmt_time()).split(' ')
    date = date.split('-')
    hour = hour.split(':')
    if (int(hour[0]) < 10):
        hour[0] = hour[0][1:]
    value = {
        # Name (required)
        #   Option: any text
        "entry.2112281434": name,
        # Where (required)
        #   Options: ['Ahihi', 'New York', 'Sài Gòn', 'Paris']
        "entry.1600556346": "Sài Gòn",
        # Date
        # "entry.77071893_year": date[0],
        # "entry.77071893_month": date[1],
        # "entry.77071893_day": date[2],
        # Date (YYYY-MM-DD)
        "entry.77071893": date[0] + '-' + date[1] + '-' + date[2],
        # Time (HH:MM (24h format))
        "entry.1734133505": hour[0] + ':' + hour[1],
        # Hour
        "entry.855769839": hour[0] + 'h',
        # Checkbox 
        "entry.819260047": ["Cà phê", "Bể bơi"],
        # One choice
        "entry.1682233942": "Okay",
        # Grid Choice: Question 2 
        #   Options: ['A', 'B', 'C']
        "entry.505915866": "A",
        # Grid checkbox: Question A 
        #   Options: ['1', '2', '3']
        "entry.1795513578": "2",
        # Grid checkbox: Question B 
        #   Options: ['1', '2', '3']
        "entry.1615989655": "3",
        # Page History 
        #   Options: from 0 to (number of page - 1)
        "pageHistory": "0,1",
        # Email address
        "emailAddress": "test_mail@gmail.com",
    }
    print(value, flush = True)
    return value


def submit(url, data):
    ''' Submit form to url with data '''
    try:
        res = requests.post(url, data=data, timeout=5)
        if res.status_code != 200:
            raise Exception("Error! Can't submit form", res.status_code)
        return True
    except Exception as e:
        print("Error!", e)
        return False

# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Running script...", flush = True)
    submit(URL, fill_form())    