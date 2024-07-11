from django.urls import path
from .views import UserDetailView, OrganisationListView, OrganisationDetailView, OrganisationCreateView

urlpatterns = [
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('organisations/', OrganisationListView.as_view(), name='organisation-list'),
    path('organisations/<int:id>/', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('organisations/create/', OrganisationCreateView.as_view(), name='organisation-create')
]