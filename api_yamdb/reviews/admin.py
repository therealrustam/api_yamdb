from django.contrib import admin
from reviews.models import Categories, Genres, Titles


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    list_editable = ('name',)


class GenresAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    list_editable = ('name',)


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description', 'genre', 'category',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name', 'year', 'genre', 'category',)


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Genres, GenresAdmin)
admin.site.register(Titles, TitlesAdmin)
