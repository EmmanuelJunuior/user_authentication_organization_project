from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()



class LoginView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            return Response({"user_id": user.id}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    permission_classes = []  # No authentication required

class RegisterView(generics.CreateAPIView):
    authentication_classes = [] 
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            org_name = f"{user.first_name}'s Organisation"
            Organisation.objects.create(name=org_name, description='', users=[user])

            token = RefreshToken.for_user(user)

            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(token.access_token),
                    "user": {
                        "user_id": str(user.id),
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone": user.phone
                    }
                }
            }, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception as e:
            # Log the actual error for debugging
            import traceback
            traceback.print_exc()
            return Response({"error": "Failed to register. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": f"Failed to retrieve organisations: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    lookup_field = 'org_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Organisation.DoesNotExist:
            return Response({"error": "Organisation not found."}, status=status.HTTP_404_NOT_FOUND)
        
class OrganisationCreateView(generics.CreateAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            user = self.request.user
            org = serializer.save()
            org.users.add(user)
            org.save()
        except Exception as e:
            return Response({"error": f"Failed to create organisation: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "id": org.id,
                "name": org.name,
                "description": org.description,
                "users": [{"user_id": user.id, "email": user.email} for user in org.users.all()]
            }
        }, status=status.HTTP_201_CREATED)

class AddUserToOrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            organisation = Organisation.objects.get(id=id)
            user = User.objects.get(id=request.data['user_id'])
            organisation.users.add(user)
            return Response({
                "status": "success",
                "message": "User added to organisation successfully"
            }, status=status.HTTP_200_OK)
        except Organisation.DoesNotExist:
            return Response({
                "status": "Bad Request",
                "message": "Organisation not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "status": "Bad Request",
                "message": "User not found"
            }, status=status.HTTP_400_BAD_REQUEST)