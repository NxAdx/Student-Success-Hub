from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = (
                'w-full px-4 py-3 rounded-xl border border-white/20 bg-white/5 '
                'text-white placeholder-gray-400 focus:outline-none focus:ring-2 '
                'focus:ring-indigo-500 focus:border-transparent transition-all duration-300'
            )
            field.widget.attrs['placeholder'] = field.label


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = (
                'w-full px-4 py-3 rounded-xl border border-white/20 bg-white/5 '
                'text-white placeholder-gray-400 focus:outline-none focus:ring-2 '
                'focus:ring-indigo-500 focus:border-transparent transition-all duration-300'
            )
            field.widget.attrs['placeholder'] = field.label


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'banner', 'bio', 'skills',
                  'department', 'graduation_year', 'linkedin_url', 'github_url', 'phone']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'banner':
                field.widget.attrs['class'] = 'block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700'
            else:
                field.widget.attrs['class'] = (
                    'w-full px-4 py-3 rounded-xl border border-gray-600 bg-gray-700/50 '
                    'text-white placeholder-gray-400 focus:outline-none focus:ring-2 '
                    'focus:ring-indigo-500 focus:border-transparent transition-all duration-300'
                )
