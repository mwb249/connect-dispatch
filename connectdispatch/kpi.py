"""
To be completed...
"""

from datetime import datetime


def incident_times(call_dt, dispatch_dt, enroute_dt, arrival_dt, clear_dt):
    call = datetime.utcfromtimestamp(call_dt) if call_dt else call = None
    dispatch = datetime.utcfromtimestamp(dispatch_dt) if dispatch_dt else dispatch = None
    enroute = datetime.utcfromtimestamp(enroute_dt) if enroute_dt else enroute = None
    arrival = datetime.utcfromtimestamp(arrival_dt) if arrival_dt else arrival = None
    clear = datetime.utcfromtimestamp(clear_dt) if clear_dt else clear = None

    alarm_processing = turnout = travel = response = on_scene = inc_open = None

    if call and dispatch:
        alarm_processing = (dispatch - call).total_seconds()

    if dispatch and enroute:
        turnout = (enroute - dispatch).total_seconds()

    if enroute and arrival:
        travel = round((arrival - enroute).total_seconds() / 60, 2)

    if call and arrival:
        response = round((arrival - call).total_seconds() / 60, 2)

    if arrival and clear:
        on_scene = round((clear - arrival).total_seconds() / 60, 2)

    if call and clear:
        inc_open = round((clear - call).total_seconds() / 60, 2)

    return {'alarm_processing': alarm_processing, 'turnout': turnout, 'travel': travel,
            'response': response, 'on_scene': on_scene, 'inc_open': inc_open}
