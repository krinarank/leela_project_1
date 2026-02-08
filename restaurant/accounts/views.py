from django.shortcuts import render, redirect
from .models import Customer
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login




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

        if password != confirmpassword:
            messages.error(request, "Password mismatch")
            return redirect('customer_register')

        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('customer_register')

        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('customer_register')

        # ✅ CORRECT WAY
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


def customer_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)   # 🔥 MAGIC LINE
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('customer_login')

    return render(request, 'accounts/customer_login.html')


def customer_logout(request):
    logout(request)
   # request.session.flush()
    return redirect('home')  # home page par redirect