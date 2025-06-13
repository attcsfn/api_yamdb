from django.contrib import admin

from .models import Category, Genre, GenreTitle, Title

admin.site.empty_value_display = 'Не задано'


class GenreInline(admin.TabularInline):
    model = GenreTitle
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'
    extra = 0


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    ordering = ('id',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    ordering = ('id',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    inlines = [
        GenreInline,
    ]
    list_display = (
        'id',
        'name',
        'description',
        'year',
        'get_genre',
        'category',
    )
    list_editable = ("category",)
    search_fields = ('name',)
    list_display_links = ('name',)
    ordering = ('id',)

    def get_genre(self, obj):
        return [genre.name for genre in obj.genre.all()]
