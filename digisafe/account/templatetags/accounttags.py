from django import template

register = template.Library()


# @register.simple_tag
# def get_dir(obj):
    # print(obj.__class__.__name__)
    # print(dir(obj))
    # return ""