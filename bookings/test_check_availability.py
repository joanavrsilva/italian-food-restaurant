""" Testcases for the check availability functions """
import datetime
from django.test import TestCase
from restaurant.models import Restaurant, Table
from .models import Booking
from .check_availability import find_tables


class TestCheckAvailability(TestCase):
    """ Tests for the available table searches. """
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name='The Pizza Oven')
        self.table1 = Table.objects.create(restaurant=self.restaurant, size=4)
        self.table2 = Table.objects.create(restaurant=self.restaurant, size=4)
        self.table3 = Table.objects.create(restaurant=self.restaurant, size=2)
        self.table4 = Table.objects.create(restaurant=self.restaurant, size=2)
        self.table5 = Table.objects.create(restaurant=self.restaurant, size=2)
        self.table6 = Table.objects.create(restaurant=self.restaurant, size=4)
        self.table7 = Table.objects.create(restaurant=self.restaurant, size=2)
        self.table8 = Table.objects.create(restaurant=self.restaurant, size=4)

    def test_smallest_single_table_chosen(self):
        """
        Test that the smallest available table is chosen when no table
        combination is required.
        """
        selected_table1 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 1, '')
        self.assertEqual(selected_table1.size, 2)

        selected_table2 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 2, '')
        self.assertEqual(selected_table2.size, 2)

        selected_table3 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 3, '')
        self.assertEqual(selected_table3.size, 4)

        selected_table4 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 4, '')
        self.assertEqual(selected_table4.size, 4)

    def test_smallest_table_combination_chosen(self):
        """
        Test that when the tables are combined the smallest number
        of tables are used and that the combined tables have the
        smallest amount of leftover space.
        """
        selected_tables1 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 5, '')
        tables1_sizes = [table.size for table in selected_tables1]
        self.assertEqual(tables1_sizes, [4, 2])

        selected_tables2 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 8, '')
        tables2_sizes = [table.size for table in selected_tables2]
        self.assertEqual(tables2_sizes, [4, 4])

    def test_other_table_combinations_chosen_when_best_not_available(self):
        """
        Test that when the best table combination is not avaiable
        the next best option is chosen.
        """
        booking1 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=8, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        tables1 = [self.table3, self.table4, self.table5, self.table7]
        booking1.tables.set(tables1)

        booking2 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(12, 00),
            party_size=8, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        tables2 = [self.table1, self.table2]
        booking2.tables.set(tables2)

        booking3 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(12, 00),
            party_size=4, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        booking3.tables.add(self.table6)

        selected_tables1 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 5, '')
        tables1_sizes = [table.size for table in selected_tables1]
        self.assertEqual(tables1_sizes, [4, 4])

        selected_tables2 = find_tables(
            datetime.date.today(), datetime.time(12, 00),
            datetime.time(14, 00), 8, '')
        tables2_sizes = [table.size for table in selected_tables2]
        self.assertEqual(tables2_sizes, [2, 2, 4])

    def test_booked_table_not_selected(self):
        """
        Test to ensure that tables are not double booked.
        """
        booking1 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=8, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        tables1 = [self.table1, self.table2]
        booking1.tables.set(tables1)

        booking2 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=4, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        booking2.tables.add(self.table6)

        selected_table1 = find_tables(
            datetime.date.today(), datetime.time(18, 00),
            datetime.time(20, 00), 3, '')
        self.assertEqual(selected_table1.id, self.table8.id)

        selected_table2 = find_tables(
            datetime.date.today(), datetime.time(17, 00),
            datetime.time(19, 00), 4, '')
        self.assertEqual(selected_table2.id, self.table8.id)

        selected_table3 = find_tables(
            datetime.date.today(), datetime.time(19, 00),
            datetime.time(21, 00), 3, '')
        self.assertEqual(selected_table3.id, self.table8.id)

    def test_booked_table_not_used_in_search_when_updating_booking(self):
        """
        Test that the update booking functionality is working correctly
        and the booked table is excluded from any search and so not
        assumed to be unavailable.
        """
        booking1 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=8, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        tables1 = [self.table1, self.table2]
        booking1.tables.set(tables1)

        booking2 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=8, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        tables2 = [self.table6, self.table8]
        booking2.tables.set(tables2)

        booking3 = Booking.objects.create(
            date=datetime.date.today(), time=datetime.time(18, 00),
            party_size=4, name='Test Name', email='test@email.com',
            phone_number='01234567890')
        tables3 = [self.table3, self.table4]
        booking3.tables.set(tables3)

        selected_table = find_tables(
            datetime.date.today(), datetime.time(19, 00),
            datetime.time(21, 00), 8, booking1.id)
        self.assertIsNotNone(selected_table)

