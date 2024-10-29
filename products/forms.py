from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш відгук'}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Пошук'}))