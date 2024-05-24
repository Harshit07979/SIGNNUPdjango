from tokenize import generate_tokens
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from logpy import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .tokens import generate_token



# Create your views here.
def home(request):
    return render(request,"authentic/index.html")

    
def signup(request):
    if request.method == "POST":
        username=request.POST.get("username")
        fname=request.POST.get("fname")
        lname=request.POST.get("lname")
        email=request.POST.get("email")
        pass1=request.POST.get("pass1")
        pass2=request.POST.get("pass2")

        # Check if a user with this username already exists
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Please try some other username.")
            return redirect('home')
            # If the user exists, return an error message
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered! Please try another email.")
            return redirect('home')
        
        if len(username)>15:
            messages.error(request, "Username must be under 15 characters! Please try again.")

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match! Please try again.")

        if not username.isalnum():
                messages.error(request,"username is not alphanumeric")
                return redirect('home')
        
            # If the user does not exist, create the new user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name= fname
        myuser.last_name= lname
        myuser.is_active = False
        myuser.save()
        messages.success(request,"Your account has been successfully created We have sent you confirmation email \n Please confirm.")
        
        
        #welcoem Email

        subject = "Welcome to practice signup session"
        message = "hello  " + myuser.first_name + "!! \n" + "Welcome to Signup Practice Session \n Thnaks for visitinng site. Lets begin seesion \n Please confirm your mail by confirmation email to continue |n\n Thanking YOU \n HARSHIT GUPTA "
        from_email = settings.EMAIL_HOST_USER
        to_list =[myuser.email]
        send_mail(subject, message ,from_email ,to_list,fail_silently =True)

        # Email address confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Practice signup session - Let's start the session"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser),
        })
        email = EmailMessage(
             email_subject,
             message2,
             settings.EMAIL_HOST_USER,
             [myuser.email],
        )
        email.fail_silently = True
        email.send()
  



        return redirect('signin')
        


    return render(request,"authentic/signup.html")

def signin(request):
    if request.method == "POST":
        username=request.POST.get("username")
        pass1=request.POST.get("pass1")

        user = authenticate(username=username,password=pass1)

        if user is not None:
            login(request,user)
            fname= user.first_name
            return render(request,"authentic/index.html",{"fname":fname})

        else:
            messages.error(request,"Bad credentials")
            return redirect("home")    
    return render(request,"authentic/signin.html")


def signout(request):
    logout(request)
    messages.success(request,"Logged out successfully")
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser =None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active= True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')