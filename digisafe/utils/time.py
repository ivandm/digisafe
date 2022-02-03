from datetime import timedelta

def timedelta_to_hm(timedelta_value):
    "ingresso oggetto timedelta uscita int ore, int minuti"
    if timedelta_value is None: 
        timedelta_value = timedelta(hours=0, minutes=0, seconds=0)
    secs = timedelta_value.total_seconds()
    hours = int(secs / 3600)
    minutes = int(secs / 60) % 60
    return hours, minutes
    
def timedelta_to_hm_str(timedelta_value):
    "ingresso oggetto timedelta uscita str 'ore:min'"
    hours, minutes = timedelta_to_hm(timedelta_value)
    return "{hours:02d}:{minutes:02d}".format(hours=hours, minutes=minutes)
