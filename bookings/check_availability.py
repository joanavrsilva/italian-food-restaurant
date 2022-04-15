""" Set up booking slots and check for available tables. """
from datetime import datetime, date, timedelta
from itertools import combinations, chain
from restaurant.models import Table
from .models import Booking


def create_booking_slots(opening_time, closing_time):
    """
    Create a list of 15 minute interval booking slots
    for use in the booking form.
    """
    # Allow bookings from the restaurant opening time.
    current_slot = datetime.combine(date.today(), opening_time)

    # Set final booking to 1 hour before closing time.
    final_slot = datetime.combine(date.today(), closing_time) - timedelta(
        minutes=59)
    slot_interval = timedelta(minutes=15)
    booking_slots = []

    while current_slot < final_slot:
        booking_slots.append(current_slot)
        current_slot += slot_interval

    return [(slot.time(), slot.strftime('%H:%M')) for slot in booking_slots]


def find_tables(selected_date, selected_time, end, party_size, booking_id):
    """
    Search for available tables on the date and time of the required booking.
    """

    # If updating a booking exclude the booking id from the search
    # so that the table will be considered available.

    # Exclude tables whose bookings overlap
    # the start time of the required booking
    if booking_id:
        check1 = Table.objects.exclude(
            bookings__in=Booking.objects.exclude(id=booking_id).filter(
                date=selected_date, time__lt=selected_time,
                end_time__gt=selected_time))
    else:
        check1 = Table.objects.exclude(
            bookings__date=selected_date,
            bookings__time__lt=selected_time,
            bookings__end_time__gt=selected_time)

    # Exclude tables whose bookings overlap
    # the end time of the required booking
    if booking_id:
        check2 = check1.exclude(
            bookings__in=Booking.objects.exclude(id=booking_id).filter(
                date=selected_date, time__lt=end, end_time__gt=end))
    else:
        check2 = check1.exclude(
            bookings__date=selected_date,
            bookings__time__lt=end,
            bookings__end_time__gt=end)

    # Exclude any tables whose bookings span the required booking
    # booking length is fixed at 2 hours so there will be no bookings
    # in the centre of the time range
    if booking_id:
        available_tables = check2.exclude(
            bookings__in=Booking.objects.exclude(id=booking_id).filter(
                date=selected_date, time__lte=selected_time,
                end_time__gte=end))
    else:
        available_tables = check2.exclude(
            bookings__date=selected_date,
            bookings__time__lte=selected_time,
            bookings__end_time__gte=end)

    # If there are any tables left after the checks
    # we need to select one or more for the booking
    if available_tables:
        return select_single_table(available_tables, party_size)


def select_single_table(tables, party_size):
    """
    Check the available tables from the find_tables function
    and see if there is one big enough for the required party size.
    """

    # It is preferred to fulfil the booking will a single table
    # so check for this first
    leftover = 0
    selected_table = ''
    for table in tables:
        # first check for table of exact size
        if table.size == party_size:
            selected_table = table
            return selected_table
        # next try to find the smallest possible table
        elif table.size > party_size:
            spaces_left = table.size - party_size
            if leftover:
                if spaces_left < leftover:
                    leftover = spaces_left
                    selected_table = table
            else:
                leftover = spaces_left
                selected_table = table

    if selected_table:
        return selected_table
    else:
        # if still no table has been found,
        # see if we can combine tables to fit the party size
        return combine_tables(tables, party_size)


def combine_tables(tables, party_size):
    """
    Combine available tables to see if a combined table will
    fit the required party size.
    """

    # With tables only 2 or 4 person in size and party size maximum 8
    # we will only ever need to combine up to 4 tables
    combos2 = combinations(tables, 2)
    combos3 = combinations(tables, 3)
    combos4 = combinations(tables, 4)
    leftover = 0
    combined_tables = ''
    for combo in chain(combos2, combos3, combos4):
        # for each combination of tables calculate combined size
        combined_size = sum([table.size for table in combo])
        # if combined size matches the party size great return the table
        if combined_size == party_size:
            combined_tables = list(combo)
            return combined_tables
        # if there is no exact match return the tables with the
        # least leftover spaces
        elif combined_size > party_size:
            spaces_left = combined_size - party_size
            if leftover:
                if spaces_left < leftover:
                    leftover = spaces_left
                    combined_tables = list(combo)
            else:
                leftover = spaces_left
                combined_tables = list(combo)

    if combined_tables:
        return combined_tables
    # if we have not returned by now there are no tables for the booking