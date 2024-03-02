from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import CartItemSerializer, POST_CartItemSerializer
from .models import CartItem


class CartItemViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == "POST":
            return POST_CartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
