from django import template
from django.utils.safestring import mark_safe

from my_app.models import Booking
from accounts.models import Member

register = template.Library()


@register.simple_tag
def check_booking(user, object):
    try:
        member = Member.objects.get(username=user)
        obj = Booking.objects.get(user=member, book=object)
        return mark_safe("<p>You have booked/reserved this book</p>")
    except:
        return mark_safe("<p>Reserve this book:\
                    <a href=\"{% url 'my_app:reserve_book' object.id %}\" data-toggle=\"modal\" data-target=\"#myModal\">\
                    <i class=\"fa fa-bookmark\" id=\"bookmark-btn\" data-id=\"{{ object.id }}\"></i>\
                    </a>\
                </p>")
