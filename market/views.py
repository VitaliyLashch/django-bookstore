import uuid
import difflib
import functools

from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from .models import Book, Category, ActivationLink, Comment
from .forms import FilterSearchForm, SignUpForm, CartForm, CommentForm

# Create your views here.

def adminget(request):
    return redirect('/admin/')
def index_page(request):
    print(request.user.is_superuser)
    return render(
        request,
        "market/index.html",
        dict(
            popular_books=Book.objects.all()[:5],
            categories=[Category.objects.all()[i::3] for i in range(3)],
            super=request.user.is_superuser
        )
    )


def product_page(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if not request.user.is_authenticated:
        is_comment_allowed = False
    else:
        is_comment_allowed = (
            not request.user.comments.filter(book__pk=pk).exists()
            and book in request.user.books.all()
        )
    
    if request.method == "GET" or not is_comment_allowed:
        print(request.user.is_superuser)
        return render(
            request, "market/product.html",
            dict(book=book, is_comment_allowed=is_comment_allowed,
        super=request.user.is_superuser)
        )

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.book = book
        comment.author = request.user
        comment.save()
        if book.score == 0:
            book.score = comment.score
        else:
            book.score = (book.score + comment.score) / 2.0
        book.save()
    
    return redirect("product_page", pk=pk)


def _compute_similarity_score(text1, text2, comp="basic"):
    if comp == "basic":
        text1_set = {word.lower() for word in text1.split()}
        text2_set = {word.lower() for word in text2.split()}
        return len(text1_set & text2_set)
    else:
        return difflib.SequenceMatcher(None, text1, text2).ratio()


def search_page(request):
    books = None
    form = FilterSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get("query")
        maxprice = form.cleaned_data.get("maxprice")
        category_pk = form.cleaned_data.get("category")
        sort = form.cleaned_data.get("sort")
        if category_pk:
            books = Book.objects.filter(categories__pk=category_pk) \
                                .filter(price__lte=maxprice)
        else:
            books = Book.objects.filter(price__lte=maxprice)
        books = list(books)
        if query:
            comp = functools.partial(_compute_similarity_score, query)
            books = [(book, comp(str(book).replace(",", "")))
                     for book in books]
            books.sort(key=lambda book_meta: book_meta[1], reverse=True)
            books = [book_meta[0] for book_meta in books if book_meta[1] > 0.1]
            print()
        if sort == "popularity":
            books.sort(key=lambda book: book.holders_count, reverse=True)
        elif sort == "reviews":
            books.sort(key=lambda book: book.score, reverse=True)
    else:
        raise Http404

    return render(request, "market/search.html", dict(
        books=books,
        form=form,
        super=request.user.is_superuser
    ))


def signup_page(request):
    if request.user.is_authenticated:
        raise Http404
    
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            confirm_link = ActivationLink.objects.create(
                user=user, link=str(uuid.uuid4())
            )
            confirm_link.save()
            user.email_user(
                "Інструкція по підтвердженюю акаунта",
                render_to_string(
                    "market/account_confirm_email.html",
                    dict(
                        token=confirm_link.link,
                        domain=get_current_site(request).domain,
        super=request.user.is_superuser
                    )
                )
            )
            return redirect("confirm_done")
    else:
        form = SignUpForm()

    return render(request, "market/account_sign_up.html", dict(form=form,
        super=request.user.is_superuser))

def confirm_account(request, uuid):
    link = ActivationLink.objects.filter(link=str(uuid)).first()
    if link:
        user = link.user
        link.delete()
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("confirm_success")
        
    return redirect("/")

@login_required
def confirm_success_page(request):
    return render(request, "market/account_confirm_success.html", dict())

def confirm_done_page(request):
    return render(request, "market/account_confirm_done.html", dict())

@login_required
def profile_page(request):
    return render(
        request, "market/profile.html",
        dict(
            books=request.user.books,
            comments=request.user.comments,
        super=request.user.is_superuser
        )
    )

@login_required
def shopping_cart_page(request):
    return render(
        request, "market/shopping_cart.html",
        dict(books=request.user.shopping_cart,
        super=request.user.is_superuser)
    )

@login_required
@require_POST
def shopping_cart_submit(request):
    books = list(request.user.shopping_cart.all())
    request.user.books.add(*books)
    request.user.shopping_cart.clear()
    request.user.save()

    for book in books:
        book.holders_count += 1
        book.save()

    return redirect("shopping_cart")

@login_required
@require_POST
def shopping_cart_add(request):
    form = CartForm(request.POST)
    if not form.is_valid():
        return redirect("/")
    book_pk = form.cleaned_data.get("book_pk")
    try:
        book = Book.objects.get(pk=book_pk)
    except Book.DoesNotExists:
        return redirect("/")

    request.user.shopping_cart.add(book)
    request.user.save()
    return redirect(form.cleaned_data.get("next_link"))

@login_required
@require_POST
def shopping_cart_remove(request):
    form = CartForm(request.POST)
    if not form.is_valid():
        return redirect("/")
    book_pk = form.cleaned_data.get("book_pk")
    try:
        book = Book.objects.get(pk=book_pk)
    except Book.DoesNotExists:
        return redirect("/")

    request.user.shopping_cart.remove(book)
    request.user.save()
    return redirect(form.cleaned_data.get("next_link"))