from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def group_required(group_name):
    def in_group(user):
        return user.is_authenticated and user.groups.filter(name=group_name).exists()
    return user_passes_test(in_group, login_url='login')
