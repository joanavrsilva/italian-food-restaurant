""" Testcases for the bookings app forms. """
import datetime
from django.test import TestCase
from restaurant.models import Restaurant, Table
from .models import Booking
from .check_availability import create_booking_slots
from .forms import BookingForm


class TestBookingForm(TestCase):
    """ Tests for the booking form. """
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name='Il oro d'Italia')
        self.table = Table.objects.create(restaurant=self.restaurant, size=2)
        self.slots = create_booking_slots(
            self.restaurant.opening_time, self.restaurant.closing_time)
        self.booking_id = ''
        self.booking = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=2, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        self.booking.tables.add(self.table)

    def test_fields_are_explicit_in_form_metaclass(self):
        """ Test to check the correct fields are listed in the form meta. """
        form = BookingForm(self.slots, self.booking_id)
        self.assertEqual(
            form.Meta.fields,
            ('date', 'time', 'party_size', 'name', 'email',
             'phone_number', 'special_requirements'))

    def test_form_gives_error_if_no_tables_available(self):
        """ Test that validation error generated when no tables available. """
        form_data = {
            'date': datetime.date.today(),
            'time': datetime.time(18, 00),
            'party_size': 2,
            'name': 'A Name',
            'email': 'email@email.com',
            'phone_number': '01234567890',
        }
        form = BookingForm(self.slots, self.booking_id, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'][0],
            'Sorry no tables available at that time!')
