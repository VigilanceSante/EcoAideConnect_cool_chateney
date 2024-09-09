from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import RegisterForm
from django.contrib.auth import login
from django.shortcuts import redirect

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to auth/urls.py file for more pages.
"""


class RegisterView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Update the context
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                print('User created')
                context = self.get_context_data(**kwargs)
                return redirect('index')
            else:
                print(form.errors)
                print('User not created')
                form = RegisterForm()
            return self.render_to_response(context)


class LoginView(TemplateView):   
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Update the context
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context
    
    def login(self, request, **kwargs):
        """
        if request.method == 'POST':
            form = CustomAuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                context = self.get_context_data(**kwargs)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                return redirect('')
            else:
                form = CustomAuthenticationForm()
                return self.render_to_response(context)
                """