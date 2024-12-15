from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.category_list, name='category_list'),
    #path('<int:category_id>/', views.item_list, name='item_list'),
    path('search/', views.search_items, name='search_items'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    
]

urlpatterns += [
    path('register/', views.register, name='register'),
]

urlpatterns += [
    path('login/', auth_views.LoginView.as_view(template_name='catalogue/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += [
    path('profile/', views.profile, name='profile'),
]

urlpatterns += [
    path('item/<int:item_id>/', views.item, name='item'),
]


urlpatterns += [
    path('fetch_cart/', views.fetch_cart, name='fetch_cart'), 
]