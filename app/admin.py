from django.contrib import admin
from .models import *

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

@admin.register(Verse)
class LineAdmin(admin.ModelAdmin):
    pass

@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    pass

@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    pass