from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.views import generic
from datetime import datetime
from django.utils.text import slugify
from django.db.models import F
from django.contrib import messages 
from django.utils.translation import ugettext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator
from .forms import PostForm, PostFormCategory, CommentForm
from .models import Category, Forum, Post, Comment
from .names import names 
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from datetime import date

# forum index, no need to log in to view all topics post
class index(generic.ListView):
    queryset = Category.objects.order_by('id')
    post_list = Category.objects.raw('SELECT * FROM forum_category')
    template_name = 'index_all_categories.html'


# get posts under each topics, just to view, cannot post
def category(request,category_id):
    cat_obj = Category.objects.get(id=category_id)
    forums = Forum.objects.filter(category_id = category_id).order_by('created_on')
    posts = Post.objects.filter(category_id = category_id).order_by('created_on')
    paginator = Paginator(posts, 15)
    
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        posts_display = paginator.page(page)
    except:
        posts_display = paginator.page(paginator.num_pages)

    if len(posts)>=0:
        context_dict = {'category':cat_obj,
                        'forums':forums,
                        'posts': posts_display}
        return render(request, 'each_category.html', context_dict)
    else:
        return render(request,'topic_not_found.html')


# get posts under each sub topics, new post added to topic automatically display
def forum(request, forum_slug):
    
    forum_obj = Forum.objects.get(slug=forum_slug)
    posts = Post.objects.filter(forum_id = forum_obj.id).order_by('created_on')
    paginator = Paginator(posts, 20)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        posts_display = paginator.page(page)
    except:
        posts_display = paginator.page(paginator.num_pages)
    context_dict = {'forum':forum_obj,
                   'posts': posts_display}
    return render(request, 'each_forum.html', context_dict)
   

# view single post, can reply
def post(request, post_id):
    post = Post.objects.get(id = int(post_id))
    comments = Comment.objects.filter(post_id=int(post_id))
    today = date.today().weekday()

    # increment num_views when load post
    Post.objects.filter(id = int(post_id)).update(num_views=F('num_views') + 1)
    post.num_views+=1

    user = request.user

    if request.method == "POST":
        commentForm = CommentForm(request.POST)
        
        if commentForm.is_valid():
            instance = commentForm.save(commit=False)
            
            if user.is_authenticated:
                instance.posted_by_user = user
                instance.posted_by = None
            else:
                instance.posted_by = random.choice(names)
                instance.posted_by_user = None

            instance.post = post
            instance.poster_ip = get_client_ip(request)
            instance.message = commentForm.cleaned_data['message']
            instance.created_on = datetime.now()
            instance.save()

            return redirect('post', post_id= post_id)

        else:
            error = commentForm.errors
            ctx={'post':post, 'comments':comments, 'error': error, 'comment_form':commentForm, 'day':today }
            return render(request, 'single_post.html', ctx)

    else:
        commentForm = CommentForm()

    ctx={'post':post, 'comments':comments, 'comment_form':commentForm, 'day':today }
    return render(request, 'single_post.html', ctx)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# post under sub cateogry
def new_post(request,forum_slug):
    user = request.user
    forum = forum_obj = error = category =""
    form = PostForm()

    if forum_slug:
        forum_obj = Forum.objects.get(slug = forum_slug)

        try: 
            if request.method == "POST":
                form = PostForm(request.POST)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.forum = forum_obj
                    instance.category = forum_obj.category
                    instance.subject = form.cleaned_data['subject']
                    instance.context = form.cleaned_data['context']
                    if user.is_authenticated:
                        instance.posted_by = None
                        instance.posted_by_user = user
                    else:
                        instance.posted_by = random.choice(names)
                        instance.posted_by_user = None
                    instance.poster_ip =  get_client_ip(request)
                    instance.created_on = datetime.now()
                    instance.slug = slugify(form.cleaned_data['subject'])
                    instance.save()
                    return redirect('forum', forum_slug= forum_slug)

        except Exception as e:
            error = e
        
    return render(request, 'new_post.html', {'form': form, 'error': error})


# post under main category, no assigned sub category, create forum when post
def new_post_category(request,category_id):
    user = request.user
    forum  = category =""
 
    if category_id:
        category = Category.objects.get(id = category_id)

        if request.method == "POST":
            form = PostFormCategory(request.POST)
            
            if form.is_valid():
                instance = form.save(commit=False)
                forum_name = request.POST.get('forum')
                forum_existed = Forum.objects.filter(name = forum_name)
                if len(forum_existed) == 0:
                    forum = Forum(name=forum_name, category = category)
                    forum.save()
                else:
                    forum = Forum.objects.get(name = forum_name)

                instance.forum = forum
                instance.category = category
                instance.subject = form.cleaned_data['subject']
                instance.context = form.cleaned_data['context']
                if user.is_authenticated:
                    instance.posted_by = None
                    instance.posted_by_user = user
                else:
                    instance.posted_by = random.choice(names)
                    instance.posted_by_user = None
                instance.poster_ip =  get_client_ip(request)
                instance.created_on = datetime.now()
                instance.slug = slugify(form.cleaned_data['subject'])

                if instance.subject and instance.context:
                    instance.save()

                return redirect('category', category_id= category_id)
            else:
                messages.add_message(request, messages.ERROR, form.errors )
        else:
            form = PostFormCategory()
      
    return render(request, 'publish_post.html', {'form': form})


@login_required
def home(request):
    user = request.user 
    posts = Post.objects.filter(posted_by_user = user)

    return render(request, 'user_profile.html',{ 'posts' : posts})

@login_required
def new_post_by_user(request):
    user = request.user
    forum = error= category = ""

    if request.method == "POST":
        category_name = request.POST.get('category', 'whatever');
        forum_name = request.POST.get('forum', None);
        subject = request.POST['subject']
        context = request.POST['context']
        all_forums = Forum.objects.filter(name = forum_name)
        category = Category.objects.get(name = category_name)
        if len(all_forums) == 0 :
            forum = Forum(name=forum_name, category = category) 
            forum.save()
        else:
            forum = Forum.objects.get(name = forum_name)

        if subject and context:
            post = Post(subject = subject, forum = forum, context = context, posted_by_user = user,
            created_on = datetime.now(), poster_ip = get_client_ip(request), category = category)
            post.save()
            return redirect('category', category_id= category.id)  
        else:
            error ='check your post again!' 

    return render(request, 'user_post.html', {'error':error} )


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('user_home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    error =""
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_home')
            else:
                return render(request, 'user_invalid.html')
        else:
            error ='check your password or username again!' 

    form = AuthenticationForm()
    return render(request, "login.html",{"form":form, 'error': error})

def profile(request):
    user = request.user
    if user.is_authenticated:
        return redirect('user_home')
    return redirect('login')

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


def add_email_and_reset_password(request):
    if request.method == 'POST':
        user_name = request.POST.get('username', None)
        user_email = request.POST.get('email', None)
        associated_user= User.objects.filter(Q(username=user_name))
      
        if not associated_user.exists():
            messages.error(request, 'this username does not exit!')
        else:
            print('user exist')
            user = User.objects.get(username = user_name)
            user.email = user_email
            user.save()
            current_site = get_current_site(request)
            subject = "reset your password for wow"
            message = render_to_string(
                    'registration/password_reset_email.html',
                    {'email': user_email,
                    'user': user,
                    'domain': current_site.domain,
                    'site_name': 'WOW',
                    'protocol':'http',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),            
                    'token': default_token_generator.make_token(user),
                    }
                )
           
            recipient_list = []
            recipient_list.append(user_email)
            send_mail(subject, message , 
                'from@example.com', recipient_list, fail_silently=False, )
            return render(request,'registration/password_reset_done.html')

    return render(request,'registration/password_reset_form.html')


@login_required
def delete_user(request):
    cur_user = request.user
    try:
        u = User.objects.get(username = cur_user.username)
        u.delete()

    except Exception as e: 
        error = e
        return render(request, 'delete.html',{'error':error })
    
    return render(request, 'delete.html')

