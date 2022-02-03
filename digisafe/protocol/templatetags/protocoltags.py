from django import template

import math

register = template.Library()
MAX_LEARNER_PER_PAGE = 2

@register.simple_tag
def get_dir(obj):
    print(obj.__class__.__name__)
    print(dir(obj))
    return ""
    
@register.simple_tag
def get_certificate_center_logo(protocol):
    if protocol.course.need_institution:
        return protocol.institution.get_logo_url()
    else:
        return protocol.center.get_logo_url()
        
@register.simple_tag
def page_add_1(n):
    return int(n)+1

@register.simple_tag
def max_learners_rest(protocol):
    # stop = protocol.learners_request
    stop = MAX_LEARNER_PER_PAGE #getattr(protocol.course, protocol.type).max_learners_theory
    start = len(protocol.learners_set.all())
    # print("protocoltags.max_learners_rest ",start, stop)
    return range(start+1,stop+1)

@register.simple_tag
def get_learner_per_page(protocol):
    # stop = protocol.learners_request
    learners = protocol.learners_set.all()
    pages = int(math.ceil(len(learners)/MAX_LEARNER_PER_PAGE))
    # print("protocoltags.get_num_page_learner ",pages)
    learner_list = []
    start = 0
    for i in range(pages):
        stop = (i+1)*MAX_LEARNER_PER_PAGE
        # print("get_learner_per_page ",start, stop )
        learner_list.append(learners[start : stop])
        start = stop
    return learner_list

@register.simple_tag
def learners_pages(protocol):
    learners = protocol.learners_set.all()
    pages = int(math.ceil(len(learners)/MAX_LEARNER_PER_PAGE))
    return pages
    
@register.simple_tag
def learners_pages_plus_first(protocol):
    learners = protocol.learners_set.all()
    pages = int(math.ceil(len(learners)/MAX_LEARNER_PER_PAGE))
    return pages+1
    
@register.simple_tag
def max_pages(protocol):
    # stop = protocol.learners_request
    learners = protocol.learners_set.all()
    learners_pages = int(math.ceil(len(learners)/MAX_LEARNER_PER_PAGE))
    sessions_pages = len(protocol.session_set.all())
    pages = 1+learners_pages+sessions_pages
    return pages
    
@register.simple_tag
def count_attendance(i, page):
    # print("count_attendance", i, page)
    s = (int(page)-1)*MAX_LEARNER_PER_PAGE
    # print("count_attendance", int(i)+s)
    return int(i)+s
    
@register.simple_tag
def sessions_pages(protocol):
    sessions = protocol.session_set.all()
    sessions_pages = len(sessions)
    # print("sessions_pages", sessions_pages)
    res = {}
    for i in range(sessions_pages):
        res[i+1] = sessions[i]
    return res
    
@register.simple_tag
def last_protocol_actions(protocol):
    if hasattr(protocol, "action_set"):
        return protocol.action_set.all().order_by("-pk")[:3]

from django.utils.safestring import  SafeText
@register.simple_tag
def get_certificate_content_i18n(protocol, i18n_code):
    res = protocol.course.feature.contents.filter(i18=i18n_code)
    if res:
        return SafeText(res[0].content)
    
