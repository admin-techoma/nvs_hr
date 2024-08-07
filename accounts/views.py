from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_control
from accounts.forms import CustomPasswordChangeForm
from employee.models import Employee

User = get_user_model()

@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def login(request):
    # if request.user.is_authenticated:
    #     return redirect('hr:hr_dashboard') 

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user and Employee.objects.filter(emp_user=user).exists():
            auth.login(request, user)

            employee = Employee.objects.get(emp_user=user)
            if not employee.password_changed:
                print("Password Changed Status:", employee.password_changed)
                print("Redirecting to change_password")
                return redirect('accounts:change_password')
            else:
                request.session['employee_name'] = employee.name
                request.session['department'] = employee.department.name
                request.session['designation'] = employee.designation.name
                request.session['documents_id'] = employee.documents_id_id
                request.session['emp_id'] = employee.emp_id
                request.session['reporting_take'] = employee.reporting_take
                request.session['session_email'] = employee.email

                if employee.department.name == 'Human Resource':
                    return redirect('hr:hr_dashboard')
                elif employee.department.name == 'Admin':
                    return redirect('hr:admin_dashboard')
                # # elif employee.position.name == 'Manager':
                # #     return redirect('employee:rmdash')
                else:
                    return redirect('employee:dash')
        elif user is not None and user.is_active: # Check if authentication is successful and user is active
            auth.login(request, user)    
            if user.is_superuser:
                    return redirect('hr:admin_dashboard')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('accounts:login')

    return render(request, 'auth/login.html')



@login_required
def change_password(request):
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            
            user = request.user
            try:
                employee = Employee.objects.get(emp_user=user)
                employee.password_changed = True
                employee.save()
            except Employee.DoesNotExist:
                messages.info(request, 'Employee does not exist')
                return redirect('accounts:login')
            form.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('employee:dash')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'auth/change_password.html', {'form': form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url=reverse_lazy('accounts:login'))

def logout(request):
    auth.logout(request)
    return redirect('accounts:login')



def password_reset_request(request):
    if request.method == "POST":
       
        data = request.POST['email']
        
        user = User.objects.filter(email=data)
        
        if user.exists():
            user = user[0]
            subject = "Password Reset Request"
            email_template_name = "auth/password_reset_email.txt"
            c = {
            "email":user.email,
            'domain': 'https://nvs.techoma.io/',
            'site_name':'Website',
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            'token': default_token_generator.make_token(user),
            'protocol':'http',
            }
            email = render_to_string(email_template_name, c)
            try:
                send_mail( subject,email, 'dvenila@gmail.com' , [user.email], fail_silently=False)
            except BadHeaderError:
                
                return HttpResponse('Invalid header found.')
            return redirect('accounts:password_reset_done')
        messages.info(request,'Invalid Email ID')
    return render(request,'auth/password_reset.html')


def password_reset_done(request):
    
    return render(request,'auth/password_reset_done.html')

def password_reset_confirm(request, *args, **kwargs):
    
    uidb64 = kwargs.get('uidb64')
    token = kwargs.get('token')
    return render(request,'auth/password_reset_confirm.html',{'token': token, 'uidb64': uidb64})

def password_reset_complete(request, *args, **kwargs):
    
    if request.method == 'POST':
        uidb64 = kwargs['uidb64']
        token = kwargs['token']
        password = request.POST.get("password")
        confirm_password  = request.POST.get("confirm_password")
        uid = urlsafe_base64_decode(uidb64)
        user = User._default_manager.get(pk=uid)

        if password==confirm_password and user is not None and default_token_generator.check_token(user, token):

            try:
                
                user.set_password(password)
                user.save()
                messages.success(request, 'Password Change SuccessFully')

            except (TypeError, ValueError, OverflowError, User.DoesNotExist):

                user = None
        else:
                
                messages.info(request,'password not matching or Password reset link has already been used. Check your email for a new link.')
               
                return render(request,'auth/password_reset_confirm.html',{'token': token, 'uidb64': uidb64})
        

    return render(request,'auth/password_reset_complete.html')



