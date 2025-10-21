from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """A custom form for user sign-up that includes email"""

    username = forms.CharField(
        max_length=30,
        help_text="Required. 30 characters or fewer. Letters, digits, - and _ only."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({
                "class": "form-control"
            })


class CustomAuthenticationForm(AuthenticationForm):
    """A custom login form that allows login with either a username or an email address"""

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            self.user_cache = authenticate(self.request, username=username_or_email, password=password)

            if self.user_cache is None and "@" in username_or_email:
                try:
                    user = User.objects.get(email__iexact=username_or_email)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class ProfileSetupForm(forms.ModelForm):
    """A form for the mandatory profile setup step after email verification"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "bio", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your First Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your Last Name"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "avatar": forms.FileInput(attrs={"class": "form-control-file"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "avatar": forms.FileInput(attrs={"class": "form-control-file"}),
        }