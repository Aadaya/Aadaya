from django.urls import path

from . import views

urlpatterns = [

    path('register/', views.register, name='register'),
    path('reg1/', views.reg1, name='reg1'),
    path('register1/', views.register1, name='register1'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/', views.dashboard, name='products_by_category'),
    path('wait_for_approval/', views.wait_for_approval, name='wait_for_approval'),
    path('notification/', views.notification, name='notification'),
    path('terms/', views.terms, name='terms'),
    path('change_password/', views.change_password, name='change_password'),
    path('search/', views.search, name='search'),
    path('orders/', views.my_orders, name='orders'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    path('contact_us/', views.contact_us, name='contact_us'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
]
