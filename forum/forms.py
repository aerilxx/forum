from datetime import datetime
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django import forms
from .models import Category, Post, Forum, Comment

# 如果某个topic已经有人发帖可以直接tag

class PostForm(forms.ModelForm):
    # title of the post
    subject = forms.CharField(max_length=500, widget=forms.TextInput(
                                            attrs={'class': 'title',
                                                   'size':'40'}))
    # context of the post
    context = forms.CharField(widget=forms.Textarea(
                                            attrs={'class': 'post_context',
                                                   'rows': '20',
                                                   'cols': '100'}))
    
    class Meta:
        model = Post
        fields = ('subject','context')

    def clean_message(self):
        msg = self.cleaned_data['context']
        forbidden_words = ['fuck','shit','motherfucker']
        for word in forbidden_words:
            word = word.strip()
            if word and word in msg:
                raise forms.ValidationError('Some word in you post is forbidden, please correct it.')
        return msg

    def update_post(self,instance,commit=True):
        for f in instance._meta.fields:
            if f.attname in self.fields:
                setattr(instance,f.attname,self.cleaned_data[f.attname])
        if commit:
            try: 
                instance.save()
            except: 
                return False
        return instance


class PostFormCategory(forms.ModelForm):
    forum = forms.CharField(max_length=100, required=False,
                        widget=forms.TextInput(attrs={'class':'forum',
                            'size':'40'}))
    subject = forms.CharField(max_length=500, widget=forms.TextInput(
                                            attrs={'class': 'title',
                                                   'size':'40'}))
    # context of the post
    context = forms.CharField(widget=forms.Textarea(
                                            attrs={'class': 'post_context',
                                                   'rows': '20','max-height': '100%',
                                                   'cols': '100','max-width': '100%'}))
    
    class Meta:
        model = Post
        fields = ( 'subject','context')

    def clean_forum(self):
        forum = self.cleaned_data['forum']
        check_forum = Forum.objects.filter(name = forum)
        if check_forum.exists():
            raise forms.ValidationError('This topic already exist, please post under the topic page.')
        return forum


    def __init__(self, *args, **kwargs):
        forum = kwargs.pop('forum', None)
        self.forum = forum or getattr(self, 'forum', None)
        super(PostFormCategory, self).__init__(*args, **kwargs)
     


class CommentForm(forms.ModelForm):
    message = forms.CharField(max_length=500, widget=forms.Textarea(
                                            attrs={'rows':"9"}))

    class Meta:
        model = Comment
        fields = ( 'message', )
        

class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(label=("Username"), max_length=254)
    email = forms.CharField(label=("Email"), max_length=254)



