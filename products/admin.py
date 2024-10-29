from django.contrib import admin

from products.models import ProductCategory, Product, Review, TestProduct

admin.site.register(TestProduct)
admin.site.register(ProductCategory)
admin.site.register(Review)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity') # відображаємі поля
    fields = ('image', 'name', 'description', ('price', 'quantity'), 'stripe_product_price_id', 'category') # наявні поля при відкритті
    search_fields = ('name',) # поле по якому буде пошук
    ordering = ('name',)