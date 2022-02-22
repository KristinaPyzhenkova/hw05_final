from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

VIEW_RECORDS = 10


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, VIEW_RECORDS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте',
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, VIEW_RECORDS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': f'Записи сообщества {group.title}'
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = user.following.filter(user=request.user)
    # following = user.following.filter(user=request.user).exists()
    post_list = user.posts.all()
    num_of_posts = post_list.count()
    paginator = Paginator(post_list, VIEW_RECORDS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'page_obj': page_obj,
        'num_of_posts': num_of_posts,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse(
            'posts:profile', kwargs={'username': request.user}
        ))
    return render(
        request, 'posts/create.html', {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(reverse(
            'posts:post_detail', kwargs={'post_id': post_id}
        ))
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(reverse(
            'posts:post_detail', kwargs={'post_id': post_id}
        ))
    return render(
        request, 'posts/create.html', {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, VIEW_RECORDS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Подписки на авторов',
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follow = get_object_or_404(User, username=username)
    if follow != request.user:
        Follow.objects.get_or_create(user=request.user, author=follow)
    return(redirect('posts:profile', username=username))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return(redirect('posts:profile', username=username))
