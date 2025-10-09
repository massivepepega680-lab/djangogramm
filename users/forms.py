from django import forms
from .models import User


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "avatar": forms.FileInput(attrs={"class": "form-control-file"}),
        }