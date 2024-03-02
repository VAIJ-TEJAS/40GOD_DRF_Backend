from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from inventory import views as inventory_views
from product import views as product_views
from cart import views as cart_views
from order import views as order_views
from user import views as user_views

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
