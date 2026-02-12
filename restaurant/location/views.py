from django.shortcuts import render
from django.db.models import Count
from location.models import Area
from orders.models import Order  

area_orders = (
    Order.objects
    .values('area__latitude', 'area__longitude')
    .annotate(order_count=Count('id'))
    .filter(area__latitude__isnull=False, area__longitude__isnull=False)
)



def order_heatmap(request):
    # Area-wise order count
    area_orders = Area.objects.annotate(order_count=Count('order')).values('name', 'order_count')

    labels = [area['name'] for area in area_orders]
    values = [area['order_count'] for area in area_orders]

    context = {
        'labels': labels,
        'values': values,
    }
    return render(request, 'dashboard/order_heatmap_grid.html', context)