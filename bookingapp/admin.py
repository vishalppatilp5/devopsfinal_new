"""admin"""
from django.contrib import admin
from .models import Flight, User, Booking

# Register your models here.

admin.site.register(Flight)
admin.site.register(User)
admin.site.register(Booking)