from adminpanel.models import Notification
from django.utils import timezone
from django.db.models import Q

def notification_count(request):

    if request.user.is_authenticated:

        count = Notification.objects.filter(
            recipient_type='customer',
            read_status=False
        ).filter(
            Q(user_id__isnull=True) | Q(user_id=request.user.id)
        ).count()

    else:
        count = 0

    return {'notification_count': count}
