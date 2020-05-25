# Automation Scripts

### ``add_offline_time.py``
This script adds my TV watching events as an [Offline Time](https://help.rescuetime.com/article/76-how-to-record-offline-time) to [RescueTime](https://www.rescuetime.com).

TV watching time events come from my [HomeBridge-IFTTT](https://www.npmjs.com/package/homebridge-ifttt) setup. Each time an event triggers (``TV-on`` or ``TV-off``), my IFTTT recipe will run and add a new row to the spreadsheet (example below).

|        Time         | Event | Logged |
| ------------------- | ----- | ------ |
| 2020-05-24 18:37:00 | TV-on |  TRUE  | 
| 2020-05-24 19:30:00 | TV-off|  TRUE  |
| 2020-05-25 12:00:00 | TV-on |        | 
| 2020-05-25 13:30:00 | TV-off|        |

``add_offline_time.py`` will run on a daily basis to scan the spreadsheet for un-logged time events, pair them up to create a duration and then add to my RescueTime activities labeled as "``Watch TV``" (it will then automatically marked as "``Very Distracting``" activity). After the duration is successfully added to RescueTime, the script will go back and upload the corresponding rows in the spreadsheet and mark them as ``Logged``.

To install and run:
```bash
pip install -r requirements.txt 
# Make sure you have Google credentials.json in your directory
export RESCUETIME_API_KEY='[Your RescueTime API Key]' && \
export SPREADSHEET_ID='[Your Spreadsheet ID]' && \
python add_offline_time.py
```