from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Customer
from .models import DeliveryPerson
from django.contrib.auth import logout
import random
import time
import re
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import DeliveryVehicle


# ---------------- DELIVERY LOGIN ----------------
# def delivery_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         try:
#             customer = Customer.objects.get(
#                 email=email,
#                 password=password,
#                 is_delivery_person=True
#             )

#             delivery = DeliveryPerson.objects.get(user=customer)

#             request.session['delivery_id'] = delivery.id
#             request.session['delivery_name'] = delivery.fname

#             return redirect('/delivery/dashboard/')
#         except:
#             messages.error(request, "Invalid credentials")

#     return render(request, 'deliverypanel/login.html')


def delivery_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Only username now
        password = request.POST.get('password')

        try:
            # Username thi login check
            customer = Customer.objects.get(
                username=username,
                password=password,
                is_delivery_person=True
            )

            delivery = DeliveryPerson.objects.get(user=customer)

            # Session set karo
            request.session['delivery_id'] = delivery.id
            request.session['delivery_name'] = delivery.fname

            return redirect('/delivery/dashboard/')

        except Customer.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, 'deliverypanel/login.html')

# ---------------- DASHBOARD ----------------
def delivery_dashboard(request):
    if 'delivery_id' not in request.session:
        return redirect('/delivery/login/')

    delivery = DeliveryPerson.objects.get(id=request.session['delivery_id'])

    return render(request, 'deliverypanel/dashboard.html', {
        'delivery': delivery
    })


# ---------------- LOGOUT ----------------
def delivery_logout(request):
    request.session.flush()
    #logout(request)
    return redirect('/delivery/login/')


# ---------------- ADD DELIVERY PERSON (ADMIN) ----------------
def add_delivery_person(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        contact = request.POST['contact']
        address = request.POST['address']

        customer = Customer.objects.create(
            username=username,
            firstname=fname,
            lastname=lname,
            email=email,
            password=password,
            contactno=contact,
            address=address,
            is_delivery_person=True
        )

        DeliveryPerson.objects.create(
            user=customer,
            fname=fname,
            lname=lname,
            email=email,
            contact_no=contact,
            address=address
        )

        messages.success(request, "Delivery Person Added Successfully")
        return redirect('/delivery/add/')

    return render(request, 'deliverypanel/add_delivery_person.html')

# def delivery_forgot_password(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')

#         try:
#             user = Customer.objects.get(
#                 email=email,
#                 is_delivery_person=True
#             )

#             otp = random.randint(100000, 999999)

#             request.session['reset_email'] = email
#             request.session['otp'] = otp

#             send_mail(
#                 'Your OTP for Password Reset',
#                 f'Your OTP is {otp}',
#                 'leelarestaurant.official@gmail.com',
#                 [email],
#                 fail_silently=False
#             )

#             return redirect('verify_otp')

#         except Customer.DoesNotExist:
#             messages.error(request, "Email not found")

#     return render(request, 'deliverypanel/forgot_password.html')

# def verify_otp(request):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
#         session_otp = request.session.get('otp')

#         print("Entered OTP:", entered_otp)
#         print("Session OTP:", session_otp)

#         if session_otp and entered_otp == str(session_otp):
#             return redirect('reset_password')
#         else:
#             messages.error(request, "Invalid OTP")

#     return render(request, 'deliverypanel/verify_otp.html')

# # def reset_password(request):
# #     if request.method == 'POST':
# #         new_pass = request.POST.get('password')
# #         confirm_pass = request.POST.get('confirm_password')

# #         if new_pass == confirm_pass:
# #             user_id = request.session.get('forgot_user')
# #             user = Customer.objects.get(id=user_id)
# #             user.password = new_pass
# #             user.save()

# #             request.session.flush()
# #             messages.success(request, "Password reset successful")
# #             return redirect('delivery_login')
# #         else:
# #             messages.error(request, "Passwords do not match")

# #     return render(request, 'deliverypanel/reset_password.html')


# def reset_password(request):
#     if request.method == 'POST':
#         new_pass = request.POST.get('password')
#         confirm_pass = request.POST.get('confirm_password')

#         if new_pass == confirm_pass:
#             user_id = request.session.get('reset_user_id')

#             if not user_id:
#                 messages.error(request, "Session expired. Try again.")
#                 return redirect('delivery_forgot_password')

#             user = Customer.objects.get(id=user_id)
#             user.set_password(new_pass)
#             user.save()

#             request.session.flush()
#             messages.success(request, "Password reset successful")
#             return redirect('delivery_login')
#         else:
#             messages.error(request, "Passwords do not match")

#     return render(request, 'deliverypanel/reset_password.html')

def delivery_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = Customer.objects.get(email=email, is_delivery_person=True)

            otp = random.randint(100000, 999999)
            request.session['otp'] = str(otp)
            request.session['otp_time'] = time.time()      # ⏱️ timestamp
            request.session['otp_attempts'] = 0             # 🔢 reset attempts
            request.session['reset_user_id'] = user.id  

            request.session['reset_email'] = email
            request.session['reset_user_id'] = user.id   # ⭐ VERY IMPORTANT
            request.session['otp'] = str(otp)

            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP is {otp}',
                'leelarestaurant.official@gmail.com',
                [user.email],
                fail_silently=False
            )
            messages.success(request,"OTP sent to your registered email")
            return redirect('verify_otp')

        except Customer.DoesNotExist:
            messages.error(request, "This Email is not registered.")

    #return render(request, 'deliverypanel/forgot_password.html')
    return render(request, 'accounts/forgot_password.html', {
        'form_action': 'delivery_forgot_password',
        'login_url': 'delivery_login'
    })

# def verify_otp(request):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
#         session_otp = request.session.get('otp')

#         if session_otp and entered_otp == session_otp:
#             return redirect('reset_password')
#         else:
#             messages.error(request, "Invalid OTP")

#     #return render(request, 'deliverypanel/verify_otp.html')
#     return render(request, 'accounts/verify_otp.html', {
#       'verify_url': 'verify_otp'
# })


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        session_otp = request.session.get('otp')
        otp_time = request.session.get('otp_time')
        attempts = request.session.get('otp_attempts', 0)

        # ❌ session missing
        if not session_otp or not otp_time:
            messages.error(request, "Session expired. Please resend OTP.")
            return redirect('verify_otp')

        # ⏱️ EXPIRY CHECK (5 min)
        if time.time() - otp_time > 300:
            del request.session['otp']
            del request.session['otp_time']
            del request.session['otp_attempts']
            messages.error(request, "OTP expired. Please resend OTP.")
            return redirect('verify_otp')

        # 🔢 MAX 3 ATTEMPTS
        if attempts >= 3:
            del request.session['otp']
            del request.session['otp_time']
            del request.session['otp_attempts']
            messages.error(request, "Too many wrong attempts. Please resend OTP.")
            return redirect('verify_otp')

        # ❌ WRONG OTP
        if entered_otp != session_otp:
            request.session['otp_attempts'] = attempts + 1
            messages.error(request, f"Invalid OTP. Attempts left: {2 - attempts}")
            return redirect('verify_otp')

        # ✅ CORRECT OTP
        del request.session['otp']
        del request.session['otp_time']
        del request.session['otp_attempts']
        return redirect('reset_password')

    #return render(request, 'accounts/verify_otp.html')
    return render(request, 'accounts/verify_otp.html', {
       'verify_url': 'verify_otp'
    })

def reset_password(request):
    if request.method == 'POST':
        new_pass = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_password')

        if new_pass != confirm_pass:
            messages.error(request, "Passwords do not match")
            return redirect('reset_password')
        
        # 🔐 PASSWORD STRENGTH CHECK
        if len(new_pass) < 8:
             messages.error(request, "Password must be at least 8 characters long")
             return redirect('reset_password')

        if not re.search(r'\d', new_pass):
            messages.error(request, "Password must contain at least one number")
            return redirect('reset_password')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_pass):
             messages.error(request, "Password must contain at least one special character")
             return redirect('reset_password')


        user_id = request.session.get('reset_user_id')

        if not user_id:
            messages.error(request, "Session expired. Try again.")
            return redirect('delivery_forgot_password')

        user = Customer.objects.get(id=user_id)
        user.password = new_pass   # ✅ plain save (IMPORTANT)
       # user.set_password(new_pass)
        user.save()

        request.session.flush()
        messages.success(request, "Password reset successful")
        return redirect('delivery_login')

    #return render(request, 'deliverypanel/reset_password.html')
    return render(request, 'accounts/reset_password.html', {
      'verify_url': 'reset_password'
})



def resend_otp(request):
    if request.method != 'POST':
        messages.error(request,"Invalid action")
        return redirect('verify_otp')

    user_id = request.session.get('reset_user_id')

    if not user_id:
        messages.error(request, "Session expired. Please start again.")
        return redirect('delivery_forgot_password')

    user = Customer.objects.get(id=user_id)

    otp = random.randint(100000, 999999)

    request.session['otp'] = str(otp)
    request.session['otp_time'] = time.time()   # 🔥 reset 5-min timer
    request.session['otp_attempts'] = 0          # 🔄 reset attempts

    send_mail(
        'Your New OTP',
        f'Your OTP is {otp}',
        'leelarestaurant.official@gmail.com',
        [user.email],
        fail_silently=False
    )

    messages.success(request, "New OTP sent to your email.")
    return redirect('verify_otp')



#workinggggggggggggggggggggggggg
# @login_required
# def delivery_profile(request):
#     # Step 1: Try to fetch any existing DeliveryPerson (without creating new)
#     delivery = DeliveryPerson.objects.first()  # just take the first existing profile
#     msg = None
#     if not delivery:
#         msg = "Profile data not created yet."

#     return render(request, 'deliverypanel/profile.html', {
#         'delivery': delivery,
#         'msg': msg
#     })

# @login_required
# def delivery_profile(request):
#     delivery = None

#     delivery_id = request.session.get('delivery_id')
#     print("SESSION delivery_id:", delivery_id)

#     if delivery_id:
#         delivery = DeliveryPerson.objects.filter(id=delivery_id).first()

#     return render(
#         request,
#         'deliverypanel/profile.html',
#         {'delivery': delivery}
#     )
####workinggggggggggggggggggggggggggggggggggg codeeeeeeeeeeeeeeeee
# def delivery_profile(request):
#     delivery = None
#     delivery_id = request.session.get('delivery_id')

#     if delivery_id:
#         delivery = DeliveryPerson.objects.filter(id=delivery_id).first()

#         if request.method == 'POST' and delivery:
#             if 'profile_image' in request.FILES:
#                 delivery.profile_image = request.FILES['profile_image']
#                 delivery.save()

#     return render(
#         request,
#         'deliverypanel/profile.html',
#         {'delivery': delivery}
#     )

# def delivery_profile(request):
#     delivery = None
#     delivery_id = request.session.get('delivery_id')
#     profile_completion = 0
#     show_image_upload = True

#     if delivery_id:
#         delivery = DeliveryPerson.objects.filter(
#             id=delivery_id
#         ).select_related('user').first()

#         if delivery:
#             # -------- IMAGE UPLOAD --------
#             if request.method == 'POST' and 'profile_image' in request.FILES:
#                 delivery.profile_image = request.FILES['profile_image']
#                 delivery.save()

#             # -------- PROFILE COMPLETION --------
#             total_fields = 6
#             completed = 0

#             if delivery.fname:
#                 completed += 1
#             if delivery.lname:
#                 completed += 1
#             if delivery.email:
#                 completed += 1
#             if delivery.contact_no:
#                 completed += 1
#             if delivery.address:
#                 completed += 1

#             if delivery.profile_image:
#                 completed += 1
#                 show_image_upload = False

#             profile_completion = int((completed / total_fields) * 100)

#     return render(
#         request,
#         'deliverypanel/profile.html',
#         {
#             'delivery': delivery,
#             'profile_completion': profile_completion,
#             'show_image_upload': show_image_upload
#         }
#     )

def delivery_profile(request):
    delivery = None
    delivery_id = request.session.get('delivery_id')

    if delivery_id:
        delivery = DeliveryPerson.objects.select_related('user').filter(id=delivery_id).first()

        # ✅ PROFILE IMAGE UPLOAD (ONLY IF NOT EXISTS)
        if request.method == 'POST' and delivery:
            if not delivery.profile_image and 'profile_image' in request.FILES:
                delivery.profile_image = request.FILES['profile_image']
                delivery.save()

    # ================= PROFILE COMPLETION =================
    completion = 0
    total = 6
    pending = []

    if delivery:
        # 1. Name
        if delivery.fname and delivery.lname:
            completion += 1
        else:
            pending.append("Add full name")

        # 2. Contact
        if delivery.contact_no:
            completion += 1
        else:
            pending.append("Add contact number")

        # 3. Address
        if delivery.address:
            completion += 1
        else:
            pending.append("Add address")

        # 4. Profile Image
        if delivery.profile_image:
            completion += 1
        else:
            pending.append("Upload profile picture")

        # 5. Vehicle
        if hasattr(delivery, 'vehicle'):
            completion += 1
        else:
            pending.append("Add vehicle details")

        # 6. Active Status
        if delivery.is_active:
            completion += 1

    profile_percent = int((completion / total) * 100)

    return render(
        request,
        'deliverypanel/profile.html',
        {
            'delivery': delivery,
            'profile_percent': profile_percent,
            'pending': pending
        }
    )



def delivery_profile_edit(request):
    delivery_id = request.session.get('delivery_id')

    if not delivery_id:
        return redirect('delivery_login')

    delivery = DeliveryPerson.objects.filter(id=delivery_id).first()

    if request.method == 'POST':
        delivery.fname = request.POST.get('fname')
        delivery.lname = request.POST.get('lname')
        delivery.contact_no = request.POST.get('contact_no')
        delivery.address = request.POST.get('address')

        if request.FILES.get('profile_image'):
            delivery.profile_image = request.FILES.get('profile_image')

        delivery.save()
        return redirect('delivery_profile')

    return render(request, 'deliverypanel/profile_edit.html', {'delivery': delivery})

def delivery_change_password(request):
    delivery_id = request.session.get('delivery_id')

    if not delivery_id:
        return redirect('delivery_login')

    delivery = DeliveryPerson.objects.get(id=delivery_id)
    user = delivery.user  # Customer

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # ✅ PLAIN TEXT CHECK
        if user.password != old_password:
            messages.error(request, "Old password is incorrect")
            return redirect('delivery_change_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('delivery_change_password')

        # ✅ SAVE NEW PASSWORD
        user.password = new_password
        user.save()

        request.session.flush()
        messages.success(request, "Password changed. Please login again.")
        return redirect('delivery_login')

    return render(request, 'deliverypanel/change_password.html')

def delivery_vehicle(request):
    delivery_id = request.session.get('delivery_id')
    if not delivery_id:
        return redirect('delivery_login')

    delivery = DeliveryPerson.objects.get(id=delivery_id)
    vehicle = DeliveryVehicle.objects.filter(delivery_person=delivery).first()

    if request.method == 'POST':
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_number = request.POST.get('vehicle_number')

        if vehicle:
            vehicle.vehicle_type = vehicle_type
            vehicle.vehicle_number = vehicle_number
            vehicle.save()
        else:
            DeliveryVehicle.objects.create(
                delivery_person=delivery,
                vehicle_type=vehicle_type,
                vehicle_number=vehicle_number
            )

        return redirect('delivery_profile')

    return render(request, 'deliverypanel/vehicle.html', {
        'vehicle': vehicle
    })