""" Views for the bookings app. """
import datetime
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from restaurant.models import Restaurant
from .models import Booking
from .forms import BookingForm
from .check_availability import create_booking_slots
from .confirmation_email import send_confirmation_email


def make_booking(request):
    """
    Display the booking form and make a booking.
    """
    restaurant = Restaurant.objects.get(name="Il oro d'Italia")
    # Create time slots between restaurant opening and closing
    # for the booking form time selection.
    slots = create_booking_slots(
        restaurant.opening_time, restaurant.closing_time)

    # Set a null booking id for the search for available tables
    # The current booking id will be used when updating a booking
    booking_id = ''

    if request.method == 'POST':
        booking_form = BookingForm(slots, booking_id, data=request.POST)
        if booking_form.is_valid():
            # Get the selected available table(s)
            tables = booking_form.cleaned_data['tables']
            booking = booking_form.save()

            # Add the selected table(s) to the booking
            if isinstance(tables, list):
                booking.tables.set(tables)
            else:
                booking.tables.add(tables)
            if request.user.is_authenticated:
                booking.customer = request.user
                booking.save()
            send_confirmation_email(booking)
            messages.success(request, 'Booking successfully made!')

            # Assign the redirect based on who is making the booking
            if request.user.is_superuser:
                return redirect('manage_bookings')
            else:
                return redirect(reverse(
                    'booking_confirmed', args=[booking.id]))
        else:
            messages.error(
                request, 'Failed to make the booking. Please check the form.')
    else:
        booking_form = BookingForm(slots, booking_id)

    context = {
        'booking_form': booking_form,
    }

    return render(request, 'bookings/make_booking.html', context)


def booking_confirmed(request, booking_id):
    """
    Confirm a successful booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    context = {
        'booking': booking,
    }

    return render(request, 'bookings/booking_confirmed.html', context)


@login_required
def manage_bookings(request):
    """
    List current and future bookings for the restaurant owner.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry this area is for the restaurant owner.')
        return redirect('home')

    bookings = Booking.objects.filter(date__gte=datetime.date.today())
    context = {
        'bookings': bookings
    }
    return render(request, 'bookings/manage_bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    Display the details of an individual booking for the restaurant owner.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry this area is for the restaurant owner.')
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)

    context = {
        'booking': booking,
    }

    return render(request, 'bookings/booking_detail.html', context)


@login_required
def add_table_no(request, booking_id):
    """
    Allow the restaurant owner to add table numbers to the saved bookings.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry only the restaurant owner can do this.')
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        table_numbers = request.POST.get('table_numbers')
        booking.table_numbers = table_numbers
        booking.save()
        return redirect('manage_bookings')


@login_required
def toggle_updated(request, booking_id):
    """
    Allow the restaurant owner to change the value of the updated field
    of the Booking model.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry only the restaurant owner can do this.')
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)
    booking.updated = not booking.updated
    booking.save()
    return redirect('manage_bookings')


@login_required
def my_bookings(request):
    """
    List the current and future bookings created by the logged in user.
    """
    customer_bookings = Booking.objects.filter(
        customer__isnull=False, customer=request.user.id)
    bookings = customer_bookings.filter(date__gte=datetime.date.today())

    context = {
        'bookings': bookings
    }

    return render(request, 'bookings/my_bookings.html', context)


@login_required
def update_booking(request, booking_id):
    """
    Allow the logged in user to make changes to an existing booking.
    """
    restaurant = Restaurant.objects.get(name="Il oro d'Italia")
    # Create time slots between restaurant opening and closing
    # for the booking form time selection.
    slots = create_booking_slots(
        restaurant.opening_time, restaurant.closing_time)

    # Get the current booking
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking_form = BookingForm(
            slots, booking_id, data=request.POST, instance=booking)
        if booking_form.is_valid():
            # If only the customer information has changed
            # save the form without updating the booked tables
            if ('date' not in booking_form.changed_data and
                    'time' not in booking_form.changed_data and
                    'party_size' not in booking_form.changed_data):
                booking_form.save()
                # Assign the redirect based on who is making the booking
                if request.user.is_superuser:
                    messages.success(request, 'Booking successfully updated.')
                    return redirect('manage_bookings')
                else:
                    # Set the upated flag so the restaurant owner knows the
                    # booking has been changed
                    booking.updated = True
                    booking.save()
                    messages.success(request, 'Booking successfully updated.')
                    return redirect('my_bookings')
            else:
                # If the booking information has changed remove original tables
                # and add the newly selected tables to the booking
                tables = booking_form.cleaned_data['tables']
                booking.tables.clear()
                booking.table_numbers = ''
                if isinstance(tables, list):
                    booking_form.save()
                    booking.tables.set(tables)
                else:
                    booking_form.save()
                    booking.tables.add(tables)
                # Assign the redirect based on who is making the booking
                if request.user.is_superuser:
                    messages.success(request, 'Booking successfully updated.')
                    return redirect('manage_bookings')
                else:
                    # Set the upated flag so the restaurant owner knows the
                    # booking has been changed
                    booking.updated = True
                    booking.save()
                    messages.success(request, 'Booking successfully updated.')
                    return redirect('my_bookings')
        else:
            messages.error(
                request,
                'Failed to update the booking. Please check the form.')
    else:
        booking_form = BookingForm(slots, booking_id, instance=booking)

    context = {
        'booking_form': booking_form,
        'booking': booking
    }
    return render(request, 'bookings/update_booking.html', context)


@login_required
def delete_booking(request, booking_id):
    """
    Allow the logged in user to cancel and delete a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, 'Booking cancelled!')
    if request.user.is_superuser:
        return redirect('manage_bookings')
    else:
        return redirect('my_bookings')
