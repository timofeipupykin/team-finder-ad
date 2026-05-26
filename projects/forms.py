from urllib.parse import urlparse

from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        if not github_url:
            return github_url
        parsed = urlparse(github_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc.lower().endswith(
            "github.com"
        ):
            raise forms.ValidationError("Укажите ссылку на github.com")
        return github_url
