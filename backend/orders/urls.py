from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/item/<int:pk>/', views.CartItemUpdateView.as_view(), name='cart-item-update'),
    path('place/', views.PlaceOrderView.as_view(), name='place-order'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my-orders'),
    path('my-orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('all/', views.AllOrdersView.as_view(), name='all-orders'),
    path('<int:pk>/status/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
]