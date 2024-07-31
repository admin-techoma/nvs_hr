from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def calculate_paid_leave_days(leave):
    leave_fromdate = leave.leave_from_date
    leave_fromtime = leave.leave_from_time
    leave_todate = leave.leave_to_date
    leave_totime = leave.leave_to_time
    
    total_full_days = 0
    total_half_days = 0

    leave_from_datetime = datetime.combine(leave_fromdate, leave_fromtime)
    leave_to_datetime = datetime.combine(leave_todate, leave_totime)

    time_9_am = datetime.strptime('10:00', '%H:%M').time()
    time_6_pm = datetime.strptime('18:45', '%H:%M').time()

    if leave_fromdate == leave_todate:
        if leave_fromtime == time_9_am and leave_totime == time_6_pm:
            total_full_days += 1
        elif leave_fromtime == time_9_am and leave_totime == time_9_am:
            total_half_days += 0.5
        elif leave_fromtime == time_6_pm and leave_totime == time_6_pm:
            total_half_days += 0.5
    else:
        if leave_fromtime == time_9_am and leave_totime == time_6_pm:
          total_full_days += 1
        
        else:
            if leave_fromtime == time_6_pm:
              total_half_days += 0.5
              
            elif leave_fromtime == time_9_am:
              total_full_days += 1
              
        if leave_totime == time_9_am:
            total_half_days += 0.5
            
        if leave_totime == time_6_pm:
            total_full_days += 1

    # Calculate full days in between start and end dates
    current_date = leave_from_datetime + timedelta(days=1)
    while current_date < leave_to_datetime:
        total_full_days += 1
        current_date += timedelta(days=1)
 
    paid_leave_total = total_full_days + total_half_days
    
    if leave_fromdate != leave_todate:
        if leave_fromtime == time_9_am and leave_totime == time_6_pm:
            paid_leave_total = paid_leave_total - 1
            
    return paid_leave_total