from itertools import product

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.core.cache import cache

from .documents import ProductDocument
from .forms import ReviewForm, SearchForm
from .models import *
from common.views import TitleMixin


class IndexView(TitleMixin, TemplateView):
    template_name = 'products/index.html'
    title = 'ModaMix'


class ProductsListView(TitleMixin, ListView):
    model = Product
    form_class = SearchForm
    template_name = 'products/products.html'
    context_object_name = 'products'
    paginate_by = 6
    title = 'ModaMix - Товари'

    def get_queryset(self):
        # queryset = super(ProductsListView, self).get_queryset() # Default Product.objects.all()
        category_id = self.kwargs.get('category_id')
        query = self.request.GET.get('query', None)
        cache_key = f'products_category_{category_id}' if category_id else 'all_products'

        products = cache.get(cache_key)
        if not products:
            if query:
                # Perform search using Elasticsearch
                products = ProductDocument.search().query("match", name=query).to_queryset()
            else:
                queryset = super(ProductsListView, self).get_queryset()  # Default Product.objects.all()
                products = queryset.filter(category__id=category_id) if category_id else queryset
                cache.set(cache_key, products, 30)
        return products

        # return queryset.filter(category__id=category_id) if category_id else queryset

    def get_context_data(self, **kwargs):
        context = super(ProductsListView, self).get_context_data()

        context['form'] = self.form_class()

        # context['categories'] = ProductCategory.objects.all()
        context['category_id'] = self.kwargs.get('category_id')

        categories = cache.get('categories')  # шукаємо в кеші данні(редіс), якщо немає йдемо в бд, шукаємо по ключ значенню
        if not categories:
            context['categories'] = ProductCategory.objects.all()
            cache.set('categories', context['categories'], 30)  # кешуємо данні до редісу, по ключу і передаємо значення
        else:
            context['categories'] = categories  # якщо дані були в кеші, то ми в контект поміщаємо данні які були в кеші

        return context


class ProductDetailView(TitleMixin, DetailView):
    model = Product
    template_name = 'products/product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['title'] = f'{self.object.name}'
        context['form'] = ReviewForm()
        context['reviews'] = Review.objects.filter(product=self.object.id)
        return context


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('products:product_info', pk=product_id)  # Перенаправлення на деталі продукту
    else:
        form = ReviewForm()

    return render(request, 'products/product.html', {'product': product, 'form': form})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    product_id = review.product.id
    if review.user == request.user:
        review.delete()
    return redirect('products:product_info', pk=product_id)


@login_required
def basket_add(request, product_id):
    product = Product.objects.get(id=product_id)
    baskets = Basket.objects.filter(user=request.user, product=product)

    if not baskets.exists():
        Basket.objects.create(user=request.user, product=product, quantity=1)
    else:
        basket = baskets.first()
        basket.quantity += 1
        basket.save()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])