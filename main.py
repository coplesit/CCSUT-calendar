### AIGC Artificial Intelligence Generated Code

week= ""
cookie= ""
userId= ""
xnxq= "" # semester

import requests
from datetime import timezone,datetime,timedelta
import json
from collections import defaultdict
import uuid

url = f"https://tls.ccsut.cn/admin/api/getXskb?xnxq={xnxq}&userId={userId}&xqid=&week={week}&role=xs"

headers = {
  'Cookie': f"{cookie}]"
}

data = requests.get(url, headers=headers)
data_dict = data.json()

START_DATE = datetime(2025+int(xnxq[:4]), 9, 1)

calendar_header = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your Organization//Your Product//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""

calendar_footer = "END:VCALENDAR"

ics_file= "calendar.ics"

CLASS_TIMES = {
    1:  ("08:20", "09:05"),
    2:  ("09:15", "10:00"),
    3:  ("10:20", "11:05"),
    4:  ("11:15", "12:00"),
    5:  ("14:00", "14:45"),
    6:  ("14:55", "15:40"),
    7:  ("16:00", "16:45"),
    8:  ("16:55", "17:40"),
    9:  ("19:00", "19:45"),
    10: ("19:55", "20:40"),
}



def get_class_time(week,xingqi,djc):
    if djc not in CLASS_TIMES:
        raise ValueError(f"Invalid class period: {djc}")
    if not (1 <= xingqi <= 7):
        raise ValueError(f"Invalid day of week: {xingqi}")
    start_str, end_str = CLASS_TIMES[djc]
    class_date = START_DATE + timedelta(weeks=week - 1, days=xingqi - 1)
    start_hour, start_minute = map(int, start_str.split(":"))
    end_hour, end_minute = map(int, end_str.split(":"))
    dtstart = class_date.replace(hour=start_hour, minute=start_minute, second=0)
    dtend = class_date.replace(hour=end_hour, minute=end_minute, second=0)
    dtstart_str = dtstart.strftime("%Y%m%dT%H%M%S")
    dtend_str = dtend.strftime("%Y%m%dT%H%M%S")
    return dtstart_str, dtend_str

def create_event(summary, week, xingqi, djc, location, description):
    result = get_class_time(week, xingqi, djc)
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtstart = result[0]
    dtend = result[1]
    uid =  f"{uuid.uuid4()}@example.com"

    event = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
LOCATION:{location}
DESCRIPTION:{description}
END:VEVENT
"""
    return event


try:
    with open(ics_file, "x", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//My Calendar//EN\n")
except FileExistsError:
    pass 

kckb_data = data_dict.get("data", {}).get("kckbData", [])

grouped = defaultdict(list)
for item in kckb_data:
    course_name = item.get("kcmc", "")
    location = item.get("croommc", "")
    instructor = item.get("tmc", "")
    xingqi = int(item.get("xingqi") or 1)
    djc = int(item.get("djc") or 1)
    key = (course_name, location, instructor, xingqi, week)
    grouped[key].append(djc)

for key, djc_list in grouped.items():
    course_name, location, instructor, xingqi, week_num = key
    instructor = "教师:" + instructor
    djc_list = sorted(djc_list)
    start_idx = 0
    while start_idx < len(djc_list):
        end_idx = start_idx
        while end_idx + 1 < len(djc_list) and djc_list[end_idx + 1] == djc_list[end_idx] + 1:
            end_idx += 1
        start_djc = djc_list[start_idx]
        end_djc = djc_list[end_idx]
        dtstart, _ = get_class_time(week_num, xingqi, start_djc)
        _, dtend = get_class_time(week_num, xingqi, end_djc)
        event = create_event(course_name, week_num, xingqi, start_djc, location, instructor)
        event_lines = event.splitlines()
        for i, line in enumerate(event_lines):
            if line.startswith("DTEND:"):
                event_lines[i] = f"DTEND:{dtend}"
                break
        event = "\n".join(event_lines) + "\n"
        with open(ics_file, "a", encoding="utf-8") as f:
            f.write(event)
        start_idx = end_idx + 1

with open(ics_file, "a", encoding ="utf-8") as f:
    f.write("END:VCALENDAR\n")




