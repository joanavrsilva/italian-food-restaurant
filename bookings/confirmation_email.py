""" Confirmation email set-up for bookings made. """
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_confirmation_email(booking):
    """
    Send a booking confirmation email to the customer email
    when a booking is confirmed.
    """
    customer_email = booking.email
    subject = render_to_string(
        'bookings/confirmation_emails/confirmation_email_subject.txt',
        {'booking': booking})
    if booking.customer:
        # If the customer is logged in inform them that they can update
        # or cancel the booking themselves.
        body = render_to_string(
            'bookings/confirmation_emails/confirmation_email_body_user.txt',
            {'booking': booking})
    else:
        body = render_to_string(
            'bookings/confirmation_emails/confirmation_email_body.txt',
            {'booking': booking})

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [customer_email]
    )