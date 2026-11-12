import json
import sys
import time
from datetime import datetime, date
from pathlib import Path
import requests
from playsound import playsound

app_dir = Path(
    sys.executable if getattr(sys, "frozen", False) else __file__
).resolve().parent

config_path = app_dir / "config.json"
alarm_path = app_dir / "alarm.mp3"
default_region = "Одеська область"
alerts_url = "https://ubilling.net.ua/aerialalerts/"

def load_config():
    try:
        with config_path.open(encoding="utf-8-sig") as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {}
    except json.JSONDecodeError:
        raise SystemExit("Not valid JSON")

    if not isinstance(config, dict):
        raise SystemExit("JSON has an unexpected format.")
    if not isinstance(config.get("response"), dict):
        config["response"] = {}
    return config


def save_user_config(config):
    with config_path.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)
    return config


def ask_time(text):
    while True:
        try:
            time_str = input(text)
            return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            print("Invalid input. Try again in H:M format")


def get_today_schedule(config):
    if "response" not in config:
        config["response"] = {}

    while True:
        print("\nWhich days would you like to set?")
        print(" 1. One specific day")
        print(" 2. Monday - Friday (0-4)")
        print(" 3. Every day (0-6)")
        choice = input("Choose 1, 2, or 3: ").strip()

        if choice == "1":
            day = input("Enter day number (0-6, where 0 is Monday): ").strip()
            if day in ["0", "1", "2", "3", "4", "5", "6"]:
                days = [day]
                break
            else:
                print("Invalid day.")
        elif choice == "2":
            days = ["0", "1", "2", "3", "4"]
            break
        elif choice == "3":
            days = ["0", "1", "2", "3", "4", "5", "6"]
            break
        else:
            print("Invalid choice. Enter 1, 2, or 3.")

    while True:
        w_time = ask_time("Set up a wake time (00:00): ")
        l_time = ask_time("Set up a late wake time (00:00): ")
        b_time = ask_time("Set up a border (00:00): ")

        if w_time < b_time < l_time:
            wake_time = w_time.strftime("%H:%M")
            late_wake_time = l_time.strftime("%H:%M")
            border_time = b_time.strftime("%H:%M")

            for day in days:
                if day not in config["response"]:
                    config["response"][day] = {}

                config["response"][day]["W"] = wake_time
                config["response"][day]["L"] = late_wake_time
                config["response"][day]["B"] = border_time

            save_user_config(config)
            print("Schedule saved successfully")
            return wake_time, late_wake_time, border_time
        else:
            print(
                "Error. The boundary (B) must be later than the rise (W) "
                "and earlier than the late rise (L)"
            )
            print("Try again")


day_names = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def remove_day(config):
    key = input("Enter day to remove (0-6): ").strip()
    if key in config["response"]:
        del config["response"][key]
    else:
        print("There was no schedule for that day.")
        return

    save_user_config(config)
    print(f"{day_names[int(key)]} is now a day off.")


def show_schedule(config):
    print("\nYour schedule:")
    for i in range(7):
        day_str = str(i)
        day_name = day_names[i]
        if day_str in config["response"]:
            w = config["response"][day_str]["W"]
            b = config["response"][day_str]["B"]
            l = config["response"][day_str]["L"]
            print(f"{day_name}: W={w} | B={b} | L={l}")
        else:
            print(f"{day_name}: Day off")


def ring():
    print("🔔 Time to wake up! 🔔")
    try:
        playsound(str(alarm_path))
    except Exception as e:
        print(f"Failed to enable sound: {e}")
    time.sleep(0.2)


def alarm_status(w_time, b_time, l_time, alert_now, time_now):
    if time_now < w_time:
        return False
    if w_time <= time_now < b_time and alert_now == False:
        return True
    if b_time <= time_now < l_time:
        return False
    if time_now >= l_time and alert_now == False:
        return True
    return False


def run_alarm(config):
    current_day_str = str(datetime.now().weekday())
    day_schedule = config.get("response", {}).get(current_day_str)

    if not day_schedule:
        print("You have a day off today. No alarm.")
        return

    w_time = datetime.strptime(day_schedule["W"], "%H:%M").time()
    b_time = datetime.strptime(day_schedule["B"], "%H:%M").time()
    l_time = datetime.strptime(day_schedule["L"], "%H:%M").time()

    today_str = date.today().isoformat()
    if config.get("last_ring_date") == today_str:
        print("Alarm already went off today.")
        return

    region = config.get("region", default_region)
    print("Alarm started for today! Waiting for time to ring... Press Ctrl+C to stop")

    while True:
        try:
            time_now = datetime.now().time()
            alert_now = get_alert_now(region)

            if alert_now is None:
                alert_now = False

            if alarm_status(w_time, b_time, l_time, alert_now, time_now):
                ring()
                config["last_ring_date"] = today_str
                save_user_config(config)
                break

            time.sleep(10)

        except KeyboardInterrupt:
            print("\nAlarm stopped.")
            break


def fetch_regions():
    response = requests.get(alerts_url, timeout=5)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Invalid API response")

    states = payload.get("states")
    if not isinstance(states, dict) or not states:
        raise ValueError("Region list is missing")

    return states


def get_alert_now(region):
    try:
        alert_now = fetch_regions()[region]["alertnow"]
        if isinstance(alert_now, bool):
            return alert_now
    except (requests.RequestException, ValueError, KeyError, TypeError):
        pass

    print("API unavailable (using default status: no alert)")
    return None


def choose_region(config):
    try:
        regions = sorted(fetch_regions())
    except (requests.RequestException, ValueError):
        print("Could not load the region list. Try again later.")
        return

    print("\nAvailable regions:")
    for number, region in enumerate(regions, start=1):
        print(f" {number}. {region}")
    print(" 0. Back")

    while True:
        try:
            choice = int(input("Choose a region: ").strip())
        except ValueError:
            print("Enter a number from the list.")
            continue

        if choice == 0:
            return

        if 1 <= choice <= len(regions):
            config["region"] = regions[choice - 1]
            save_user_config(config)
            print(f"Region saved: {config['region']}")
            return

        print("Enter a number from the list.")


def main():
    config = load_config()

    while True:
        print("\n   MENU   ")
        print(" 1. Set schedule")
        print(" 2. Remove a day")
        print(" 3. Show schedule")
        print(" 4. Start alarm")
        print(" 5. Exit")
        print(f" 6. Choose region (current: {config.get('region', default_region)})")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            get_today_schedule(config)
        elif choice == "2":
            remove_day(config)
        elif choice == "3":
            show_schedule(config)
        elif choice == "4":
            run_alarm(config)
        elif choice == "5":
            print("Exiting program...")
            break
        elif choice == "6":
            choose_region(config)
        else:
            print("Invalid choice. Please choose from 1 to 6.")


if __name__ == "__main__":
    main()