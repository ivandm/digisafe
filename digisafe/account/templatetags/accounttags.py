from django import template

register = template.Library()


# @register.simple_tag
# def make_heads(obj):
#     print(obj)
#     print(dir(obj))
#     return ""