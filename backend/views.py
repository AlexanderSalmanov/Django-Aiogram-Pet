from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from .forms import LoginForm

from tg_bot.airtable_dump import table

from pyairtable.formulas import match


class HomePage(generic.TemplateView):
    template_name = 'home.html'

home_page = HomePage.as_view()

class LoginView(generic.FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        request = self.request
        user = request.user

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            return redirect('/profile/')

            return super(LoginView, self).form_invalid(form)

login_view = LoginView.as_view()

@login_required
def profile_page(request):
    user_obj = request.user

    formula = match({'username': user_obj.username})
    airtable_user_sheet = table.first(formula=formula)

    all_entries = table.all()
    user_entry = None
    for entry in all_entries:
        if entry['fields'].get('username') == user_obj.username:
            user_entry = entry['fields']
            break

    context = {
        'username': user_obj.username,
        'email': user_obj.email,
        'tg_data': user_entry
    }

    return render(request, 'auth/profile.html', context)
