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
        datetime_comparison = time(6, 15)
        ##weekday_today = datetime_now.weekday()
        weekday_today = 4
        # alert_now = (res['states']['Одеська область']['alertnow'])
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
        wake_time = parse_time(config, weekday_today, "W")
        border_time = parse_time(config, weekday_today, "B")
        late_wake_time = parse_time(config, weekday_today, "L")
        return wake_time, border_time, late_wake_time
    else:
        return None, None, None


def save_user_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)
    return config


def input_schedule(config):
    while True:
        try:
            num_day = str(input("For which day would you like to set an alarm?: "))
            if num_day in config["response"]:
                break
            else:
                print("Invalid input. Try again.")
        except ValueError:
            print("Invalid input. Try again.")
    while True:
        try:
            w_time = input("Set up a wake time (00:00): ")
            w_datetime = datetime.strptime(w_time, "%H:%M")
            break
        except ValueError:
            print("Invalid input. Try again.")
    while True:
        try:
            l_time = input("Set up a late wake time (00:00): ")
            l_datetime = datetime.strptime(l_time, "%H:%M")
            if l_datetime > w_datetime:
                break
            else:
                print("Поздний подъем должен быть позже основного")
        except ValueError:
            print("Invalid input. Try again.")
    while True:
        try:
            b_time = input("Set up a border (00:00): ")
            b_datetime = datetime.strptime(b_time, "%H:%M")

            if w_datetime < b_datetime < l_datetime:
                config["response"][num_day]["W"] = w_time
                config["response"][num_day]["L"] = l_time
                config["response"][num_day]["B"] = b_time
                break
            else:
                print("Ошибка. Граница (B) должна быть позже подъема (W) и раньше позднего подъема (L)")
        except ValueError:
            print("Invalid input. Try again.")

    save_user_config(config)


def alarm_status(time_now, w_time, b_time, l_time, alert_now, alert_was):
    url = 'https://ubilling.net.ua/aerialalerts/'
    response = requests.get(url)
    res = response.json()

    time_now = datetime.now()
    alert_now = (res['states']['Одеська область']['alertnow'])


datetime_now = datetime.now()
print(datetime_now)

