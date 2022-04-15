""" Testcases for the bookings app views. """
import datetime
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from restaurant.models import Restaurant, Table
from .models import Booking


class TestViews(TestCase):
    """ Tests for the views. """
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            'admin', 'admin@email.com', 'adminpassword')
        self.user = User.objects.create_user(
            'john', 'john@email.com', 'johnpassword')

        self.restaurant = Restaurant.objects.create(name='Il oro d'Italia')
        self.table = Table.objects.create(restaurant=self.restaurant, size=2)
        self.table = Table.objects.create(restaurant=self.restaurant, size=4)
        self.booking = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=2, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        self.booking.tables.add(self.table)

    def test_get_make_booking_page(self):
        """ Test the get make booking page view. """
        response = self.client.get('/bookings/make_booking')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/make_booking.html')

    def test_get_booking_confirmed_page(self):
        """ Test the get booking confirmed page view. """
        response = self.client.get(
            f'/bookings/booking_confirmed/{self.booking.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_confirmed.html')

    def test_get_manage_bookings_page(self):
        """ Test the get manage bookings page view. """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get('/bookings/manage_bookings')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/manage_bookings.html')

    def test_get_booking_detail_page(self):
        """ Test the get booking detail page view. """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(
            f'/bookings/booking_detail/{self.booking.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_detail.html')

    def test_get_my_bookings_page(self):
        """ Test the get booking my bookings page view. """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get('/bookings/my_bookings')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/my_bookings.html')

    def test_get_update_booking_page(self):
        """ Test the get update booking page view. """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(
            f'/bookings/update_booking/{self.booking.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/update_booking.html')

    def test_can_delete_booking_user(self):
        """ Test that the delete booking view deletes a booking. """
        # Test for a standard user.
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(
            f'/bookings/delete_booking/{self.booking.id}')
        self.assertRedirects(response, '/bookings/my_bookings')
        existing_bookings = Booking.objects.filter(id=self.booking.id)
        self.assertEqual(len(existing_bookings), 0)

    def test_can_delete_booking_superuser(self):
        """ Test that the delete booking view redirects. """
        # Test the redirect for a superuser
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(
            f'/bookings/delete_booking/{self.booking.id}')
        self.assertRedirects(response, '/bookings/manage_bookings')

    def test_can_toggle_updated(self):
        """
        Test that the toggle updated view changes the value
        of the updated field.
        """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(
            f'/bookings/toggle_updated/{self.booking.id}')
        self.assertRedirects(response, '/bookings/manage_bookings')
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertFalse(updated_booking.updated)

    def test_can_add_table_no(self):
        """
        Test that the add table no view sets the
        table numbers field.
        """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(
            f'/bookings/add_table_no/{self.booking.id}',
            {'table_numbers': '20'})
        self.assertRedirects(response, '/bookings/manage_bookings')
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertEqual(updated_booking.table_numbers, '20')

    def test_the_restaurant_owner_areas_redirect_standard_users(self):
        """
        Test that views that only allow access by a superuser
        redirect a normal user to the homepage.
        """
        # manage bookings
        self.client.login(username='john', password='johnpassword')
        manage = self.client.get('/bookings/manage_bookings', follow=True)
        self.assertRedirects(manage, '/')
        msg_manage = list(manage.context.get('messages'))[0]
        self.assertEqual(
            msg_manage.message, 'Sorry this area is for the restaurant owner.')

        # booking detail
        detail = self.client.get(
            f'/bookings/booking_detail/{self.booking.id}', follow=True)
        self.assertRedirects(detail, '/')
        msg_detail = list(detail.context.get('messages'))[0]
        self.assertEqual(
            msg_detail.message, 'Sorry this area is for the restaurant owner.')

        # toggle updated
        toggle = self.client.get(
            f'/bookings/toggle_updated/{self.booking.id}', follow=True)
        self.assertRedirects(toggle, '/')
        msg_toggle = list(toggle.context.get('messages'))[0]
        self.assertEqual(
            msg_toggle.message, 'Sorry only the restaurant owner can do this.')

        # add table number
        add_no = self.client.post(
            f'/bookings/add_table_no/{self.booking.id}',
            {'table_numbers': '20'}, follow=True)
        self.assertRedirects(add_no, '/')
        msg_add_no = list(add_no.context.get('messages'))[0]
        self.assertEqual(
            msg_add_no.message, 'Sorry only the restaurant owner can do this.')

    def test_can_make_booking(self):
        """ Test that a booking can be made on the make booking view. """
        # If no or standard user.
        response = self.client.post(
            '/bookings/make_booking',
            {
                'date': datetime.date.today(),
                'time': datetime.time(14, 00),
                'party_size': 2,
                'name': 'User Name',
                'email': 'test@email.com',
                'phone_number': '01234567890',
            }, follow=True)
        booking = Booking.objects.get(name='User Name')
        self.assertRedirects(
            response, f'/bookings/booking_confirmed/{booking.id}')
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.message, 'Booking successfully made!')

        response2 = self.client.post(
            '/bookings/make_booking',
            {
                'date': datetime.date.today(),
                'time': datetime.time(11, 00),
                'party_size': 6,
                'name': 'User2 Name',
                'email': 'test@email.com',
                'phone_number': '01234567890',
            }, follow=True)
        booking2 = Booking.objects.get(name='User2 Name')
        self.assertRedirects(
            response2, f'/bookings/booking_confirmed/{booking2.id}')
        message = list(response2.context.get('messages'))[0]
        self.assertEqual(message.message, 'Booking successfully made!')

        # If user is superuser.
        self.client.login(username='admin', password='adminpassword')
        response_su = self.client.post(
            '/bookings/make_booking',
            {
                'date': datetime.date.today(),
                'time': datetime.time(21, 00),
                'party_size': 2,
                'name': 'Test Name',
                'email': 'test@email.com',
                'phone_number': '01234567890',
            }, follow=True)
        self.assertRedirects(response_su, '/bookings/manage_bookings')
        message_su = list(response_su.context.get('messages'))[0]
        self.assertEqual(message_su.message, 'Booking successfully made!')

    def test_can_update_booking(self):
        """
        Test that a booking can be updated with the update booking view.
        """
        # If standard user
        self.client.login(username='john', password='johnpassword')
        self.booking.updated = False
        self.booking.save()
        response = self.client.post(
            f'/bookings/update_booking/{self.booking.id}',
            {
                'date': self.booking.date,
                'time': datetime.time(17, 00),
                'party_size': self.booking.party_size,
                'name': self.booking.name,
                'email': self.booking.email,
                'phone_number': self.booking.phone_number,
            }, follow=True)
        self.assertRedirects(response, '/bookings/my_bookings')
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.message, 'Booking successfully updated.')
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertEqual(updated_booking.time, datetime.time(17, 00))
        self.assertTrue(updated_booking.updated)

        self.booking.updated = False
        self.booking.save()
        response2 = self.client.post(
            f'/bookings/update_booking/{self.booking.id}',
            {
                'date': self.booking.date,
                'time': self.booking.time,
                'party_size': 6,
                'name': self.booking.name,
                'email': self.booking.email,
                'phone_number': self.booking.phone_number,
            }, follow=True)
        self.assertRedirects(response2, '/bookings/my_bookings')
        message2 = list(response2.context.get('messages'))[0]
        self.assertEqual(message2.message, 'Booking successfully updated.')
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertEqual(updated_booking.party_size, 6)
        self.assertTrue(updated_booking.updated)

        # Test redirect if superuser
        self.client.login(username='admin', password='adminpassword')
        self.booking.updated = False
        self.booking.save()
        response_su = self.client.post(
            f'/bookings/update_booking/{self.booking.id}',
            {
                'date': self.booking.date,
                'time': datetime.time(16, 00),
                'party_size': self.booking.party_size,
                'name': self.booking.name,
                'email': self.booking.email,
                'phone_number': self.booking.phone_number,
            }, follow=True)
        self.assertRedirects(response_su, '/bookings/manage_bookings')
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertFalse(updated_booking.updated)

    def test_error_message_generated_when_booking_form_not_valid(self):
        """
        Test the make booking and update booking post views to
        ensure that an error message is generated when the
        booking form is not valid.
        """
        # Make booking
        response = self.client.post(
            '/bookings/make_booking',
            {
                'date': datetime.date.today(),
                'time': datetime.time(14, 00),
                'party_size': 8,
                'name': 'User Name',
                'email': 'test@email.com',
                'phone_number': '01234567890',
            })
        message = list(response.context.get('messages'))[0]
        self.assertEqual(
            message.message,
            'Failed to make the booking. Please check the form.')

        # Update booking
        self.client.login(username='john', password='johnpassword')
        response2 = self.client.post(
            f'/bookings/update_booking/{self.booking.id}',
            {
                'date': self.booking.date,
                'time': self.booking.time,
                'party_size': 8,
                'name': self.booking.name,
                'email': self.booking.email,
                'phone_number': self.booking.phone_number,
            })
        message2 = list(response2.context.get('messages'))[0]
        self.assertEqual(
            message2.message,
            'Failed to update the booking. Please check the form.')