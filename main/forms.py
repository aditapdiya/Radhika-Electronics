from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile ,Category ,Brand ,Product ,Order, OrderItem, Feedback
from django.core.exceptions import ValidationError

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'phone', 'message']  
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone Number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}),
        }

#  Register Form
class RegisterForm(UserCreationForm):
    mobile = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter mobile number'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Enter your address'})
    )

    class Meta:
        model = User
        
        fields = ['username', 'first_name', 'last_name','mobile','email', 'address', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        if UserProfile.objects.filter(mobile=mobile).exists():
            raise ValidationError("This mobile number is already registered.")
        return mobile

#  Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model= Product
        fields='__all__'


#  Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields='__all__'



#  Brand Form
class BrandForm(forms.ModelForm):
    class Meta:
        model=Brand
        fields='__all__'

#  Order Form
class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields='__all__'


#  OrderItem Form
class OrderItemForm(forms.ModelForm):
    class Meta:
        model =OrderItem
        fields='__all__'

# Userprofile form 

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mobile', 'address']
        widgets = {
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
