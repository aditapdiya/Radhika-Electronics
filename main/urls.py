# urls.py
from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    
    # Cart URLs
    path('add-to-cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:pid>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Order URLs - FIXED: Changed place_order to place_cod_order
    path('place-order/', views.place_cod_order, name='place_order'),  # Keep for backward compatibility
    path('place-cod-order/', views.place_cod_order, name='place_cod_order'),
    path('order-history/', views.order_history, name='order_history'),
    path('order-invoice/<int:order_id>/', views.order_invoice, name='order_invoice'),
    path('invoice/<int:order_id>/pdf/', views.download_invoice_pdf, name='download_invoice_pdf'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Remove Razorpay URLs
    # path('payment-success/', views.payment_success, name='payment_success'),
    # path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
    
    # Product Management
    path('delete-product/<int:id>/', views.delete_product, name="delete_product"),
    path('delete-brand/<int:id>/', views.delete_brand, name="delete_brand"),
    path('delete-category/<int:id>/', views.delete_category, name="delete_category"),
    path('product/update/<int:id>/', views.update_product, name='update_product'),
    path('add-product/', views.add_product, name='add_product'),
    path('product-list/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_details, name='product_details'),
    path('shop/', views.shop, name='shop'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Order Management (Admin)
    path('order-list/', views.order_list, name='order_list'),
    path('update_order/<int:id>/', views.update_order, name='update_order'),
    
    # Password Management
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('changepwd-admin/', views.changepwd_admin, name='changepwd_admin'),
    path('change-password/', views.changepwd_user, name='changepwd_user'),
    
    # Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Category and Brand
    path('add-category/', views.add_category, name='add_category'),
    path('add-brand/', views.add_brand, name='add_brand'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    
    # Feedback
    path('feedback/', views.show_feedback, name='feedback'),
    
    # User Management
    path('user-list/', views.user_list, name="user_list"),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Revenue Reports
    path('revenue-list/', views.revenue_list, name='revenue_list'),
    path('monthly-revenue/', views.monthly_revenue, name='monthly_revenue'),
    path('daily-revenue/', views.daily_revenue, name='daily_revenue'),
]