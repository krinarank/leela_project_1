from django import forms
from adminpanel.models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'recipient_type']
        widgets = {
            'send_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
# from django import forms
# from .models import Notification

# class NotificationForm(forms.ModelForm):
#     class Meta:
#         model = Notification
#         exclude = ['send_datetime', 'read_status','user']

#     def clean_title(self):
#         title = self.cleaned_data['title']
#         if len(title) < 3:
#             raise forms.ValidationError("Title must be at least 3 characters")
#         return title
