from django.contrib import admin
from .models import Post, Tag, Like, Image


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "caption_preview", "created_at")
    list_filter = ("author", "tags", "created_at")
    search_fields = ("caption", "author_username")
    inlines = [ImageInline]

    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption

admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Image)