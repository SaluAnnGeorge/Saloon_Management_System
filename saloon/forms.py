from django import forms
from .models import Review, Service, ServiceReview

class ReviewForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    
    class Meta:
        model = Review
        fields = ['service', 'rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select mb-3'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'rows': 4,
                'placeholder': 'Share your experience with this service...'
            }),
        }

class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience with this service...'}),
        }

from django import forms
from .models import Category

class ServiceSearchForm(forms.Form):
    q = forms.CharField(max_length=100, required=False, label="Service Name")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Category")


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)