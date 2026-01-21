from django.shortcuts import render,redirect
from adminpanel.models import FoodItemCategory, FoodItemSubCategory, FoodItem, FoodItemImage
from django.contrib import messages
from .models import Inquiry


from adminpanel.models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem
)

from django.shortcuts import render

def home(request):
    return render(request, 'menu/home.html')

def menu_page(request):
   categories = FoodItemCategory.objects.prefetch_related(
        'fooditemsubcategory_set__fooditem_set__images'
    )

   return render(request, 'menu/menu.html', {
        'categories': categories
    })

def about(request):
    return render(request, 'menu/about.html')

def contact(request):
    return render(request, 'menu/contact.html')

# def contact_view(request):
#     if request.method == "POST":
#         Inquiry.objects.create(
#             subject=request.POST['subject'],
#             message=request.POST['message'],
#             user=request.user if request.user.is_authenticated else None
#         )
#         messages.success(request, "Your message has been sent successfully!")
#         return redirect('contact')  # page reload

#     return render(request, 'menu/contact.html')



def contact_view(request):
    if request.method == "POST":
        # POST data read correctly
        name = request.POST.get('name')  # optional, store in user or ignore
        email = request.POST.get('email')  # optional
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Save in DB
        Inquiry.objects.create(
            subject=subject,
            message=message,
            user=request.user if request.user.is_authenticated else None
        )

        # Success message
        messages.success(request, "Your message has been sent successfully!")

        # Redirect to same page (important for messages to appear)
        return redirect('contact')

    return render(request, 'menu/contact.html')