from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Category, Forum, Post, Comment


admin.site.register(Category)

class ForumAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'num_replies', 'num_posts',)
    list_filter = ('category',)
   
admin.site.register(Forum, ForumAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'forum', 'category','posted_by', 'closed',
        'num_views', 'num_replies', 'created_on' )
    list_filter = ('category','forum','closed')
   
admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post', 'posted_by', 
        'created_on', 'updated_on', )
    search_fields = ('post__subject' ,)
   
    actions = ['delete_model']

    def get_actions(self, request):
        actions = super(CommentAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

# if commet is deleted, update post 
    def delete_model(self, request, obj):
        for o in obj.all():
            post = o.post
            o.delete()
            post.update_state_info()

    delete_model.short_description = 'Delete comments'

admin.site.register(Comment, CommentAdmin)

