import requests
from datetime import datetime, date, time, timezone
import json

def get_status():
    url = 'https://ubilling.net.ua/aerialalerts/'

    response = requests.get(url)

    if response.status_code == 200:
        res = response.json()
        ##print(res)

        datetime_now = datetime.now()
        ##datetime_comparison = datetime_now.time()
        datetime_comparison = time(6,15)
        ##weekday_today = datetime_now.weekday()
        weekday_today = 4
        #alert_now = (res['states']['Одеська область']['alertnow'])
        alert_now = True
    else:
        print(response.status_code)


def load_config():
    with open('config.json') as file:
        config = json.load(file)

    return config

weekday_today = str(datetime.today().weekday())

def parse_time(config, weekday_today, key):
    wake_text = config['response'][weekday_today][key]
    wake_datetime = datetime.strptime(wake_text, "%H:%M").time()

    return wake_datetime

config = load_config()

def get_today_schedule(config):
    weekday_today = str(datetime.today().weekday())
    if weekday_today in config["response"]:
        wake_time = parse_time(config,weekday_today,"W")
        border_time = parse_time(config,weekday_today,"B")
        late_wake_time = parse_time(config,weekday_today,"L")
        return wake_time, border_time, late_wake_time
    else:
        return None, None,None

def input_schedule(config):
    while True:
        try:
            num_day = str(input("For which day would you like to set an alarm?: "))
            if num_day < 5 and num_day >= 0:
                break
            else:
                print("Invalid input. Try again.")
        except ValueError:
            print("Invalid input. Try again.")



    def save_user_config(config):
        with open('config.json','w') as file:
            json.dump(config ,file ,indent = 4)
        return config


input_schedule(config)

