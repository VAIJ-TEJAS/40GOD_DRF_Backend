from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import ProductVariantSerializer
from .models import ProductVariant

class ProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id is not None:
            return ProductVariant.objects.filter(color__product_id=product_id)
        return ProductVariant.objects.all()