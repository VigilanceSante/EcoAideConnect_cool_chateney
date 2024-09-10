"""
This file contains the views for the authentication app.
"""
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import RegisterForm, LoginForm

class RegisterView(TemplateView):
    """
    A view to register a new user.
    """
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
        """
        Handle the POST request to register a new user.
        """
        context = self.get_context_data(**kwargs)
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                if User.objects.count() == 1:
                    # First user becomes an Admin
                    admin_group = Group.objects.get(name='admins')
                    admin_group.user_set.add(user)
                    user.is_staff = True
                    user.is_superuser = True
                else:
                    # Other users become Standard Users
                    standard_group = Group.objects.get(name='town_hall_employee_group')
                    standard_group.user_set.add(user)
                    user.is_staff = False
                    user.is_superuser = False
                user.save()
                context = self.get_context_data(**kwargs)
                return redirect('index')
            context['form'] = form
            return self.render_to_response(context)


class LoginView(TemplateView):   
    """
    A view to login a user.
    """
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
        """
        Handle the POST request to login a user.
        """
        context = self.get_context_data(**kwargs)
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                context = self.get_context_data(**kwargs)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                return redirect('index')
            context['form'] = form
            return self.render_to_response(context)
            