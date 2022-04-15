""" Forms for making or updating bookings """
import datetime
from django import forms

from .models import tables_bookings
from .availability import find_tables


class BookingForm(forms.ModelForm):
    """
    A form for making or updating a booking in the restaurant.
    """
    class Meta:
        """ Select the model and define the fields. """
        model = Booking
        fields = ('date', 'time', 'party_size',
                  'name', 'email', 'phone_number', 'special_requirements')

    def __init__(self, slots, booking_id, *args, **kwargs):
        """
        Set the booking time choices, add a calender widget for the
        booking date field and add placeholder text. Also extract the
        current booking id for use in the form validation table search.
        """
        # Get the id for the original booking for use in the table search.
        # If a new booking is being made the id will be an empty string.
        self.form_booking_id = booking_id

        super().__init__(*args, **kwargs)
        self.fields['time'].widget = forms.Select(choices=slots)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['special_requirements'].widget.attrs['placeholder'] = (
            'Let us know of any special dietary or other requirements.')

    def clean(self):
        """
        Custom form validation to check for available tables on the
        booking date and time and raise a validation error if none
        are availale.
        """
        cleaned_data = super().clean()
        planned_date = cleaned_data.get('date')
        planned_time = cleaned_data.get('time')
        planned_party_size = cleaned_data.get('party_size')
        current_booking_id = self.form_booking_id

        # Calculate the end time of the planned booking.
        end = datetime.datetime.combine(
            datetime.date.today(), planned_time) + datetime.timedelta(hours=2)
        booking_end = end.time()

        # Search for avaiable tables using the form parameters.
        tables = find_tables(
            planned_date, planned_time, booking_end, planned_party_size,
            current_booking_id)

        # Make the selected table(s) available to the view or
        # raise a validation error if none available.
        if tables:
            cleaned_data['tables'] = tables
        else:
            raise forms.ValidationError(
                "Sorry no tables available at that time!"
            )

        return cleaned_datas