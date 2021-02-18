"""
To be completed...
"""


def incident_times(call_dt, dispatch_dt, enroute_dt, arrival_dt, clear_dt):
    return {'alarm_processing': int((dispatch_dt - call_dt) / 1000) if call_dt and dispatch_dt else None,
            'turnout': int((enroute_dt - dispatch_dt) / 1000) if dispatch_dt and enroute_dt else None,
            'travel': round(((arrival_dt - enroute_dt) / 1000) / 60, 2) if enroute_dt and arrival_dt else None,
            'response': round(((arrival_dt - call_dt) / 1000) / 60, 2) if call_dt and arrival_dt else None,
            'on_scene': round(((clear_dt - arrival_dt) / 1000) / 60, 2) if arrival_dt and clear_dt else None,
            'incident_open': round(((clear_dt - call_dt) / 1000) / 60, 2) if call_dt and clear_dt else None}


def incident_status(enroute_dt, arrival_dt, clear_dt):
    if clear_dt:
        status = 'Clear'
    elif arrival_dt:
        status = 'Arrival'
    elif enroute_dt:
        status = 'Responding'
    else:
        status = 'Dispatched'
    return status
