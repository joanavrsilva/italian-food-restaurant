""" urls for the restaurant app. """
from django.urls import path
from . import views

urlpatterns = [
    path('make_booking', views.make_booking, name='make_booking'),
    path(
        'booking_confirmed/<booking_id>',
        views.booking_confirmed, name='booking_confirmed'),
    path('manage_bookings', views.manage_bookings, name='manage_bookings'),
    path('my_bookings', views.my_bookings, name='my_bookings'),
    path(
        'booking_detail/<booking_id>', views.booking_detail,
        name='booking_detail'),
    path('add_table_no/<booking_id>', views.add_table_no, name='add_table_no'),
    path(
        'toggle_updated/<booking_id>', views.toggle_updated,
        name='toggle_updated'),
    path(
        'delete_booking/<booking_id>', views.delete_booking,
        name='delete_booking'),
    path(
        'update_booking/<booking_id>', views.update_booking,
        name='update_booking'),
]
