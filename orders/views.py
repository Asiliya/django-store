from http import HTTPStatus

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView
import stripe
from django.conf import settings

from common.views import TitleMixin
from orders.forms import OrderForm
from orders.models import Order
from products.models import Basket, Product

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'ModaMix - Дякуємо за замовлення!'


class CanceledTemplateView(TemplateView):
    template_name = 'orders/canceled.html'

class OrderListView(TitleMixin, ListView):
    template_name = 'orders/orders.html'
    title = 'Store - замовлення'
    queryset = Order.objects.all() # всі закази впринципі, повинно бути сортування по авторизованому юзеру
    context_object_name = 'orders'
    ordering = ('-created')

    def get_queryset(self): # тут і буде сортуватися по авторизованому юзеру
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(DetailView):
    template_name = 'orders/order.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['title'] = f'Store - Замовлення #{self.object.id}'
        return context

class OrderCreateView(TitleMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:order_create')
    title = 'ModaMix - Оформлення заказа'

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data()
        baskets = Basket.objects.filter(user=self.request.user)
        context['baskets'] = baskets
        context['total_sum'] = sum(basket.sum() for basket in baskets)
        context['total_quantity'] = sum(basket.quantity for basket in baskets)
        return context

    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        baskets = Basket.objects.filter(user=self.request.user)
        line_items = []
        for basket in baskets:
            item = {
                'price': basket.product.stripe_product_price_id,
                'quantity': basket.quantity,
            }
            line_items.append(item)

        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            metadata={'order_id': self.object.id}, # передаємо для  вебхука айді товарів
            mode='payment',
            success_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_success')),
            cancel_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_canceled')),
        )
        return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

    def form_valid(self, form):
        form.instance.initiator = self.request.user # обовязкове поле для заповнення в моделі, звязок з юзером
        return super(OrderCreateView, self).form_valid(form)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body # сюди прийде відповідь від страйпа
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if (
        event['type'] == 'checkout.session.completed'
        or event['type'] == 'checkout.session.async_payment_succeeded'
    ):
        fulfill_checkout(event['data']['object']['id'])

    return HttpResponse(status=200)


def fulfill_checkout(session):
    order_id = int(session.metadata.order_id)
    order = Order.objects.get(id=order_id) # беремо обьекти корзини
    order.update_after_payment() # виконуємо функцію після успішної оплати
    print('Fullfill')