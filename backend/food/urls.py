from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('items/', views.FoodItemListView.as_view(), name='food-list'),
    path('items/<int:pk>/', views.FoodItemDetailView.as_view(), name='food-detail'),
    path('items/create/', views.FoodItemCreateView.as_view(), name='food-create'),
    path('items/<int:pk>/update/', views.FoodItemUpdateDeleteView.as_view(), name='food-update'),
    path('rescue/', views.RescueFoodListView.as_view(), name='rescue-food'),
]