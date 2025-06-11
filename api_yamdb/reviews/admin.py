from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Review, Comment
from api_yamdb.constants import MAX_TEXT_LENGTH


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'author', 'score', 'title', 'pub_date')
    list_filter = ('score', 'pub_date', 'title__category')
    search_fields = ('text', 'author__username', 'title__name')
    readonly_fields = ('author', 'title', 'pub_date')
    date_hierarchy = 'pub_date'
    fieldsets = (
        (None, {'fields': ('title', 'author')}),
        (_('Content'), {'fields': ('text', 'score')}),
        (_('Dates'), {'fields': ('pub_date',)}),
    )

    @admin.display(description=_('Text'))
    def truncated_text(self, obj):
        return format_html(
            '<span title="{}">{}...</span>',
            obj.text, obj.text[:MAX_TEXT_LENGTH]
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and (request.user.is_moderator or request.user.is_admin):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and (request.user.is_moderator or request.user.is_admin):
            return True
        return super().has_delete_permission(request, obj)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'author', 'review_link', 'pub_date')
    list_filter = ('pub_date', 'review__title__category')
    search_fields = ('text', 'author__username', 'review__text')
    readonly_fields = ('author', 'review', 'pub_date')
    date_hierarchy = 'pub_date'
    fieldsets = (
        (None, {'fields': ('review', 'author')}),
        (_('Content'), {'fields': ('text',)}),
        (_('Dates'), {'fields': ('pub_date',)}),
    )

    @admin.display(description=_('Text'))
    def truncated_text(self, obj):
        return format_html(
            '<span title="{}">{}...</span>',
            obj.text, obj.text[:MAX_TEXT_LENGTH]
        )

    @admin.display(description=_('Review'))
    def review_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/reviews/review/{obj.review.id}/change/',
            obj.review.truncated_text()
        )

    def has_change_permission(self, request, obj=None):
        if obj and (request.user.is_moderator or request.user.is_admin):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and (request.user.is_moderator or request.user.is_admin):
            return True
        return super().has_delete_permission(request, obj)
