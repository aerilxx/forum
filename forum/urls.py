from django.conf.urls import url, include, re_path
from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (
	PasswordResetConfirmView,PasswordResetCompleteView,
)

category_patterns = [
    url(r'^(?P<category_id>\w+)/$', views.category, name='category'),
    url(r'^(?P<category_id>\w+)/new/$', views.new_post_category, name='post_in_category'),
]
 
post_patterns = [
    url(r'^(?P<post_id>\d+)/$', views.post, name='post'),
]

forum_patterns = [
    url(r'^(?P<forum_slug>[\w-]+)/$', views.forum, name='forum'),
    url(r'^(?P<forum_slug>[\w-]+)/new/$', views.new_post, name='post_in_topic'),
]

user_patterns = [
	url(r'^$', views.home, name='user_home'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^delete/$', views.delete_user, name='delete_account'),
    url(r'^post/$', views.new_post_by_user, name='post_in_profile'),
# override reset password template, add a user name field
    url(r'^password_reset', views.add_email_and_reset_password, name="password_reset"),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView,
        {'template_name': "registration/password_reset_done.html"},
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), 
    	name="password_reset_confirm"),
    path('reset/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.PasswordResetConfirmView,
    #     {'template_name': "registration/password_reset_confirm.html"},
    #     name='password_reset_confirm'),
    # re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView,
    #     {'template_name': "registration/password_reset_complete.html"},
    #     name='password_reset_complete'),    
    ]

urlpatterns = [
    url(r'^$', views.index.as_view(), name='forum_index'),
    url(r'^profile/',include(user_patterns)),
    url(r'^category/', include(category_patterns)),
    url(r'^topic/', include(forum_patterns)),
    url(r'^post/', include(post_patterns)),
]
