from django import forms
from .models import Profile, Review


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            "full_name",
            "bio",
            "profile_picture",
            "skills_offered",
            "skills_wanted",
            "experience",
            "language",
            "availability",
            "location",
            "learning_mode",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your full name"
            }),

            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Tell others about yourself"
            }),

            "skills_offered": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Example: Python, Java, HTML"
            }),

            "skills_wanted": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Example: Django, React, AI"
            }),

            "experience": forms.Select(attrs={
                "class": "form-control"
            }),

            "language": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "English, Tamil, Hindi..."
            }),

            "availability": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Weekends, Evenings..."
            }),

            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "City"
            }),

            "learning_mode": forms.Select(attrs={
                "class": "form-control"
            }),

            "profile_picture": forms.FileInput(attrs={
                "class": "form-control"
            }),
        }


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review

        fields = [
            "rating",
            "review",
        ]

        widgets = {
            "rating": forms.Select(attrs={
                "class": "form-control"
            }),

            "review": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Write your review here...",
                "class": "form-control"
            }),
        }

        labels = {
            "rating": "Rating",
            "review": "Your Review",
        }