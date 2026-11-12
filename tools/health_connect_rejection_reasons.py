"""Synthetic-safe quality breakdown for Health Connect step records."""
def reasons(rows, floor, ceiling):
    seen=set()
    counts={"missing_uuid":0,"duplicate_uuid":0,"timestamp_type":0,"count_type":0,"time_bounds":0,"count_bounds":0,"valid":0}
    for uuid,start,end,count in rows:
        if not isinstance(uuid,str) or not uuid:
            counts["missing_uuid"]+=1
        elif uuid in seen:
            counts["duplicate_uuid"]+=1
        else:
            seen.add(uuid)
        if type(start) is not int or type(end) is not int:
            counts["timestamp_type"]+=1
        elif not floor<=start<end<=ceiling:
            counts["time_bounds"]+=1
        if type(count) is not int:
            counts["count_type"]+=1
        elif count<0 or count>100000:
            counts["count_bounds"]+=1
        if all((isinstance(uuid,str),bool(uuid),type(start) is int,type(end) is int,type(count) is int)) and floor<=start<end<=ceiling and 0<=count<=100000:
            counts["valid"]+=1
    return counts
