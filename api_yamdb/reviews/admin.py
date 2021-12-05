from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from reviews.models import Category, Genre, Title


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ['email', 'username', 'role', 'is_active']
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    list_editable = ('name',)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    list_editable = ('name',)


class TitleAdmin(admin.ModelAdmin):
    #list_display = ('pk', 'name', 'year', 'description', 'genre', 'category',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
   # list_filter = ('name', 'year', 'genre', 'category',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
