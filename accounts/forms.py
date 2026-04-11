from django import forms

from .models import CustomUser


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class SalesmanCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "SALESMAN"
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class SalesmanEditForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Yangi parol (ixtiyoriy)",
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number"]

    def save(self, commit=True):
        user = super().save(commit=False)
        pw = self.cleaned_data.get("password")
        if pw:
            user.set_password(pw)
        if commit:
            user.save()
        return user
