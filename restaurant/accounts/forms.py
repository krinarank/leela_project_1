from django import forms
from .models import Customer
from django.core.exceptions import ValidationError


class CustomerProfileForm(forms.ModelForm):

    # ✅ IMPORTANT: make image optional
    profile_image = forms.ImageField(required=False)

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=False
    )

    def clean_contactno(self):
        contact = self.cleaned_data.get('contactno')

        if contact:
            if not contact.isdigit():
                raise ValidationError("Phone number must contain only digits")

            if len(contact) < 10 or len(contact) > 12:
                raise ValidationError("Phone number must be 10–12 digits")

        return contact

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')

        if image:
            if image.size > 2 * 1024 * 1024:
                raise ValidationError("Image size must be less than 2MB")

            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise ValidationError("Only PNG, JPG, JPEG allowed")

        return image

    class Meta:
        model = Customer
        fields = [
            'firstname',
            'lastname',
            'gender',
            'contactno',
            'address',
            'profile_image'
        ]

        # ✅ widgets MUST be inside Meta
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter your address'
            }),
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'contactno': forms.TextInput(attrs={'class': 'form-control'}),
        }
