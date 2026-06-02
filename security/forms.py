from django import forms


class HoneypotForm(forms.Form):
    """Base form with honeypot field."""
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Leave this field empty'
    )
    
    def clean_honeypot(self):
        """Validate that honeypot field remains empty."""
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise forms.ValidationError('Invalid form submission')
        return honeypot
