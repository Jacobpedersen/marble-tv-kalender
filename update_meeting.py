#!/usr/bin/env python3
import datetime, json, os, re, urllib.request
import icalendar, recurring_ical_events

url = os.environ.get("ICS_URL", "").strip()
req = urllib.request.Request(url, headers={"User-Agent": "marble-cal/1.0"})
data = urllib.request.urlopen(req, timeout=30).read()
cal = icalendar.Calendar.from_ical(data)
now = datetime.datetime.now(datetime.timezone.utc)
horizon = now + datetime.timedelta(days=60)
occ = recurring_ical_events.of(cal).between(now, horizon)
best = None
for ev in occ:
    start = ev.get("DTSTART").dt
    if not isinstance(start, datetime.datetime):
        continue
    if start.tzinfo is None:
        start = start.replace(tzinfo=datetime.timezone.utc)
    su = start.astimezone(datetime.timezone.utc)
    if su < now:
        continue
    if str(ev.get("STATUS", "")).upper() == "CANCELLED":
        continue
    if best is None or su < best[0]:
        best = (su, start, ev)
if not best:
    payload = {"title": "", "start": "", "location": ""}
else:
    _, start, ev = best
    title = re.sub(r"^Option:\s*", "", str(ev.get("SUMMARY", "")).strip())
    loc = str(ev.get("LOCATION", "")).strip().replace("\n", ", ")
    if len(loc) > 70:
        loc = loc[:67] + "..."
    payload = {"title": title, "start": start.isoformat(), "location": loc}
with open("next.json", "w") as f:
    json.dump(payload, f, ensure_ascii=False)
print("wrote:", payload.get("title") or "(none)")
