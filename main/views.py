# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, ProductForm, BrandForm, CategoryForm, OrderForm, FeedbackForm, UserProfileForm
from .models import UserProfile, Product, Category, Brand, Order, OrderItem, Feedback, Wishlist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import render_to_pdf
from django.core.paginator import Paginator
import qrcode
from io import BytesIO
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.dateparse import parse_date
import base64

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models.functions import TruncDate, TruncMonth
from django.db.models import Sum

from django.contrib.auth import get_user_model
User = get_user_model()


def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_products = Product.objects.count()
    total_feedback = Feedback.objects.count()
    recent_orders = Order.objects.order_by('-ordered_at')[:7][::-1] 

    order_dates = [order.ordered_at.strftime("%d-%b") for order in recent_orders]
    order_totals = [float(order.total_amount) for order in recent_orders]

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'order_dates': order_dates,
        'order_totals': order_totals,
        'total_feedback': total_feedback,
    })


@login_required
@staff_member_required
def revenue_list(request):
    orders = Order.objects.select_related('user').all()

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    username = request.GET.get('username')
    filter_type = request.GET.get('filter_type')

    if filter_type == 'daily' and start_date:
        orders = orders.filter(ordered_at__date=parse_date(start_date))

    elif filter_type == 'monthly' and start_date:
        selected_date = parse_date(start_date)
        orders = orders.filter(
            ordered_at__year=selected_date.year,
            ordered_at__month=selected_date.month
        )

    elif filter_type == 'custom':
        if start_date:
            orders = orders.filter(ordered_at__date__gte=parse_date(start_date))
        if end_date:
            orders = orders.filter(ordered_at__date__lte=parse_date(end_date))

    if username:
        orders = orders.filter(user__username__icontains=username)

    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'orders': orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'revenue_list.html', context)

@staff_member_required
def monthly_revenue(request):
    revenue_data = (
        Order.objects.annotate(month=TruncMonth('ordered_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    return render(request, 'monthly_revenue.html', {'revenue_data': revenue_data})

@staff_member_required
def daily_revenue(request):
    revenue_data = (
        Order.objects
        .annotate(date=TruncDate('ordered_at'))
        .values('date')
        .annotate(total=Sum('total_amount'))
        .order_by('-date')
    )

    return render(request, 'daily_revenue.html', {'revenue_data': revenue_data})

@login_required
def user_dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    total_orders = orders.count()
    wishlist_items = Wishlist.objects.filter(user=request.user)
    wishlist_count = wishlist_items.count()
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    last_order_date = orders.first().ordered_at if orders.exists() else None

    # For spending chart
    chart_data = (
        orders.annotate(date=TruncDate('ordered_at'))
        .values('date')
        .annotate(total=Sum('total_amount'))
        .order_by('date')
    )
    order_dates = [item['date'].strftime("%d %b") for item in chart_data]
    order_totals = [float(item['total']) for item in chart_data]

    return render(request, 'user_dashboard.html', {
        'total_orders': total_orders,
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
        'total_spent': total_spent,
        'last_order_date': last_order_date,
        'recent_orders': orders[:5],
        'order_dates': order_dates,
        'order_totals': order_totals,
    })



def index(request):
    categories = Category.objects.all()
    form = FeedbackForm()

    selected_category_id = request.GET.get('category')
    selected_brand_id = request.GET.get('brand')

    products = Product.objects.all()
    brands = Brand.objects.all()

    if selected_category_id:
        products = products.filter(category_id=selected_category_id)
        brands = Brand.objects.filter(category_id=selected_category_id)

    if selected_brand_id:
        products = products.filter(brand_id=selected_brand_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Thank you for your feedback!")
            return redirect('index')  
        else:
            messages.error(request, "❌ Please correct the errors in the form.")

    return render(request, 'index.html', {
        'categories': categories,
        'form': form,
        'products': products,
        'brands': brands,
        'selected_category': int(selected_category_id) if selected_category_id else None,
        'selected_brand': int(selected_brand_id) if selected_brand_id else None,
    })




def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop_by_category.html', {
        'category': category,
        'products': products
    })



def home(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()

    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    if brand_id:
        products = products.filter(brand_id=brand_id)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category': category_id,
    }
    return render(request, 'home.html', context)




@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    total = 0

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        total += product.price * qty

    return render(request, 'checkout.html', {
        'total': total,
    })


@csrf_exempt
@login_required
def place_cod_order(request):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Cart is empty!")
            return redirect('view_cart')

        total = 0
        order = Order.objects.create(
            user=request.user, 
            total_amount=0,
            payment_method='COD',
            status='pending'
        )

        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)
            subtotal = product.price * qty
            total += subtotal

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )
            product.stock -= qty
            product.save()

        order.total_amount = total
        order.save()
        request.session['cart'] = {}

        messages.success(request, "✅ Order placed successfully! You'll pay via Cash on Delivery.")
        return render(request, 'order_success.html', {'order': order})

    return redirect('checkout')


# Add this alias for backward compatibility
@csrf_exempt
@login_required
def place_order(request):
    """Alias for place_cod_order for backward compatibility"""
    return place_cod_order(request)


def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(
                user=user,
                mobile=form.cleaned_data['mobile'],
                address=form.cleaned_data['address']
            )

            messages.success(request, "Registration successful. Please login.")
            form = RegisterForm()
            return render(request, 'register.html', {'form': form})
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')

        try:
            profile = UserProfile.objects.get(mobile=mobile)
            user = authenticate(username=profile.user.username, password=password)

            if user is not None:
                login(request, user)
                # Instead of redirecting immediately, show success modal
                if user.is_superuser:
                    return render(request, 'login.html', {'login_success': True, 'redirect_url': 'admin_dashboard'})
                else:
                    return render(request, 'login.html', {'login_success': True, 'redirect_url': 'index'})
            else:
                return render(request, 'login.html', {'login_failed': True})

        except UserProfile.DoesNotExist:
            return render(request, 'login.html', {'login_failed': True})

    return render(request, 'login.html')


@login_required
def logout_user(request):
    logout(request)
    return redirect('index')

@login_required(login_url='/login/')
def add_to_cart(request, pid):
    if request.user.is_authenticated:
        cart = request.session.get('cart', {})
        cart[str(pid)] = cart.get(str(pid), 0) + 1
        request.session['cart'] = cart
        messages.success(request, '✅ Product added to cart successfully!')
        return redirect('home')
    else:
        messages.error(request, 'Please login to add product to cart')
        return redirect('login')
        

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for pid, quantity in cart.items():
        try:
            product = Product.objects.get(id=pid)
            subtotal = quantity * product.price
            total += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('view_cart')

            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)] = quantity
                request.session['cart'] = cart
                messages.success(request, "Cart updated successfully.")
        except ValueError:
            messages.error(request, "Invalid quantity.")

    return redirect('view_cart')

@login_required
def remove_from_cart(request, pid):
    cart = request.session.get('cart', {})
    pid = str(pid)

    if pid in cart:
        del cart[pid]
        request.session['cart'] = cart
        messages.success(request, "❌ Product removed from cart.")
    else:
        messages.error(request, "Product not found in cart.")

    return redirect('view_cart')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    qr_data = f"Order #{order.id} | ₹{order.total_amount} | {order.ordered_at.strftime('%Y-%m-%d')}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'invoice.html',{
        'order': order,
        'items': items,
        'qr_code': img_str
    })

@login_required
def download_invoice_pdf(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    qr_data = f"Order #{order.id} | ₹{order.total_amount} | {order.ordered_at.strftime('%Y-%m-%d')}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    context ={
        'order': order,
        'items': items,
        'qr_code': img_str,
    }

    return render_to_pdf('invoice_pdf.html', context)

@login_required
def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()        
            return redirect('add_product')
    else:
        form = BrandForm()  

    return render(request, 'add_brand.html', {'form': form})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()        
            return redirect('add_brand')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()        
            return redirect('product_list')
    else:
        form = ProductForm() 
    return render(request, 'add_product.html', {'form': form})


@login_required
def update_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')  
    else:
        form = ProductForm(instance=product)

    return render(request, 'add_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request,id):
    product=get_object_or_404(Product,pk=id)
    product.delete()
    messages.success(request,"Product Deleted Successfully")
    return redirect("home")


@login_required
def delete_brand(request,id):
    brand=get_object_or_404(Brand,pk=id)
    brand.delete()
    return redirect("home")


@login_required
def delete_category(request,id):
    category=get_object_or_404(Category,pk=id)
    category.delete()
    return redirect("home")

@login_required
def show_feedback(request):
    feedback_list = Feedback.objects.all().order_by('-created_at')
    paginator = Paginator(feedback_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'feedback.html', {'feedbacks': page_obj})

@login_required
def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return redirect('wishlist')
    else:
        messages.error(request, 'Please login to add product to cart')
        return redirect('login_user')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')


@login_required
def update_order(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')  
    else:
        form = OrderForm(instance=order)  

    return render(request, 'update_order.html', {'form': form, 'order': order}) 

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-ordered_at') 
    return render(request, 'order_list.html', {'orders': orders})  

@login_required
def changepwd_admin(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password successfully updated!")
            return redirect('changepwd_admin')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})



def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')
    query = request.GET.get('q')
    stock = request.GET.get('stock')  

    if category_id:
        products = products.filter(category_id=category_id)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if query:
        products = products.filter(name__icontains=query)

    if stock == 'out':
        products = products.filter(stock=0)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
    })



def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    search = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if category_id:
        products = products.filter(category_id=category_id)

    if brand_id:
        products = products.filter(brand_id=brand_id)

    if search:
        products = products.filter(name__icontains=search)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'main/shop.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
    })

def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})

@login_required
def product_list_view(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    
    paginator = Paginator(products, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'product_list.html', {
        'page_obj': page_obj,
        'category_id': category_id,
    })



@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': user_profile})


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('edit_profile') 
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
def changepwd_user(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  
            return redirect('user_dashboard') 
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'changepwd_user.html', {'form': form})