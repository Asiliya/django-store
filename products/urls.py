from django.contrib import admin
from django.urls import path

from .views import *

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='index'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_info'),
    path('<int:product_id>/add_review/', add_review, name='add_review'),
    path('<int:review_id>/delete/', delete_review, name='delete_review'),
    path('category/<int:category_id>', ProductsListView.as_view(), name='category'),
    path('page/<int:page>', ProductsListView.as_view(), name='paginator'),
    path('category/<int:category_id>/page/<int:page>/', ProductsListView.as_view(), name='category_page'),
    path('baskets/add/<int:product_id>/', basket_add, name='basket_add'),
    path('baskets/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
]