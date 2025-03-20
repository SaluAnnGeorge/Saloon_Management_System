from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Blog
from .forms import BlogForm
from django.contrib import messages

def blog_list(request):
    blogs = Blog.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/blog_detail.html', {'blog': blog})

@login_required
def blog_new(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.published_date = timezone.now()
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog:blog_detail', pk=blog.pk)
    else:
        form = BlogForm()
    return render(request, 'blog/blog_edit.html', {'form': form})

@login_required
def blog_edit(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.user != blog.author and not request.user.is_staff:
        messages.error(request, 'You are not authorized to edit this post!')
        return redirect('blog:blog_detail', pk=pk)
    
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.published_date = timezone.now()
            blog.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog:blog_detail', pk=blog.pk)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blog/blog_edit.html', {'form': form})
