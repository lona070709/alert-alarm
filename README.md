# Alert Clock

A command-line alarm clock for Windows that checks air raid alerts in the selected region of Ukraine before ringing. 
You can choose a region in Ukraine and set a different alarm schedule for
each day of the week.

## Run the project

Open PowerShell in the project folder and run:

```powershell
py -m pip install requests "playsound==1.2.2"
py main.py
```

Choose **6** to select a region, **1** to set your schedule, and **4** to start
the alarm for today. Keep the console open while the alarm is waiting.
Your schedule and region are saved in `config.json`.
