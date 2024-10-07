"""
This file contains the views for the authentication app.
"""
from django.views.generic import TemplateView
from django.contrib.auth import login, logout
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from apps.authentication.models import RegisterInvitation
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import RegisterForm, LoginForm, InvitationForm
from .decorators import group_required

class RegisterView(TemplateView):
    """
    A view to register a new user.
    """

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context

    def get(self, request, **kwargs):
        """
        Handle the GET request to register page.
        """
        context = self.get_context_data(**kwargs)
        token = kwargs.get('token', '')
        invitation = get_object_or_404(RegisterInvitation, token=token)
        if invitation:
            context['invitation_role'] = invitation.role
            context['invite_token'] = token
            return self.render_to_response(context)
        return self.render_to_response(context)

    def post(self, request, token, **kwargs):
        """
        Handle the POST request to register a new user.
        """
        context = self.get_context_data(**kwargs)
        context['invite_token'] = token
        invitation = get_object_or_404(RegisterInvitation, token=token)
        context['invitation_role'] = invitation.role

        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                user_group = Group.objects.get(name=context['invitation_role']+'_group')
                user_group.user_set.add(user)
                if invitation.role == 'admin_town_hall_employee':
                    user_group = Group.objects.get(name="admins")
                    user_group.user_set.add(user)
                    user_group = Group.objects.get(name="town_hall_employee_group")
                    user_group.user_set.add(user)
                    user.is_staff = True
                    #user.is_superuser = True
                elif invitation.role == 'town_hall_employee':
                    user.is_staff = False
                    user.is_superuser = False
                user.save()
                logout(request)
                login(request, user)
                return redirect('index')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
        return self.render_to_response(self.get_context_data(**kwargs))

class LoginView(TemplateView):
    """
    A view to login a user.
    """
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
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
        print("login_test_1")
        if request.method == 'POST':
            print("login_test_2")
            form = LoginForm(request.POST)
            print("form", form.is_valid())
            print(form.errors)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                print("login_test")
                context = self.get_context_data(**kwargs)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(3600)
                else:
                    request.session.set_expiry(1209600)
                return redirect('index')
            context = self.get_context_data(**kwargs)
            context['form'] = form
        return self.render_to_response(self.get_context_data(**kwargs))

class InviteUserView(TemplateView):
    form_class = InvitationForm
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )

        return context

    def form_valid(self, form):
        invitation = form.save(commit=False)
        invitation.invited_by = self.request.user
        invitation.save()
        invite_link = self.request.build_absolute_uri(reverse('register', args=[invitation.token]))
        send_mail(
            'Invitation d\'inscription coolchatenay',
            f'Vous avez été invité(e) à vous inscrire: {invite_link}',
            settings.DEFAULT_FROM_EMAIL,
            [invitation.email],
        )
        return redirect('index')

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            context = self.get_context_data(**kwargs)
            if request.user.groups.filter(name='admin_town_hall_employee_group').exists():
                context['form'] = self.form_class()
                return self.render_to_response(context)
        return redirect('index')

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            context = self.get_context_data(**kwargs)
            if request.user.groups.filter(name='admin_town_hall_employee_group').exists():
                context['form'] = self.form_class()
                if request.method == 'POST':
                    form = self.form_class(request.POST)
                    if form.is_valid():
                        return self.form_valid(form)
                    context['form'] = form
                    return self.render_to_response(context)
        return redirect('index')
    