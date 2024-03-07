import os
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response

from inventory import views as inventory_views
from product import views as product_views
from cart import views as cart_views
from order import views as order_views
from user import views as user_views

class FileView(APIView):
    def get(self, request):
        file_path = 'EA5319DB112428830A9B5AAC7AA851CE.txt' 
        file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if os.path.exists(file_path):
            file = open(file_path, 'rb')
            response = FileResponse(file)
            return response
        else:
            return Response({'error': 'File not found'}, status=404)
  

router = DefaultRouter()
router.register('signup', user_views.UserRegisterModelViewSet, basename='signup')
router.register('product', product_views.ProductViewSet, basename='product')
router.register('inventory', inventory_views.ProductVariantViewSet, basename='inventory')
router.register('cart-items', cart_views.CartItemViewSet, basename='cart-items')
router.register('order', order_views.OrderViewSet, basename='order')
router.register('address-book', user_views.AddressBookViewSet, basename='address-book')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/', user_views.CustomObtainAuthToken.as_view()),
    path('.well-known/pki-validation/EA5319DB112428830A9B5AAC7AA851CE.txt/', FileView.as_view(), name='file-view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
