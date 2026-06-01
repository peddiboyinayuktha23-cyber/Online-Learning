from django.shortcuts import redirect
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('signup/', views.signup_page, name='signup'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor-dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('about/', lambda request: views.page(request, 'pages/about.html'), name='about'),
    path('contact/', lambda request: views.page(request, 'pages/contact.html'), name='contact'),
    path('instructor/', lambda request: views.page(request, 'pages/instructor.html'), name='instructor'),
    path('search/', lambda request: redirect(f"/courses/?q={request.GET.get('q', '')}"), name='search'),
    path('privacy-policy/', lambda request: views.page(request, 'pages/privacy_policy.html'), name='privacy_policy'),
    path('terms/', lambda request: views.page(request, 'pages/terms.html'), name='terms'),
    path('faq/', lambda request: views.page(request, 'pages/faq.html'), name='faq'),
    path('testimonials/', lambda request: views.page(request, 'pages/testimonials.html'), name='testimonials'),
    path('pricing/', lambda request: views.page(request, 'pages/pricing.html'), name='pricing'),
]
