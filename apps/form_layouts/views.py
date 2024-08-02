from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactForm

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to form_layouts/urls.py file for more pages.
"""

class FormLayoutsView(TemplateView):
    template_name = 'contact_form.html'

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def post(self, request, *args, **kwargs):
        form_data = {
            'message': request.POST.get('message'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'monday_all_day': request.POST.get('monday_all_day') == 'on',
            'monday_morning': request.POST.get('monday_morning') == 'on',
            'monday_afternoon': request.POST.get('monday_afternoon') == 'on',
            'monday_evening': request.POST.get('monday_evening') == 'on',
            'tuesday_all_day': request.POST.get('tuesday_all_day') == 'on',
            'tuesday_morning': request.POST.get('tuesday_morning') == 'on',
            'tuesday_afternoon': request.POST.get('tuesday_afternoon') == 'on',
            'tuesday_evening': request.POST.get('tuesday_evening') == 'on',
            'wednesday_all_day': request.POST.get('wednesday_all_day') == 'on',
            'wednesday_morning': request.POST.get('wednesday_morning') == 'on',
            'wednesday_afternoon': request.POST.get('wednesday_afternoon') == 'on',
            'wednesday_evening': request.POST.get('wednesday_evening') == 'on',
            'thursday_all_day': request.POST.get('thursday_all_day') == 'on',
            'thursday_morning': request.POST.get('thursday_morning') == 'on',
            'thursday_afternoon': request.POST.get('thursday_afternoon') == 'on',
            'thursday_evening': request.POST.get('thursday_evening') == 'on',
            'friday_all_day': request.POST.get('friday_all_day') == 'on',
            'friday_morning': request.POST.get('friday_morning') == 'on',
            'friday_afternoon': request.POST.get('friday_afternoon') == 'on',
            'friday_evening': request.POST.get('friday_evening') == 'on',
            'saturday_all_day': request.POST.get('saturday_all_day') == 'on',
            'saturday_morning': request.POST.get('saturday_morning') == 'on',
            'saturday_afternoon': request.POST.get('saturday_afternoon') == 'on',
            'saturday_evening': request.POST.get('saturday_evening') == 'on',
            'sunday_all_day': request.POST.get('sunday_all_day') == 'on',
            'sunday_morning': request.POST.get('sunday_morning') == 'on',
            'sunday_afternoon': request.POST.get('sunday_afternoon') == 'on',
            'sunday_evening': request.POST.get('sunday_evening') == 'on',
        }
        contact_form = ContactForm(**form_data)
        contact_form.save()
        messages.success(request, 'Votre message a été envoyé avec succès.')
        return redirect('contact_form')
