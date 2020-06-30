from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from mtupdate import views

urlpatterns = [
    path('mtupdate/', views.mtupdate_list),
    path('mtupdate/<int:pk>', views.mtupdate_detail),
    path('mtaccount/', views.mtaccount_list),
    path('mtaccount/<int:pk>', views.mtaccount_detail),

]

urlpatterns = format_suffix_patterns(urlpatterns)

