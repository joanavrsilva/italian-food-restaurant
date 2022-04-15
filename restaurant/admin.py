""" Admin panel set-up for the restaurant app. """
from django.contrib import admin
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import Restaurant, Table


# Remove unrequired models from the admin panel.
#admin.site.unregister(Site)
#admin.site.unregister(SocialAccount)
#admin.site.unregister(SocialToken)
#admin.site.unregister(SocialApp)

# Disable delete action for the site
admin.site.disable_action('delete_selected')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    Admin options for the Restaurant model.
    """
    # Pizza oven restaurant name is used in some of the templates
    # so ensure it cannot be changed in the admin.
    readonly_fields = ('name',)

    list_display = ('name', 'opening_time', 'closing_time')
    search_fields = ('name',)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """
    Admin options for the Table model.
    """
    list_display = ('size', 'restaurant')
    ordering = ('size',)
    list_filter = ('size',)
    # Enable delete action for this model
    actions = ['delete_selected']