from django.shortcuts import render, redirect
from .models import Customer
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer, PasswordResetOTP



# def customer_register(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         firstname = request.POST.get('firstname')
#         lastname = request.POST.get('lastname')
#         gender = request.POST.get('gender')
#         email = request.POST.get('email')
#         contactno = request.POST.get('contactno')
#         address = request.POST.get('address')
#         password = request.POST.get('password')
#         confirmpassword = request.POST.get('confirmpassword')

#         if password != confirmpassword:
#             messages.error(request, "Password mismatch")
#             return redirect('customer_register')

#         if Customer.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists")
#             return redirect('customer_register')

#         if Customer.objects.filter(email=email).exists():
#             messages.error(request, "Email already exists")
#             return redirect('customer_register')

#         # ✅ CORRECT WAY
#         Customer.objects.create_user(
#             username=username,
#             password=password,
#             email=email,
#             firstname=firstname,
#             lastname=lastname,
#             gender=gender,
#             contactno=contactno,
#             address=address
#         )

#         messages.success(request, "Registration successful")
#         return redirect('customer_login')

#     return render(request, 'accounts/customer_register.html')


import re
from django.contrib import messages
from django.shortcuts import render, redirect



def customer_register(request):

    if request.method == "POST":

        username = request.POST.get('username', '').strip()
        firstname = request.POST.get('firstname', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        gender = request.POST.get('gender', '').strip()
        email = request.POST.get('email', '').strip()
        contactno = request.POST.get('contactno', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '')
        confirmpassword = request.POST.get('confirmpassword', '')

        errors = []

        # ================= VALIDATIONS =================

        if not all([username, firstname, lastname, gender, email, contactno, password, confirmpassword]):
            errors.append("All fields are required.")

        if not re.match(r'^[A-Za-z0-9_]{4,20}$', username):
            errors.append("Username must be 4-20 characters and contain only letters, numbers, underscore.")

        if not firstname.isalpha():
            errors.append("First name must contain only letters.")

        if not lastname.isalpha():
            errors.append("Last name must contain only letters.")

        if gender not in ["Male", "Female"]:
            errors.append("Invalid gender selection.")

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append("Invalid email format.")

        if not re.match(r'^[6-9]\d{9}$', contactno):
            errors.append("Enter valid 10 digit Indian mobile number.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")

        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number.")

        if not re.search(r'[@$!%*?&]', password):
            errors.append("Password must contain at least one special character.")

        if password != confirmpassword:
            errors.append("Password and Confirm Password do not match.")

        if Customer.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if Customer.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        # ================= STOP IF ERRORS =================

        if errors:
            for error in errors:
                messages.error(request, error)

            return render(request, 'accounts/customer_register.html')

        # ================= CREATE USER =================

        Customer.objects.create_user(
            username=username,
            password=password,
            email=email,
            firstname=firstname,
            lastname=lastname,
            gender=gender,
            contactno=contactno,
            address=address
        )

        messages.success(request, "Registration successful")
        return redirect('customer_login')

    return render(request, 'accounts/customer_register.html')

# def customer_login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)   # 🔥 MAGIC LINE
#             return redirect('home')
#         else:
#             messages.error(request, "Invalid username or password")
#             return redirect('customer_login')

#     return render(request, 'accounts/customer_login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Customer

# #after changes workmigggggg
# def customer_login(request):
#     if request.user.is_authenticated:
#         # Already logged in
#         if not request.user.isadmin and not request.user.is_delivery_person:
#             return redirect('home')
#         else:
#             logout(request)
#             messages.error(request, "You are not a customer. Please login with customer account.")
#             return redirect('customer_login')

#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username=username, password=password)

#         if user and not user.isadmin and not user.is_delivery_person:
#             login(request, user)
#             return redirect('home')
#         elif user:
#             messages.error(request, "This is an admin or delivery account. Use proper login.")
#             return redirect('customer_login')
#         else:
#             messages.error(request, "Invalid username or password")
#             return redirect('customer_login')

#     return render(request, 'accounts/customer_login.html')

# accounts/views.py
def customer_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and not user.isadmin:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('customer_login')
    return render(request, 'accounts/customer_login.html')


def customer_logout(request):
    logout(request)
    request.session.flush()
    return redirect('home')  # home page par redirect


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer, PasswordResetOTP
import re


def customer_forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = Customer.objects.get(
                username=username,
                is_delivery_person=False
            )
        except Customer.DoesNotExist:
            messages.error(request, "Username not found")
            return redirect("customer_forgot_password")

        # Delete old OTPs
        PasswordResetOTP.objects.filter(user=user).delete()

        otp = PasswordResetOTP.generate_otp()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp
        )

        send_mail(
            "Customer Password Reset OTP",
            f"Your OTP is {otp}. It is valid for 5 minutes.",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )

        # 🔥 DO NOT FLUSH SESSION
        request.session["reset_user_id"] = user.id
        request.session["otp_verified"] = False

        messages.success(request, "OTP sent successfully.")
        return redirect("customer_verify_otp")

    return render(request, "accounts/forgot_password_customer.html")


# views.py
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Customer




def customer_verify_otp(request):
    user_id = request.session.get("reset_user_id")

    if not user_id:
        messages.error(request, "Session expired. Please resend OTP.")
        return redirect("customer_forgot_password")

    try:
        user = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect("customer_forgot_password")

    otp_obj = PasswordResetOTP.objects.filter(
        user=user,
        is_used=False
    ).order_by("-created_at").first()

    if not otp_obj:
        messages.error(request, "OTP not found. Please resend.")
        return redirect("customer_forgot_password")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        # 🔥 Backend validation
        if not entered_otp or not entered_otp.isdigit() or len(entered_otp) != 6:
            messages.error(request, "Enter valid 6-digit OTP.")
            return redirect("customer_verify_otp")

        if otp_obj.is_expired():
            messages.error(request, "OTP expired. Please resend.")
            return redirect("customer_verify_otp")

        if otp_obj.attempts >= 3:
            messages.error(request, "Too many attempts. Please resend OTP.")
            return redirect("customer_verify_otp")

        if entered_otp != otp_obj.otp:
            otp_obj.attempts += 1
            otp_obj.save()
            messages.error(request, "Invalid OTP.")
            return redirect("customer_verify_otp")

        # SUCCESS
        otp_obj.is_used = True
        otp_obj.save()

        request.session["otp_verified"] = True
        messages.success(request, "OTP verified successfully.")
        return redirect("customer_reset_password")

    return render(request, "accounts/verify_otp_customer.html")


from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from .models import Customer, PasswordResetOTP


def customer_resend_otp(request):
    user_id = request.session.get("reset_user_id")

    # Session check
    if not user_id:
        messages.error(request, "Session expired. Please start again.")
        return redirect("customer_forgot_password")

    try:
        user = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        messages.error(request, "Invalid session.")
        return redirect("customer_forgot_password")

    # 🔥 Delete all previous OTPs
    PasswordResetOTP.objects.filter(user=user).delete()

    # Generate new OTP
    new_otp = PasswordResetOTP.generate_otp()

    # Create fresh OTP record
    PasswordResetOTP.objects.create(
        user=user,
        otp=new_otp,
        attempts=0,              # reset attempts
        is_used=False
    )

    # Send email
    send_mail(
        subject="New Password Reset OTP",
        message=f"Your new OTP is {new_otp}. It is valid for 5 minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )

    messages.success(request, "New OTP sent successfully.")
    return redirect("customer_verify_otp")


import re

def customer_reset_password(request):
    if not request.session.get("otp_verified"):
        return redirect("customer_login")

    user_id = request.session.get("reset_user_id")

    try:
        user = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        return redirect("customer_login")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("customer_reset_password")

        if (
            len(password) < 8 or
            not re.search(r"\d", password) or
            not re.search(r"[!@#$%^&*]", password)
        ):
            messages.error(request, "Password must be 8+ characters, include number & special character.")
            return redirect("customer_reset_password")

        user.set_password(password)
        user.save()

        request.session.flush()
        messages.success(request, "Password reset successful.")
        return redirect("customer_login")

    return render(request, "accounts/reset_password_customer.html")

