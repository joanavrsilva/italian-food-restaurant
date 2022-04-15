""" Testcases for the bookings app models. """
import datetime
from django.test import TestCase
from .models import Booking


class TestModels(TestCase):
    """ Tests for the model. """
    def setUp(self):
        self.booking = Booking.objects.create(
            date=datetime.date(2021, 11, 8), time=datetime.time(12, 00),
            party_size=4, name='Test Name', email='test@email.com',
            phone_number='01234567890')

    def test_booking_string_method_includes_date_and_party_size(self):
        """ Test the Booking model string method. """
        self.assertEqual(str(self.booking), 'A table of 4 on 08-11-2021')

    def test_booking_end_time_generated_on_save(self):
        """
        Test the Booking model generate_end_time method is
        run on save and saves a time 2 hours after the booking
        time.

        """
        self.assertEqual(self.booking.end_time, datetime.time(14, 00))

    def test_updated_defaults_to_true(self):
        """ Test that the updated field defaults correctly. """
        self.assertTrue(self.booking.updated)