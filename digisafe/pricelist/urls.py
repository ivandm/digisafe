from django.urls import path, include

from .views import index, PriceListView, PriceCreateView, PriceUpdateView, PriceDeleteView,\
    PriceModalListView, getprice

urlpatterns = [
    path('index/', index, name="index"),
    path('list/', PriceListView.as_view(), name="list"),
    path('create/', PriceCreateView.as_view(), name="create"),
    path('<int:pk>/update/', PriceUpdateView.as_view(), name="update"),
    path('<int:pk>/delete/', PriceDeleteView.as_view(), name="delete"),


    path('modal/list/', PriceModalListView.as_view(), name="modal-list"),
    path('modal/getprice/', getprice, name="modal-getprice"),
]