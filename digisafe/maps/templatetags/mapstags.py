from django import template

register = template.Library()

@register.simple_tag
def get_init_position(user):
    if user.is_authenticated:
        try:
            return user.usersposition.geom["coordinates"]
        except:
            print("No user position")