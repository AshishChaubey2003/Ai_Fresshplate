from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.DonationCreateView.as_view(), name='donation-create'),
    path('my-donations/', views.MyDonationsView.as_view(), name='my-donations'),
    path('all/', views.AllDonationsView.as_view(), name='all-donations'),
    path('<int:pk>/status/', views.UpdateDonationStatusView.as_view(), name='donation-status'),
    path('rescue-centers/', views.RescueCenterListView.as_view(), name='rescue-centers'),
    path('rescue-centers/create/', views.RescueCenterCreateView.as_view(), name='rescue-center-create'),
]