from django.shortcuts import render, redirect
from .models import Customer
from django.contrib import messages
from django.contrib.auth import logout


# =========================
# CUSTOMER REGISTRATION
# =========================
def customer_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        contactno = request.POST.get('contactno')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        # -------- VALIDATIONS --------

        # firstname & lastname -> only text
        if not firstname.isalpha():
            messages.error(request, "First name ma number allowed nathi")
            return redirect('customer_register')

        if not lastname.isalpha():
            messages.error(request, "Last name ma number allowed nathi")
            return redirect('customer_register')

        # contact number -> only digits
        if not contactno.isdigit():
            messages.error(request, "Contact number ma khali digits j allowed chhe")
            return redirect('customer_register')

        # password match
        if password != confirmpassword:
            messages.error(request, "Password ane Confirm Password same nathi")
            return redirect('customer_register')

        # unique username
        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('customer_register')

        # unique email
        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('customer_register')

        # -------- SAVE CUSTOMER --------
        Customer.objects.create(
            username=username,
            firstname=firstname,
            lastname=lastname,
            gender=gender,
            email=email,
            contactno=contactno,
            address=address,
            password=password,          # (hashing next step ma karishu)
            isadmin=False               # backend only
        )

        messages.success(request, "🎉 Registration Successfully Completed")
        return redirect('customer_login')

    return render(request, 'accounts/customer_register.html')


# =========================
# CUSTOMER LOGIN
# =========================
def customer_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(username=username, password=password)
            request.session['customer_id'] = customer.id
            request.session['customer_username'] = customer.username
            return redirect('home')
        except Customer.DoesNotExist:
            messages.error(request, "Invalid Username or Password")
            return redirect('customer_login')

    return render(request, 'accounts/customer_login.html')


# =========================
# CUSTOMER LOGOUT
# =========================
# def customer_logout(request):
#     request.session.flush()
#     return redirect('customer_login')
def customer_logout(request):
    logout(request)
    return redirect('home')  # home page par redirect