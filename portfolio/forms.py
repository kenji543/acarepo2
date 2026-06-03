from django import forms
from .models import ResearchPaper, CoAuthor, Dataset

INPUT_CLASS = (
    "w-full rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-900 "
    "placeholder:text-slate-400 transition duration-200 "
    "focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
)
SELECT_CLASS = INPUT_CLASS
TEXTAREA_CLASS = f"{INPUT_CLASS} resize-y min-h-[8rem]"
FILE_INPUT_CLASS = "absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0"


class ResearchPaperForm(forms.ModelForm):
    """Form for creating/editing research papers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pdf_field = self.fields["pdf_file"]
        
        # For editing (instance exists), make PDF optional to preserve existing file
        if self.instance and self.instance.pk:
            pdf_field.required = False
        else:
            pdf_field.required = True
        
        pdf_field.widget.attrs.update(
            {
                "accept": "application/pdf",
            }
        )

    def clean_pdf_file(self):
        uploaded = self.cleaned_data.get("pdf_file")
        
        # If no file uploaded, check if it's an edit (should have existing file)
        if not uploaded:
            if self.instance and self.instance.pdf_file:
                return self.instance.pdf_file
            raise forms.ValidationError("A PDF file is required.")

        if not uploaded.name.lower().endswith(".pdf"):
            raise forms.ValidationError(
                "Only PDF files are allowed for the main paper upload."
            )

        content_type = getattr(uploaded, "content_type", "") or ""
        if content_type and content_type not in (
            "application/pdf",
            "application/x-pdf",
        ):
            raise forms.ValidationError(
                "Only PDF files are allowed for the main paper upload."
            )

        return uploaded

    class Meta:
        model = ResearchPaper
        fields = [
            "title",
            "abstract",
            "keywords",
            "publication_date",
            "doi",
            "pdf_file",
            "supplementary_data",
            "raw_data_file",
            "visibility",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Enter the full paper title",
                }
            ),
            "abstract": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 5,
                    "placeholder": "Summarize your research findings and methodology",
                }
            ),
            "keywords": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "machine learning, climate science, …",
                }
            ),
            "publication_date": forms.DateInput(
                attrs={"class": INPUT_CLASS, "type": "date"}
            ),
            "doi": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "10.1234/example.doi",
                }
            ),
            "visibility": forms.Select(attrs={"class": SELECT_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "pdf_file": forms.FileInput(
                attrs={
                    "class": FILE_INPUT_CLASS,
                    "accept": "application/pdf",
                    "required": "required",
                    "data-file-label": "pdf-filename",
                }
            ),
            "supplementary_data": forms.FileInput(
                attrs={
                    "class": FILE_INPUT_CLASS,
                    "data-file-label": "supplementary-filename",
                }
            ),
            "raw_data_file": forms.FileInput(
                attrs={
                    "class": FILE_INPUT_CLASS,
                    "data-file-label": "rawdata-filename",
                }
            ),
        }


class CoAuthorInlineFormSet(forms.BaseInlineFormSet):
    """Formset for managing co-authors."""

    def clean(self):
        super().clean()
        orders = [
            form.cleaned_data.get("order")
            for form in self.forms
            if form.cleaned_data
        ]
        if len(orders) != len(set(orders)):
            raise forms.ValidationError("Co-author order must be unique.")


class DatasetForm(forms.ModelForm):
    """Form for creating/editing datasets."""

    class Meta:
        model = Dataset
        fields = [
            "title",
            "description",
            "file_format",
            "data_file",
            "visibility",
            "version",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "description": forms.Textarea(
                attrs={"class": TEXTAREA_CLASS, "rows": 4}
            ),
            "file_format": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "visibility": forms.Select(attrs={"class": SELECT_CLASS}),
            "version": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "data_file": forms.FileInput(attrs={"class": FILE_INPUT_CLASS}),
        }
