from django.contrib import admin
from .models import *

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    #title = forms.CharField(widget=forms.Textarea)
    pass

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    pass

@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    pass

@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    pass