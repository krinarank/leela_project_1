from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from accounts.models import Customer
from location.models import State, City, Area
from deliverypanel.models import DeliveryPerson
from django.contrib.auth import get_user_model
from purchase.models import Supplier
import requests
from django.shortcuts import render, redirect
from .forms import NotificationForm
from adminpanel.models import Notification


from django.db.models import Sum
from deliverypanel.models import DeliveryPerson 
from django.core.paginator import Paginator
from django.db.models import Q

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from location.models import State, City, Area
from django.contrib.auth.decorators import login_required
from .models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem,
    FoodItemImage,
    
)
from menu.models import Inquiry
from purchase.models import Ingredient
from purchase.models import Purchase 


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid credentials'})

    return render(request, 'auth/login.html')

@login_required
def admin_menu_view(request):
    categories = FoodItemCategory.objects.all()
    return render(request, 'adminpanel/admin_menu.html', {
        'categories': categories
    })

from .models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem,
    FoodItemImage
)

@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name').strip()

        # Numeric check
        if category_name.isnumeric():
            messages.error(request, "Category name cannot be numeric")
            return redirect('add_category')

        # Duplicate check
        if FoodItemCategory.objects.filter(category_name__iexact=category_name).exists():
            messages.error(request, f"Category '{category_name}' already exists")
            return redirect('add_category')

        # Create category
        FoodItemCategory.objects.create(category_name=category_name)
        messages.success(request, "Food category added successfully")
        return redirect('add_category')

    categories = FoodItemCategory.objects.all()
    return render(request, 'add/add_category.html', {'categories': categories})



@login_required
def add_subcategory(request):
    if request.method == 'POST':
        subcategory_name = request.POST.get('subcategory_name', '').strip()
        category_id = request.POST.get('category_id')

        # Check if subcategory name is empty
        if not subcategory_name:
            messages.error(request, "Subcategory name cannot be empty")
            return redirect('add_subcategory')

        # Numeric check
        if subcategory_name.isnumeric():
            messages.error(request, "Subcategory name cannot be numeric")
            return redirect('add_subcategory')

        # Category selection check
        if not category_id:
            messages.error(request, "Please select a parent category")
            return redirect('add_subcategory')

        # Duplicate check (case-insensitive) under the same category
        if FoodItemSubCategory.objects.filter(
            subcategory_name__iexact=subcategory_name,
            food_item_cat_id=category_id
        ).exists():
            messages.error(request, f"Subcategory '{subcategory_name}' already exists in this category")
            return redirect('add_subcategory')

        # Create subcategory
        FoodItemSubCategory.objects.create(
            subcategory_name=subcategory_name,
            food_item_cat_id=category_id
        )
        messages.success(request, "Subcategory added successfully")
        return redirect('add_subcategory')

    # GET request
    subcategories = FoodItemSubCategory.objects.select_related('food_item_cat').all()
    categories = FoodItemCategory.objects.all()
    return render(request, 'add/add_subcategory.html', {
        'subcategories': subcategories,
        'categories': categories
    })
# ---------------- ADD FOOD ITEM ----------------

@login_required
def add_fooditem(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price')
        calories = request.POST.get('calories')
        is_available = request.POST.get('is_available') == 'on'
        is_special = request.POST.get('is_special') == 'on'  

        # 1️⃣ Required field check
        if not all([category_id, subcategory_id, name, price, calories]):
            messages.error(request, "All fields are required")
            return redirect('add_fooditem')

        # 2️⃣ Name cannot be numeric
        if name.isnumeric():
            messages.error(request, "Food item name cannot be numeric")
            return redirect('add_fooditem')

        # 3️⃣ Category & subcategory existence check
        category = get_object_or_404(FoodItemCategory, id=category_id)
        subcategory = get_object_or_404(FoodItemSubCategory, id=subcategory_id, food_item_cat=category)

        # 4️⃣ Duplicate check (same subcategory)
        if FoodItem.objects.filter(name__iexact=name, sub_cat=subcategory).exists():
            messages.error(request, f"'{name}' already exists in this subcategory")
            return redirect('add_fooditem')

        # 5️⃣ Price & calories validation
        try:
            price = float(price)
            if price <= 0:
                messages.error(request, "Price must be greater than zero")
                return redirect('add_fooditem')
        except ValueError:
            messages.error(request, "Invalid price")
            return redirect('add_fooditem')

        try:
            calories = int(calories)
            if calories <= 0:
                messages.error(request, "Calories must be greater than zero")
                return redirect('add_fooditem')
        except ValueError:
            messages.error(request, "Invalid calories")
            return redirect('add_fooditem')

        # ✅ Create food item
        FoodItem.objects.create(
            name=name,
            price=price,
            calories=calories,
            is_available=is_available,
            is_special=is_special,
            sub_cat=subcategory
        )

        messages.success(request, "Food item added successfully")
        return redirect('add_fooditem')

    # GET request
    fooditems = FoodItem.objects.select_related('sub_cat__food_item_cat').all()
    categories = FoodItemCategory.objects.all()
    subcategories = FoodItemSubCategory.objects.all()

    return render(request, 'add/add_fooditem.html', {
        'fooditems': fooditems,
        'categories': categories,
        'subcategories': subcategories
    })


# ---------------- UPDATE FOOD ITEM ----------------
# def update_fooditem(request, id):
#     item = get_object_or_404(FoodItem, id=id)
#     subcategories = FoodItemSubCategory.objects.all()

#     if request.method == 'POST':
#         item.name = request.POST.get('name')
#         item.price = request.POST.get('price')
#         item.calories = request.POST.get('calories')
#         item.is_available = True if request.POST.get('is_available') == 'on' else False
#         item.is_special = request.POST.get('is_special') == 'on' 
#         item.sub_cat_id = request.POST.get('subcategory_id')
#         item.save()

#         # ✅ SHOW message on the same page
#         messages.success(request, "Food item updated successfully")
#         # Don't redirect to add_fooditem
#         return redirect('update_fooditem', id=item.id)

#     return render(request, 'update/update_fooditem.html', {
#         'fooditem': item,
#         'subcategories': subcategories
#     })
def update_fooditem(request, id):
    item = get_object_or_404(FoodItem, id=id)
    subcategories = FoodItemSubCategory.objects.all()

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.price = request.POST.get('price')
        item.calories = request.POST.get('calories')
        item.is_available = request.POST.get('is_available') == 'on'
        item.is_special = request.POST.get('is_special') == 'on'
        item.sub_cat_id = request.POST.get('subcategory_id')
        item.save()

        return redirect(f'/dashboard/update-fooditem/{item.id}/?success=1')

    return render(request, 'update/update_fooditem.html', {
        'fooditem': item,
        'subcategories': subcategories
    })

# ---------------- DELETE FOOD ITEM ----------------
def delete_fooditem(request, id):
    item = get_object_or_404(FoodItem, id=id)
    item.delete()
    messages.success(request, "Food item deleted successfully")
    return redirect('add_fooditem')

# ---------------- ADD + LIST FOOD IMAGE ----------------

def add_foodimage(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_item')
        image = request.FILES.get('img_url')

        if food_id and image:

            # -------- FILE TYPE VALIDATION --------
            allowed_types = ['image/jpeg', 'image/png']
            if image.content_type not in allowed_types:
                messages.error(request, "Only JPG ,JPEG and PNG images are allowed.")
                return redirect('add_foodimage')

            # -------- FILE SIZE VALIDATION (1MB) --------
            if image.size > 1024 * 300:
                messages.error(request, "Image size must be under 300 kb.")
                return redirect('add_foodimage')

            food = get_object_or_404(FoodItem, id=food_id)

            # Duplicate check
            if FoodItemImage.objects.filter(food_item=food).exists():
                messages.error(request, "This food item already has an image!")
                return redirect('add_foodimage')

            FoodItemImage.objects.create(
                food_item=food,
                img_url=image
            )
            messages.success(request, "Image uploaded successfully")
            return redirect('add_foodimage')

    images = FoodItemImage.objects.select_related(
        'food_item',
        'food_item__sub_cat',
        'food_item__sub_cat__food_item_cat'
    )

    food_items = FoodItem.objects.exclude(
        id__in=FoodItemImage.objects.values_list('food_item_id', flat=True)
    )

    return render(request, 'add/add_foodimage.html', {
        'food_items': food_items,
        'images': images
    })

# ---------------- UPDATE FOOD IMAGE ----------------
# def update_foodimage(request, id):
#     image = get_object_or_404(FoodItemImage, id=id)
#     food_items = FoodItem.objects.all()

#     if request.method == 'POST':
#         food_id = request.POST.get('food_item')
#         new_image = request.FILES.get('img_url')

#         image.food_item_id = food_id

#         if new_image:
#             image.img_url = new_image

#         image.save()
#         messages.success(request, "Food image updated successfully")
#         return redirect('update_foodimage', id=image.id)

#     return render(request, 'update/update_foodimage.html', {
#         'image': image,
#         'food_items': food_items
#     })

def update_foodimage(request, id):
    image = get_object_or_404(FoodItemImage, id=id)
    food_items = FoodItem.objects.all()

    if request.method == 'POST':
        food_id = request.POST.get('food_item')
        new_image = request.FILES.get('img_url')

        image.food_item_id = food_id

        if new_image:
            image.img_url = new_image

        image.save()

        return redirect(f'/dashboard/update-foodimage/{image.id}/?success=1')


    return render(request, 'update/update_foodimage.html', {
        'image': image,
        'food_items': food_items
    })


# ---------------- DELETE FOOD IMAGE ----------------
def delete_foodimage(request, id):
    image = get_object_or_404(FoodItemImage, id=id)
    image.delete()
    messages.success(request, "Image deleted successfully")
    return redirect('add_foodimage')


def logout_view(request):
    logout(request)  # clears session
    return redirect('login')  # go back to login page


def delete_category(request, id):
    category = get_object_or_404(FoodItemCategory, id=id)
    category.delete()
    return redirect('add_category')

# def update_category_page(request, category_id):
#     category = get_object_or_404(FoodItemCategory, id=category_id)

#     if request.method == "POST":
#         new_name = request.POST.get('category_name')
#         if new_name:
#             category.category_name = new_name
#             category.save()
#             messages.success(request, "Category updated successfully!")
#             return redirect('update_category', category_id=category.id)
#         else:
#             messages.error(request, "Please enter a category name.")

#     context = {
#         'category': category
#     }
#     return render(request, 'update/update_category.html', context)

def update_category_page(request, category_id):
    category = get_object_or_404(FoodItemCategory, id=category_id)

    if request.method == "POST":
        new_name = request.POST.get('category_name')
        if new_name:
            category.category_name = new_name
            category.save()

            return redirect(f'/dashboard/update-category/{category.id}/?success=1')
        else:
            return render(request, 'update/update_category.html', {
                'category': category,
                'error': "Please enter category name"
            })

    return render(request, 'update/update_category.html', {'category': category})

# #update subcategory
# def update_subcategory(request, id):
#     sub = get_object_or_404(FoodItemSubCategory, id=id)
#     categories = FoodItemCategory.objects.all()

#     if request.method == 'POST':
#         sub.subcategory_name = request.POST.get('subcategory_name')

#         cat_id = request.POST.get('food_item_cat')
#         sub.food_item_cat = FoodItemCategory.objects.get(id=cat_id)

#         sub.save()

#         messages.success(request, "Subcategory updated successfully")

#         return render(request, 'update/update_subcategory.html', {
#             'sub': sub,
#             'categories': categories
#         })

#     return render(request, 'update/update_subcategory.html', {
#         'sub': sub,
#         'categories': categories
#     })

def update_subcategory(request, id):
    sub = get_object_or_404(FoodItemSubCategory, id=id)
    categories = FoodItemCategory.objects.all()

    if request.method == 'POST':
        sub.subcategory_name = request.POST.get('subcategory_name')
        cat_id = request.POST.get('food_item_cat')
        sub.food_item_cat = FoodItemCategory.objects.get(id=cat_id)
        sub.save()

        return redirect(f'/dashboard/update-subcategory/{sub.id}/?success=1')

    # VERY IMPORTANT (GET request mate return)
    return render(request, 'update/update_subcategory.html', {
        'sub': sub,
        'categories': categories
    })


# Delete subcategory
from django.contrib import messages

def delete_subcategory_item(request, id):
    try:
        sub = FoodItemSubCategory.objects.get(id=id)
        sub.delete()
        messages.success(request, "Subcategory deleted successfully")
    except FoodItemSubCategory.DoesNotExist:
        messages.warning(request, "Subcategory already deleted or not found")

    return redirect('add_subcategory')

@login_required
def admin_inquiry_list(request):
    inquiries = Inquiry.objects.all().order_by('-inquiry_date')
    return render(request, 'adminpanel/inquiry_list.html', {
        'inquiries': inquiries
    })


def reply_inquiry(request, id):
    #inquiry = Inquiry.objects.get(id=id)
    inquiry = get_object_or_404(Inquiry, inquiry_id=id)


    if request.method == "POST":
        reply_msg = request.POST.get("reply")

        inquiry.admin_reply = reply_msg
        inquiry.status = "Responded"
        inquiry.save()

        return redirect('admin_inquiry_list')

    return render(request, 'adminpanel/reply_inquiry.html', {
        'inquiry': inquiry
    })



# @login_required(login_url='login')
# def dashboard_view(request):
#     total_customers = Customer.objects.filter(isadmin=False).count()
#     total_inquiries = Inquiry.objects.count()
#     pending_inquiries = Inquiry.objects.filter(status='Pending').count()
#     responded_inquiries = Inquiry.objects.filter(status='Responded').count()

#     # 🔴 LOW STOCK
#     LOW_STOCK_LIMIT = 5
#     low_stock_ingredients = Ingredient.objects.filter(available_qty__lte=LOW_STOCK_LIMIT)

#     # 📊 DAILY PURCHASE TOTAL (Last 7 days)
#     daily_purchases = (
#         Purchase.objects
#         .values('purchase_date')
#         .annotate(total=Sum('total_amount'))
#         .order_by('-purchase_date')[:7]
#     )

#     # reverse for chart (old → new)
#     daily_purchases = list(daily_purchases)[::-1]

#     purchase_labels = [str(p['purchase_date']) for p in daily_purchases]
#     purchase_totals = [float(p['total'] or 0) for p in daily_purchases]

#     return render(request, 'dashboard/dashboard.html', {
#         'total_customers': total_customers,
#         'total_inquiries': total_inquiries,
#         'pending_inquiries': pending_inquiries,
#         'responded_inquiries': responded_inquiries,

#         'low_stock_ingredients': low_stock_ingredients,

#         # 📊 CHART
#         'purchase_labels': purchase_labels,
#         'purchase_totals': purchase_totals,
#     })
@login_required(login_url='login')
def dashboard_view(request):

    total_customers = Customer.objects.filter(isadmin=False).count()
    total_suppliers = Supplier.objects.count()   # ✅ ADD THIS

    total_inquiries = Inquiry.objects.count()
    pending_inquiries = Inquiry.objects.filter(status='Pending').count()
    responded_inquiries = Inquiry.objects.filter(status='Responded').count()

    # 🔴 LOW STOCK
    LOW_STOCK_LIMIT = 5
    low_stock_ingredients = Ingredient.objects.filter(
        available_qty__lte=LOW_STOCK_LIMIT
    )

    # 📊 DAILY PURCHASE TOTAL (Last 7 days)
    daily_purchases = (
        Purchase.objects
        .values('purchase_date')
        .annotate(total=Sum('total_amount'))
        .order_by('-purchase_date')[:7]
    )

    daily_purchases = list(daily_purchases)[::-1]

    purchase_labels = [str(p['purchase_date']) for p in daily_purchases]
    purchase_totals = [float(p['total'] or 0) for p in daily_purchases]

    return render(request, 'dashboard/dashboard.html', {
        'is_dashboard': True,

        'total_customers': total_customers,
        'total_suppliers': total_suppliers,   # ✅ PASS TO TEMPLATE

        'total_inquiries': total_inquiries,
        'pending_inquiries': pending_inquiries,
        'responded_inquiries': responded_inquiries,

        'low_stock_ingredients': low_stock_ingredients,

        'purchase_labels': purchase_labels,
        'purchase_totals': purchase_totals,
        
    })
   


def get_pending_inquiry_count():
    return Inquiry.objects.filter(status='Pending').count()

# def add_delivery_person(request):
 
#     if request.method == "POST":
#         fname = request.POST.get('fname')
#         lname = request.POST.get('lname')
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         contact = request.POST.get('contact')
#         address = request.POST.get('address')

#         # ---- validation (basic) ----
       
#         if Customer.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists")
#             return redirect('/adminpanel/add-delivery-person/')

#         # ---- create CUSTOMER (login holder) ----
#         customer = Customer.objects.create(
#             username=username,
#             firstname=fname,
#             lastname=lname,
#             email=email,
#             password=password,   # (plain for now – hashing later)
#             contactno=contact,
#             address=address,
#             is_delivery_person=True
#         )

#         # ---- create DELIVERY PERSON ----
#         DeliveryPerson.objects.create(
#             user=customer,
#             fname=fname,
#             lname=lname,
#             email=email,
#             contact_no=contact,
#             address=address
#             # joining_date auto set
#         )

#         messages.success(request, "Delivery Person added successfully")
#         return redirect('add_delivery_person')

#     return render(request, 'adminpanel/add_delivery_person.html')


# def add_delivery_person(request):

#     if request.method == "POST":
#         fname = request.POST.get('fname')
#         lname = request.POST.get('lname')
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         contact = request.POST.get('contact')
#         address = request.POST.get('address')

#         if Customer.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists")
#             return redirect('add_delivery_person')

#         customer = Customer.objects.create(
#             username=username,
#             firstname=fname,
#             lastname=lname,
#             email=email,
#             password=password,   # custom admin chhe etle ok
#             contactno=contact,
#             address=address,
#             is_delivery_person=True
#         )

#         DeliveryPerson.objects.create(
#             user=customer,
#             fname=fname,
#             lname=lname,
#             email=email,
#             contact_no=contact,
#             address=address
#         )

#         messages.success(request, "Delivery Person Added Successfully")
#         return redirect('add_delivery_person')
    
#     # ---------- SEARCH ----------
#     search = request.GET.get('search')
#     delivery_qs = DeliveryPerson.objects.all().order_by('-id')

#     if search:
#         delivery_qs = delivery_qs.filter(
#             Q(fname__icontains=search) |
#             Q(lname__icontains=search) |
#             Q(email__icontains=search) |
#             Q(contact_no__icontains=search)
#         )

#     # ---------- PAGINATION ----------
#     paginator = Paginator(delivery_qs, 5)  # per page 5
#     page_number = request.GET.get('page')
#     delivery_list = paginator.get_page(page_number)

#     return render(request, 'adminpanel/add_delivery_person.html', {
#         'delivery_list': delivery_list,
#         'search': search
#     })

#     delivery_list = DeliveryPerson.objects.all()

#     return render(request, 'adminpanel/add_delivery_person.html', {
#         'delivery_list': delivery_list
#     })



def add_delivery_person(request):

    # ---------- ADD ----------
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')
        address = request.POST.get('address')

        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('add_delivery_person')

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
        return redirect('add_delivery_person')

    # ---------- SEARCH ----------
    search = request.GET.get('search')
    delivery_qs = DeliveryPerson.objects.all().order_by('id')

    if search:
        delivery_qs = delivery_qs.filter(
            Q(fname__icontains=search) |
            Q(lname__icontains=search) |
            Q(email__icontains=search) |
            Q(contact_no__icontains=search)
        )

    # ---------- PAGINATION ----------
    paginator = Paginator(delivery_qs, 5)
    page_number = request.GET.get('page')
    delivery_list = paginator.get_page(page_number)

    return render(request, 'adminpanel/add_delivery_person.html', {
        'delivery_list': delivery_list,
        'search': search
    })


def edit_delivery_person(request, id):
    delivery = get_object_or_404(DeliveryPerson, id=id)

    if request.method == "POST":
        delivery.fname = request.POST.get('fname')
        delivery.lname = request.POST.get('lname')
        delivery.email = request.POST.get('email')
        delivery.contact_no = request.POST.get('contact')
        delivery.address = request.POST.get('address')

        delivery.user.firstname = delivery.fname
        delivery.user.lastname = delivery.lname
        delivery.user.email = delivery.email
        delivery.user.contactno = delivery.contact_no
        delivery.user.address = delivery.address

        delivery.save()
        delivery.user.save()

        messages.success(request, "Delivery Person Updated")
        return redirect('add_delivery_person')

    return render(request, 'adminpanel/edit_delivery_person.html', {
        'delivery': delivery
    })

def delete_delivery_person(request, id):
    delivery = get_object_or_404(DeliveryPerson, id=id)

    delivery.user.delete()   # FK sathe delivery bhi delete
    messages.success(request, "Delivery Person Deleted")

    return redirect('add_delivery_person')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def toggle_delivery_status(request, id):
    if request.method == "POST":
        delivery = get_object_or_404(DeliveryPerson, id=id)
        delivery.is_active = not delivery.is_active
        delivery.save()

        return JsonResponse({
            'status': delivery.is_active
        })



# ======================
# STATE
# ======================
def add_and_list_state(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:  # simple validation
            # Check if state already exists
            if State.objects.filter(name__iexact=name).exists():
                messages.error(request, "State already exists!")
            else:
                State.objects.create(name=name)
                messages.success(request, "State added successfully!")
        return redirect('add_and_list_state')  # redirect to same page to show updated list

    # GET request → show form and list
    states = State.objects.all().order_by('id')
    return render(request, "adminpanel/add_and_list_state.html", {'states': states})

def edit_state(request, id):
    state = get_object_or_404(State, id=id)
    updated = False  # default

    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            if State.objects.filter(name__iexact=name).exclude(id=id).exists():
                messages.error(request, "State with this name already exists!")
            else:
                state.name = name
                state.save()
                updated = True  # ✅ flag to show card

    return render(request, "adminpanel/edit_state.html", {'state': state, 'updated': updated})


def delete_state(request, id):
    State.objects.filter(id=id).delete()
    return redirect('add_and_list_state')

# ======================
# CITY
# ======================
def add_and_list_city(request):
    states = State.objects.all().order_by('name')  # For dropdown
    if request.method == "POST":
        name = request.POST.get('name')
        state_id = request.POST.get('state')
        if name and state_id:
            state = get_object_or_404(State, id=state_id)
            if City.objects.filter(name__iexact=name, state=state).exists():
                messages.error(request, "City already exists for this state!")
            else:
                City.objects.create(name=name, state=state)
                messages.success(request, "City added successfully!")
        return redirect('add_and_list_city')

    cities = City.objects.all().order_by('id')
    return render(request, "adminpanel/add_and_list_city.html", {'cities': cities, 'states': states})



def edit_city(request, id):
    city = get_object_or_404(City, id=id)
    states = State.objects.all().order_by('name')
    updated = False

    if request.method == "POST":
        new_name = request.POST.get('name')
        new_state_id = request.POST.get('state')

        if new_name and new_state_id:
            state_obj = get_object_or_404(State, id=new_state_id)

            if City.objects.filter(name__iexact=new_name, state=state_obj).exclude(id=id).exists():
                messages.error(request, "City with this name already exists in selected state!")
            else:
                city.name = new_name
                city.state = state_obj
                city.save()
                updated = True

    return render(request, "adminpanel/edit_city.html", {'city': city, 'states': states, 'updated': updated})

def delete_city(request, id):
    City.objects.filter(id=id).delete()
    return redirect('add_and_list_city')


# ======================
# AREA
# ======================
# # def add_and_list_area(request):
# #     if request.method == "POST":
# #         name = request.POST.get('name')
# #         city_id = request.POST.get('city')
# #         if name and city_id:
# #             city = City.objects.get(id=city_id)
# #             if Area.objects.filter(name__iexact=name, city=city).exists():
# #                 messages.error(request, "Area already exists in this city!")
# #             else:
# #                 Area.objects.create(name=name, city=city)
# #                 messages.success(request, "Area added successfully!")
# #         return redirect('add_and_list_area')

#     cities = City.objects.all().order_by('name')  # for dropdown
#     areas = Area.objects.all().order_by('id')
#     return render(request, "adminpanel/add_and_list_area.html", {'areas': areas, 'cities': cities})
def add_and_list_area(request):
    if request.method == "POST":
        name = request.POST.get('name')
        city_id = request.POST.get('city')

        if name and city_id:
            city = get_object_or_404(City, id=city_id)

            if Area.objects.filter(name__iexact=name, city=city).exists():
                messages.error(request, "Area already exists in this city!")
            else:
                # 🔥 Fetch lat/lng using improved function
                lat, lng = get_lat_lng_from_osm(name, city.name, city.state.name if city.state else "Gujarat")

                if lat is None or lng is None:
                    messages.warning(request, "Could not fetch coordinates. Please check spelling!")
                    lat, lng = 0.0, 0.0  # optional fallback

                Area.objects.create(
                    name=name,
                    city=city,
                    latitude=lat,
                    longitude=lng
                )
                messages.success(request, "Area added successfully!")

        return redirect('add_and_list_area')

    # GET request → show page
    cities = City.objects.all().order_by('name')
    areas = Area.objects.all().order_by('id')
    return render(request, "adminpanel/add_and_list_area.html", {
        'areas': areas,
        'cities': cities
    })

 
def edit_area(request, id):
    area = get_object_or_404(Area, id=id)
    cities = City.objects.all().order_by('name')
    updated = False

    if request.method == "POST":
        new_name = request.POST.get('name')
        new_city_id = request.POST.get('city')

        if new_name and new_city_id:
            city_obj = get_object_or_404(City, id=new_city_id)

            if Area.objects.filter(name__iexact=new_name, city=city_obj).exclude(id=id).exists():
                messages.error(request, "Area with this name already exists in selected city!")
            else:
                area.name = new_name
                area.city = city_obj
                area.save()
                updated = True

    return render(request, "adminpanel/edit_area.html", {'area': area, 'cities': cities, 'updated': updated})


def delete_area(request, id):
    Area.objects.filter(id=id).delete()
    return redirect('add_and_list_area')


def add_delivery_person(request):
    # ⚠️ OPTIONAL: agar admin login session use kar rahi ho
    # if 'admin_id' not in request.session:
    #     return redirect('/adminpanel/login/')

    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')
        address = request.POST.get('address')

        # ---- validation (basic) ----
       
        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/adminpanel/add-delivery-person/')

        # ---- create CUSTOMER (login holder) ----
        customer = Customer.objects.create(
            username=username,
            firstname=fname,
            lastname=lname,
            email=email,
            password=password,   # (plain for now – hashing later)
            contactno=contact,
            address=address,
            is_delivery_person=True
        )

        # ---- create DELIVERY PERSON ----
        DeliveryPerson.objects.create(
            user=customer,
            fname=fname,
            lname=lname,
            email=email,
            contact_no=contact,
            address=address
            # joining_date auto set
        )

        messages.success(request, "Delivery Person added successfully")
        return redirect('add_delivery_person')

    return render(request, 'adminpanel/add_delivery_person.html')




User = get_user_model()

def admin_customers(request):
    customers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        is_delivery_person=False
    ).order_by('-creationdate')

    return render(request, 'adminpanel/customers/customers.html', {
        'customers': customers
    })




def get_lat_lng_from_osm(area, city, state="Gujarat"):
    """
    Fetch real lat/lng from OSM for given area, city, state
    """
    query = f"{area}, {city}, {state}, India"
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "RestaurantProject/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            print(f"OSM: Found {area} → lat: {lat}, lng: {lng}")
            return lat, lng
        else:
            print(f"OSM: No data for {query}")
            return None, None

    except requests.RequestException as e:
        print(f"OSM ERROR: {e}")
        return None, None


from django.shortcuts import render, redirect
from .forms import NotificationForm

# @login_required
# def admin_notifications(request):
#     notifications = Notification.objects.all().order_by('-send_datetime')

#     if request.method == "POST":
#         form = NotificationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Notification sent successfully")
#             form = NotificationForm()   # ✅ reset form
#     else:
#         form = NotificationForm()

#     return render(request, 'adminpanel/notifications.html', {
#         'form': form,
#         'notifications': notifications
#     })
@login_required
def admin_notifications(request):
    notifications = Notification.objects.all().order_by('-send_datetime')

    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification sent successfully")
            form = NotificationForm()   # ✅ reset form
    else:
        form = NotificationForm()

    return render(request, 'adminpanel/notifications.html', {
        'form': form,
        'notifications': notifications
    })


from django.shortcuts import get_object_or_404

def edit_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    if request.method == "POST":
        form = NotificationForm(request.POST, instance=notif)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification updated successfully!")
            return redirect('admin_notifications')  # redirect back to your notifications page
    else:
        form = NotificationForm(instance=notif)
    
    return render(request, 'adminpanel/edit_notification.html', {'form': form, 'notif': notif})

def delete_notification(request, id):
    notif = get_object_or_404(Notification, id=id)
    notif.delete()
    messages.success(request, "Notification deleted")
    return redirect('admin_notifications')

def delivery_person_list(request):
    return render(request, 'adminpanel/delivery_person_list.html')
