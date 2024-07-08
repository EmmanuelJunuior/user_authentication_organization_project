from django.urls import path
from . import views
from .views import home
from .views import create_user, register_user, login_user
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView,  CustomTokenObtainPairView, AddUserToOrganisationView


urlpatterns = [
    path('', home, name='home'),
    path('create_user/', create_user, name='create_user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('organisations/<int:id>/users/', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
]