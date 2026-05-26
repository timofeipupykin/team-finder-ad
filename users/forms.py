from django import forms
from django.contrib.auth import authenticate

from .models import User
from .utils import is_github_url, is_valid_phone, normalize_phone


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def save(self, commit=True):
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
        )
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный email или пароль")
            self.user = user
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        if not is_valid_phone(phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )
        normalized = normalize_phone(phone)
        qs = User.objects.filter(phone=normalized)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Пользователь с таким номером уже существует")
        return normalized

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        if github_url and not is_github_url(github_url):
            raise forms.ValidationError("Укажите ссылку на github.com")
        return github_url
