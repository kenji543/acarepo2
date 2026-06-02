from django import forms
from .models import ResearchPaper, CoAuthor, Dataset


class ResearchPaperForm(forms.ModelForm):
    """Form for creating/editing research papers."""
    
    class Meta:
        model = ResearchPaper
        fields = ['title', 'abstract', 'keywords', 'publication_date', 'doi', 
                  'pdf_file', 'supplementary_data', 'raw_data_file', 'visibility', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Paper Title'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10.xxxx/xxxxx'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class CoAuthorInlineFormSet(forms.BaseInlineFormSet):
    """Formset for managing co-authors."""
    def clean(self):
        super().clean()
        orders = [form.cleaned_data.get('order') for form in self.forms if form.cleaned_data]
        if len(orders) != len(set(orders)):
            raise forms.ValidationError("Co-author order must be unique.")


class DatasetForm(forms.ModelForm):
    """Form for creating/editing datasets."""
    
    class Meta:
        model = Dataset
        fields = ['title', 'description', 'file_format', 'data_file', 'visibility', 'version']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file_format': forms.TextInput(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
        }
