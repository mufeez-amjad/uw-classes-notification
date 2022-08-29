# uw-classes-notification

`main.py` is a script that notifies you if there are open spots for any courses you specified. It uses Twilio to call you (optionally) and message you.

You can deploy this script on UW's student servers (ECE or CS) and add it to the crontab.

Every 15 minutes:
```
*/15 * * * * cd /home/<userId>/scripts && .venv/bin/python3 schedule.py
```
