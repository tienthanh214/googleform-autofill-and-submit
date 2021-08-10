import requests
import datetime
import time
import random

url = "https://docs.google.com/forms/d/e/1FAIpQLSc5as-uLd4UOOR26iRaSpqdMuNneMP7pAO_KxOb50l5kcfY1g/formResponse"

def get_gmt_time(delta = 7):
    ''' get time in vietnam'''
    date = datetime.datetime.now()
    tz = datetime.timezone(datetime.timedelta(hours = delta))
    return date.astimezone(tz)


'''
19h - 5h 
'''
start_day = datetime.datetime(2021, 8, 10,  tzinfo = datetime.timezone(datetime.timedelta(hours = 7)))
today = get_gmt_time()
names = ["Nguyễn Đình Nhâm", "Nguyễn Đăng Kham", "Thông", "Mẫn"]
submit_hour = [19, 21, 23, 1, 3, 5]


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
        # Họ và tên
        "entry.648944920": name,
        # Đơn vị Tuần tra
        "entry.1323047968": "PHÚ BÀI",
        # Ngày Tuần tra
        "entry.914980634_year": date[0],
        "entry.914980634_month": date[1],
        "entry.914980634_day": date[2],
        # Thời gian Tuần tra
        "entry.1734465153": hour[0] + 'h',
        # Điểm tuần tra
        "entry.436161856": ["Tường rào", "Bồn bể", "Nhà bơm", "Giàn cấp phát"],
        # Kết quả tuần tra
        "entry.1224443740": "Bình thường"
    }
    print(value, flush = True)
    return value


def submit(url, data):
    try:
        requests.post(url, data = data)
        print("Submitted successfully")
        return True
    except:
        print("Error!")
        return False

'''----------------------------------------------------------------------'''
pre_submit = -1
submit_times = 0

print("Running script...", flush = True)
while True:
    if submit_times >= len(submit_hour):
        break

    now = get_gmt_time()
    now = now.strftime("%d-%m-%Y:%H:%M").split(':')

    if int(now[1]) in submit_hour:
        if pre_submit == int(now[1]):
            continue
        print('Now:', now[0], now[1] + ':' + now[2], flush = True)
        delay = random.randint(0, 10)
        print('Delay time:', delay, 'sec', flush = True)
        time.sleep(delay)

        while not submit(url, fill_form()):
            continue
        submit_times += 1            
        
        if int(now[1]) == submit_hour[-1]:
            break
        pre_submit = int(now[1])    
        time.sleep(2 * 60 * 60)