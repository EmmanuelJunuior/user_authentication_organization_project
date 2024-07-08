from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import User, Organisation
from api.serializers import UserSerializer, OrganisationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from api.serializers import UserSerializer, OrganisationSerializer,CustomTokenObtainPairSerializer

User = get_user_model()

def home(request):
    return render(request, 'index.html')
 
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

class CustomTokenObtainPairView(APIView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.validated_data
        return Response(response_data, status=status.HTTP_200_OK)

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
            organisation = Organisation.objects.create(name=org_name, description='')
            organisation.users.set([user])


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