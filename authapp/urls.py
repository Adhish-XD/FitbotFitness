from django.urls import path, re_path, include
from authapp import views

urlpatterns = [
    path('',views.home,name="Home"),
    path('signup/',views.signup,name="signup"),
    re_path('^signup$', views.signup),
    path('login',views.handlelogin,name="handlelogin"),
    path('logout',views.handleLogout,name="handleLogout"),
    path('contact/',views.contact,name="contact"),
    path('demographics/', views.demographics, name="demographics"),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('chatbot/', include('Chatbot.urls')),
]
