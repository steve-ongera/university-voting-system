# Voting app URLs (voting/urls.py)
from django.urls import path
from . import views


urlpatterns = [
    # Authentication URLs
    path('', views.LoginView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main application URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('results/', views.election_results_view, name='results'),
    
    # Voting URLs
    path('vote/delegate/', views.vote_for_delegate, name='vote_delegate'),
    path('vote/candidate/', views.vote_for_candidate, name='vote_candidate'),

    # Status and information APIs
    path('status/', views.voting_status_api, name='voting_status'),
    path('candidates/', views.candidates_api, name='candidates'),
    path('delegates/', views.delegates_api, name='delegates'),
]
