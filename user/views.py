from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import AddressBook, User
from .serializers import AddressBookSerializer, UserSerializer


class UserRegisterModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    http_method_names = ["post"]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": str(token.user)})


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])

        # Serialize the user object
        user_serializer = UserSerializer(token.user)
        serialized_user = user_serializer.data

        return Response({"token": token.key, "user": serialized_user})
    
class AddressBookViewSet(viewsets.ModelViewSet):
    serializer_class = AddressBookSerializer

    def get_queryset(self):
        return AddressBook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

