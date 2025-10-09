from django import forms
from .models import Post


class PostCreateForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. travel, foodie, sunset"}),
        help_text="Separate tags with commas."
    )

    class Meta:
        model = Post
        fields = ["caption"]
        widgets = {
            "caption": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"class": "form-control-file"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ImageUploadForm(forms.Form):
    images = MultipleImageField(required=True)