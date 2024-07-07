"""
URL configuration for user_authentication_organization_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import RegisterView, UserDetailView, OrganisationListView, OrganisationDetailView, OrganisationCreateView, AddUserToOrganisationView, RegisterView, LoginView, CustomTokenObtainPairView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),  # Separate login endpoint
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('api/organisations/', OrganisationListView.as_view(), name='organisation-list'),
    path('api/organisations/<int:id>/', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('api/organisations/create/', OrganisationCreateView.as_view(), name='organisation-create'),
    path('api/organisations/<int:id>/users/', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
]
