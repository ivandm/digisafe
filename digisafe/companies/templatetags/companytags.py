from django import template

register = template.Library()


@register.simple_tag
def pending_request(request, user):
    from companies.models import Company
    company_id = request.session.get("company_id")
    if company_id:
        c = Company.objects.get(pk=company_id)
        if user.requestassociatepending_set.filter(company=c):
            return True
    return False


@register.filter
def sort_by(queryset, order):
    order = [x.strip() for x in order.split(',')]
    return queryset.order_by(*order)
