from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import PostForm
from .models import Post, Author
from marketing.models import Singup

def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def get_category_count():
     queryset = Post \
         .objects\
         .values('categories__title') \
         .annotate(Count('categories__title'))
     return queryset

def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method == "POST":
        email = request.POST["email"]
        new_Singup = Singup()
        new_Singup.email = email 
        new_Singup.save()

    context = {
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'index.html', context)

def blog(request):
    most_recent = Post.objects.order_by('-timestamp')[:3]
    category_count = get_category_count()
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginator_queryset = paginator.page(page)
    except PageNotAnInteger:
         paginator_queryset = paginator.page(1)
    except EmptyPage:
         paginator_queryset = paginator.page(paginator.num_pages)

    context = {
         'most_recent': most_recent,
        'queryset': paginator_queryset,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render(request, 'blog.html', context)

def post(request , id):
    post = get_object_or_404(Post, id = id )
    category_count = get_category_count()

    most_recent = Post.objects.order_by('-timestamp')[:3]
    context = {
        'post':post,
        'most_recent': most_recent,
        'category_count': category_count
    }
    return render(request, 'post.html', context)


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)

def post_update(request , id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)

def post_delete(request , id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post-list"))

def search (request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
       queryset = queryset.filter(
          Q(title__icontains=query) |
          Q(overview__icontains=query)
        ).distinct()
    context = {
         'queryset':queryset
     }
    return render(request, 'search.html',context)
