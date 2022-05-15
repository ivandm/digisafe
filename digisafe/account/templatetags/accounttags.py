from django import template

import datetime
import calendar
from dateutil import relativedelta

from agenda.models import Agenda

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
    # @return: query Agenda
    # print("accounttags.calendar_event")
    year = day.year
    month = day.month
    day = day.day
    d = datetime.date(int(year), int(month), int(day))
    q = Agenda.objects.filter(
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

@register.simple_tag
def calendar_is_today(year, month, day):
    d = datetime.date(int(year), int(month), int(day))
    today = datetime.date.today()
    return d==today

@register.simple_tag
def busy_in_date(date, user, datebook):
    """
    Verifica una data impegnata di User in Agenda
    :param date: datetime
    :param user: int
    :param user: DateSession object
    :return: str dd-mm-aaaa oppure False
    """
    q = Agenda.objects.filter(
        user=user, date_start__date__lte=date, date_end__date__gte=date).exclude(
        datebook=datebook
    )
    if q:
        return "{}".format(q[0].object)
    return False

@register.simple_tag(takes_context=True)
def session_confirm(context):
    """
    Controlla se un utente è stato confermato in un session book
    :param request: deve avere un contex 'object'
    :return: bool
    """
    user = context['user']
    sessionbook = context['object']
    for db in sessionbook.datebook_set.all():
        if user in db.users_confirm.all():
            return True
    return False
