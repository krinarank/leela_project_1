from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    FoodItemCategory,
    FoodItemSubCategory,
    FoodItem,
    FoodItemImage
)

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

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


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
        FoodItemCategory.objects.create(
            category_name=request.POST.get('category_name')
        )
        return redirect('add_category')

    # RIGHT SIDE TABLE MATE DATA
    categories = FoodItemCategory.objects.all()

    return render(request, 'add/add_category.html', {
        'categories': categories
    })

def add_subcategory(request):
    if request.method == 'POST':
        FoodItemSubCategory.objects.create(
            subcategory_name=request.POST.get('subcategory_name'),
            food_item_cat_id=request.POST.get('category_id')  # ✅ FIX
        )
        messages.success(request, "Subcategory added successfully")
        return redirect('add_subcategory')

    subcategories = FoodItemSubCategory.objects.select_related('food_item_cat').all()
    categories = FoodItemCategory.objects.all()

    return render(request, 'add/add_subcategory.html', {
        'subcategories': subcategories,
        'categories': categories
    })

# ---------------- ADD FOOD ITEM ----------------
def add_fooditem(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        name = request.POST.get('name')
        price = request.POST.get('price')
        calories = request.POST.get('calories')
        is_available = request.POST.get('is_available') == 'on'

        # Validate
        if not all([category_id, subcategory_id, name, price, calories]):
            messages.error(request, "All fields are required")
            return redirect('add_fooditem')

        subcategory = get_object_or_404(FoodItemSubCategory, id=subcategory_id)

        FoodItem.objects.create(
            name=name,
            price=float(price),
            calories=int(calories),
            is_available=is_available,
            sub_cat=subcategory
        )

        messages.success(request, "Food item added successfully")
        return redirect('add_fooditem')

    # GET
    fooditems = FoodItem.objects.select_related('sub_cat__food_item_cat').all()
    categories = FoodItemCategory.objects.all()
    subcategories = FoodItemSubCategory.objects.all()

    return render(request, 'add/add_fooditem.html', {
        'fooditems': fooditems,
        'categories': categories,
        'subcategories': subcategories
    })

# ---------------- UPDATE FOOD ITEM ----------------
def update_fooditem(request, id):
    item = get_object_or_404(FoodItem, id=id)
    subcategories = FoodItemSubCategory.objects.all()

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.price = request.POST.get('price')
        item.calories = request.POST.get('calories')
        item.is_available = True if request.POST.get('is_available') == 'on' else False
        item.sub_cat_id = request.POST.get('subcategory_id')
        item.save()

        # ✅ SHOW message on the same page
        messages.success(request, "Food item updated successfully")
        # Don't redirect to add_fooditem
        return redirect('update_fooditem', id=item.id)

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

# def add_foodimage(request):
#     food_items = FoodItem.objects.all()
#     if request.method == 'POST':
#         food_id = request.POST.get('food_item')
#         image_file = request.FILES.get('img_url')

#         if food_id and image_file:
#             try:
#                 food = FoodItem.objects.get(id=food_id)  # FK object
#                 FoodItemImage.objects.create(
#                     food_item=food,  # must pass object, not string
#                     img_url=image_file
#                 )
#                 print("Image saved!")  # debug
#                 return redirect('admin_menu')
#             except FoodItem.DoesNotExist:
#                 print("FoodItem not found!")
#     return render(request, 'add/add_foodimage.html', {'food_items': food_items})
# ---------------- ADD + LIST FOOD IMAGE ----------------
def add_foodimage(request):
    if request.method == 'POST':
        food_id = request.POST.get('food_item')
        image = request.FILES.get('img_url')

        if food_id and image:
            food = get_object_or_404(FoodItem, id=food_id)
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
    food_items = FoodItem.objects.all()

    return render(request, 'add/add_foodimage.html', {
        'food_items': food_items,
        'images': images
    })

# ---------------- UPDATE FOOD IMAGE ----------------
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
        messages.success(request, "Food image updated successfully")
        return redirect('update_foodimage', id=image.id)

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

def update_category_page(request, category_id):
    category = get_object_or_404(FoodItemCategory, id=category_id)

    if request.method == "POST":
        new_name = request.POST.get('category_name')
        if new_name:
            category.category_name = new_name
            category.save()
            messages.success(request, "Category updated successfully!")
            return redirect('update_category', category_id=category.id)
        else:
            messages.error(request, "Please enter a category name.")

    context = {
        'category': category
    }
    return render(request, 'update/update_category.html', context)
#update subcategory
def update_subcategory(request, id):
    sub = get_object_or_404(FoodItemSubCategory, id=id)
    categories = FoodItemCategory.objects.all()

    if request.method == 'POST':
        sub.subcategory_name = request.POST.get('subcategory_name')

        cat_id = request.POST.get('food_item_cat')
        sub.food_item_cat = FoodItemCategory.objects.get(id=cat_id)

        sub.save()

        messages.success(request, "Subcategory updated successfully")

        return render(request, 'update/update_subcategory.html', {
            'sub': sub,
            'categories': categories
        })

    return render(request, 'update/update_subcategory.html', {
        'sub': sub,
        'categories': categories
    })
# Delete subcategory
def delete_subcategory_item(request, id):
    sub = get_object_or_404(FoodItemSubCategory, id=id)
    sub.delete()
    return redirect('add_subcategory')