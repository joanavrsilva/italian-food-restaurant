from django.db import models
from cloudinary.models import CloudinaryField
import datetime

class Restaurant(models.Model):
    """
    Restaurant model to add information about the restaurant.
    The times will be used to assign available slots for the
    booking system.
    """
    name = models.CharField(max_length=50)
    description = models.TextField(
        blank=True, help_text='Warning editing this field will change the'
        ' About Us section on the home page!'
        ' Clear the field to display the default text.')
    opening_time = models.TimeField(
        auto_now=False, auto_now_add=False, default=datetime.time(11, 00, 00))
    closing_time = models.TimeField(
        auto_now=False, auto_now_add=False, default=datetime.time(23, 00, 00))
    menu = CloudinaryField(
        'image', default='placeholder', use_filename=True,
        help_text='Image of restaurant menu.')

    # Taken from:
    # https://stackoverflow.com/questions/62521421/
    def clean(self):
        if self.closing_time <= self.opening_time:
            raise ValidationError('Closing time should be after opening time!')

    def __str__(self):
        return self.name


class Table(models.Model):
    """
    Table model to add tables of a certain size to the restaurant
    to be used for bookings.
    """

    # Limit to only the most common tables sizes.
    # These can be combined for bigger party sizes.
    TABLE_SIZES = [
        (2, 'Two Person'),
        (4, 'Four Person'),
    ]

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='tables')
    size = models.IntegerField(choices=TABLE_SIZES)

    def __str__(self):
        return f"A table of {self.size} people size"