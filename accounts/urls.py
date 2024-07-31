from django.urls import path
from .import views


app_name="accounts"

urlpatterns = [

    path('',views.login,name="login"),
    path('change-password/', views.change_password, name='change_password'),
    path('password_reset',views.password_reset_request,name="password_reset"),
    path('password_reset_done',views.password_reset_done,name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/',views.password_reset_confirm,name="password_reset_confirm"),
    path('password_reset_complete/<uidb64>/<token>/',views.password_reset_complete,name="password_reset_complete"),
    path('logout',views.logout,name="logout"),
    ]