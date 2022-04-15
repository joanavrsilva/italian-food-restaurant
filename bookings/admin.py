from django.contrib import admin

""" Admin panel set-up for the bookings app. """
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin options for the Booking model.
    """
    fields = ('date', 'time', 'party_size', 'tables', 'table_numbers',
              'customer', 'name', 'email', 'phone_number',
              'special_requirements', 'updated')
    list_display = ('name', 'email', 'date', 'time', 'party_size')
    readonly_fields = ('date', 'time', 'party_size', 'tables')
    search_fields = ['name']
    list_filter = ('date', 'party_size', 'updated')
    ordering = ('-date', '-time')
    # Enable delete action for this model
    actions = ['delete_selected']

    def has_add_permission(self, request):
        """
        Remove permission to add bookings to ensure they are not added
        without checking for availability.
        """
        return False
