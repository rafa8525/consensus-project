"""Conservative analysis of actual step rows. No daily total until unambiguous."""
from datetime import datetime, timezone

def assess(rows, floor_ms, ceiling_ms):
    previous_end=None
    seen=set()
    total=0
    overlap=0
    invalid=0
    valid=0
    for row_id, uuid, start, end, count in rows:
        if (type(row_id) is not int or row_id <= 0 or row_id in seen
            or any(type(v) is not int for v in (start,end,count))
            or not (floor_ms <= start < end <= ceiling_ms)
            or not (0 <= count <= 100000)):
            invalid+=1
            continue
        seen.add(row_id)
        if previous_end is not None and start < previous_end:
            overlap+=1
        previous_end=end if previous_end is None else max(end, previous_end)
        valid+=1
        total+=count
    safe=bool(valid) and invalid==0 and overlap==0
    return {"records":len(rows),"valid":valid,"invalid":invalid,"overlap":overlap,
            "safe":safe,"total":total if safe else None}

def assess_db(db, now=None):
    now=now or datetime.now(timezone.utc)
    start=datetime(now.year,now.month,now.day,tzinfo=timezone.utc)
    floor=int(start.timestamp()*1000)
    ceiling=int(now.timestamp()*1000)+300000
    apps=db.execute(
        "SELECT a.package_name,COUNT(*) FROM steps_record_table s "
        "JOIN application_info_table a ON a.row_id=s.app_info_id "
        "GROUP BY a.package_name ORDER BY COUNT(*) DESC"
    ).fetchall()
    choices=[name for name,n in apps if name and "fitbit" in name.lower()]
    if len(choices)!=1:
        return {"status":"BLOCKED_AMBIGUOUS_FITBIT","sources":len(apps)}
    rows=db.execute(
        "SELECT s.row_id,s.uuid,s.start_time,s.end_time,s.count FROM steps_record_table s "
        "JOIN application_info_table a ON a.row_id=s.app_info_id "
        "WHERE a.package_name=? AND s.start_time >= ? AND s.end_time <= ? "
        "ORDER BY s.start_time,s.end_time,s.row_id", (choices[0],floor,ceiling)
    ).fetchall()
    quality=assess(rows,floor,ceiling)
    quality["status"]="SAFE_SOURCE_ONLY" if quality["safe"] else "BLOCKED_QUALITY"
    quality["sources"]=len(apps)
    return quality
