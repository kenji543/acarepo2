from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-900 "
    "placeholder:text-slate-400 transition duration-200 "
    "focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
)


class SessionLoginForm(AuthenticationForm):
    """Styled login form for template-based session authentication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASS


class SessionRegistrationForm(UserCreationForm):
    """Styled registration form for template-based sign-up."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": INPUT_CLASS, "placeholder": "you@university.edu"}
        ),
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Last name"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": INPUT_CLASS, "placeholder": "Choose a username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": INPUT_CLASS, "placeholder": "Create a password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": INPUT_CLASS, "placeholder": "Confirm your password"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
