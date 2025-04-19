from django.shortcuts import render,redirect
from django.http import HttpResponse
from portfolio.models import User

# Create your views here.

def login(request):
    if request.method == 'GET':
        if request.session.get('user_id'):
            return redirect('portfolio:index')
        return render(request, 'login.html')
    if request.method == 'POST':
        emailId = request.POST.get('email')
        password = request.POST.get('password')
        try: 
            user = User.objects.get(email_id=emailId)
            if user.check_password(password):
                request.session['user_id'] = user.user_id
                return redirect('portfolio:index')
            else:
                  return render(request, 'login.html', {'error': 'Incorrect password'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email id'})
        
    return render(request, 'login.html')

# def signup(request):
#     if request.method == 'POST':
#         emailId = request.POST.get('email')
#         password = request.POST.get('password')
#         name = request.POST.get('name')
#         user = User(name=name, emailId=emailId, password=password)
#         user.save()
#         return HttpResponse('User created successfully')
#     return render(request, 'signup.html')
# def index(request):
#     return render(request, 'portfolio/base.html')

def print_request(request):
    print("Method:", request.method)
    print("GET params:", request.GET)
    print("POST data:", request.POST)
    print("Uploaded files:", request.FILES)
    print("Path:", request.path)
    print("Full path:", request.get_full_path())
    print("User agent:", request.META.get('HTTP_USER_AGENT'))
    print("Client IP:", request.META.get('REMOTE_ADDR'))
    print("Cookies:", request.COOKIES)
    print("Session:", request.session)
    print("Logged-in user:", request.user)

def logout(request):
    request.session.flush()
    return redirect('portfolio:index')