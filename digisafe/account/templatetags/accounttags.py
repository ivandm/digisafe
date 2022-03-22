from django import template

import datetime, calendar
from dateutil import relativedelta

from account.models import UsersPosition

register = template.Library()

# START calendar
@register.simple_tag
def calendar_month_name(year, month):
    return datetime.datetime(int(year), int(month), 1)

@register.simple_tag
def calendar_before_month_name(year, month):
    datum = datetime.datetime(int(year), int(month), 1) - relativedelta.relativedelta(months=1)
    return datum

@register.simple_tag
def calendar_next_month_name(year, month):
    datum = datetime.datetime(int(year), int(month), 1) + relativedelta.relativedelta(months=1)
    return datum

@register.simple_tag
def calendar_event(user, day):
    # @param user: class django user
    # @param day: datetime.date type
    # @return: query UsersPosition
    # print("accounttags.calendar_event")
    year = day.year
    month = day.month
    day = day.day
    d = datetime.date(int(year), int(month), int(day))
    q = UsersPosition.objects.filter(
        user=user, date_start__date__lte=d, date_end__date__gte=d)
    # print(user, d, q)
    return q

@register.simple_tag
def calendar_tmpl(year, month):
    c = calendar.TextCalendar(0)
    return c.monthdatescalendar(int(year), int(month))

@register.simple_tag
def calendar_day_name():
    for day in calendar.day_name:
        yield day
# START calendar