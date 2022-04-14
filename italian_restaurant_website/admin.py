from django.contrib import admin
from .models import Restaurants

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'opening_time', 'closing_time')
    search_fields = ('name',)