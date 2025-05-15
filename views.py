from ast import Or
from email import message
import imp
import re
from tokenize import group
from unicodedata import category
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from .sendemail import *
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.core.mail import EmailMessage
import random
import math
import datetime

from django.conf import settings

# Create your views here.
def Home(request):
    return render(request,'carousel.html')

def About(request):
    return render(request,'about.html')

def Contact(request):
    return render(request,'contact.html')

def Gallery(request):
    return render(request,'gallery.html')

def Login_User(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        sign = ""
        if not user.is_staff and user:
            login(request, user)
            messages.success(request, "Logged in Successfully")
            return redirect('home')
        else:
            messages.success(request, "Invalid user")
    return render(request, 'login.html')

def admin_login(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        sign = ""
        if user.is_staff:
            login(request, user)
            messages.success(request, "Logged in Successfully")
            return redirect('admin_home')
        else:
            messages.success(request, "Invalid user")
    return render(request, 'admin_login.html')

def Signup_User(request):
    cat = Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        d = request.POST['dob']
        con = request.POST['contact']
        add = request.POST['add']
        group = request.POST['group']
        pin = request.POST['pincode']
        im = request.FILES['image']
        cat = Category.objects.get(id=group)
        user = User.objects.create_user(email=e, username=u, password=p, first_name=f,last_name=l)
        UserProfile.objects.create(user=user,contact=con,address=add,image=im,dob=d, blood_group=cat,password=p, pincode=pin)
        messages.success(request, "Registration Successful")
        return redirect('login')
    return render(request,'register.html', {'cat':cat})

def Logout(request):
    logout(request)
    return redirect('home')

def Change_Password(request):
    user = User.objects.get(username=request.user.username)
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            messages.success(request, "Password changed successfully")
        else:
            messages.success(request, "New password and confirm password are not same.")
        return redirect('home')
    return render(request,'change_password.html')


def view_user(request):
    data = UserProfile.objects.all()
    d = {'data':data}
    return render(request,'view_user.html',d)

def edit_profile(request,pid):
    data = UserProfile.objects.get(id=pid)
    cat = Category.objects.all()
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        e = request.POST['email']
        con = request.POST['contact']
        add = request.POST['add']
        cat = request.POST['group']
        try:
            im = request.FILES['image']
            data.image=im
            data.save()
        except:
            pass
        data.user.first_name = f
        data.user.last_name = l
        data.user.email = e
        data.contact = con
        bl = Category.objects.get(id=cat)
        data.blood_group = bl
        data.address = add
        data.user.save()
        data.save()
        messages.success(request, "User Profile updated")
        if request.user.is_staff:
            return redirect('view_user')
        else:
            return redirect('profile')
    d = {'data':data, 'cat':cat}
    return render(request,'edit_profile.html',d)

def profile(request):
    pro = UserProfile.objects.get(user=request.user)
    return render(request, "profile.html", {'pro':pro})

def add_category(request):
    if request.method == 'POST':
        n = request.POST['name']
        Category.objects.create(name=n)
        messages.success(request, "Category created successfully")
        return redirect('view_category')
    return render(request, 'add_category.html')

def edit_category(request, pid):
    data = Category.objects.get(id=pid)
    if request.method == 'POST':
        n = request.POST['name']
        data.name=n
        data.save()
        messages.success(request, "Category Updated successfully")
        return redirect('view_category')
    return render(request, 'edit_category.html',{'data':data})

def view_category(request):
    data = Category.objects.all()
    return render(request, 'view_category.html', {'data':data})

def delete_category(request, pid):
    data = Category.objects.get(id=pid)
    data.delete()
    messages.success(request, "Category deleted successfully")
    return redirect('view_category')

def search_blood(request):
    userprofile = UserProfile.objects.get(user=request.user)
    cat = Category.objects.get(id=userprofile.blood_group.id)
    data = Blood_Donation.objects.filter(status="Approved", blood_group=cat).exclude(purpose="Request for Blood", user=userprofile)
    if request.method == "POST":
        place = request.POST['place']
        unit = request.POST['unit']
        desc = request.POST['desc']
        bg = request.POST['group']
        
        cat = Category.objects.get(name=bg)
        user = UserProfile.objects.get(user=request.user)
        Blood_Donation.objects.create(blood_group=cat, user=user, purpose="Request for Blood", status="Pending", place=place, blood_units=unit, description=desc,)
        messages.success(request, "Request Generated.")
        return redirect('search_blood')
    all_cat = Category.objects.all()
    return render(request, 'search_blood.html', {'data':data, 'cat':all_cat})

def donate_blood(request):
    user = UserProfile.objects.get(user=request.user)
    mydonate = Blood_Donation.objects.filter(user=user, purpose="Blood Donor").last()
    if mydonate and mydonate.donation_date and datetime.datetime.today().month - mydonate.donation_date.month < 3:
        messages.success(request, "You are not able to donate now. You can donate after 3 months of your previous.")
        return redirect('home')
    if request.method == "POST":
        bg = request.POST['group']
        place = request.POST['place']

        # unit = request.POST['unit']
        # desc = request.POST['desc']
        bp = request.POST['bp']
        
        
        hiv = False
        try:
            hiv = request.POST['hiv']
            if hiv == 'on':
                hiv = True
        except:
            pass
            
        hepb = False
        try:
            hepb = request.POST['hepb']
            if hepb == 'on':
                hepb = True
        except:
            pass

        hepc = False
        try:
            hepc = request.POST['hepc']
            if hepc == 'on':
                hepc = True
        except:
            pass
            
        syphilis = False
        try:
            syphilis = request.POST['syphilis']
            if syphilis == 'on':
                syphilis = True
        except:
            pass


        cat = Category.objects.get(name=bg)
        user = UserProfile.objects.get(user=request.user)
        data = Blood_Donation.objects.create(blood_group=cat, user=user, purpose="Blood Donor", status="Pending", place=place, blood_pressure=bp, hiv=hiv, hapetitis_c=hepc, hapetitis_b=hepb, syphilis=syphilis)
        messages.success(request, "Added Your Detail.")
        return redirect('donate_blood')
    all_cat = Category.objects.all()
    return render(request, 'donate_blood.html', {'cat':all_cat})

def request_blood(request):
    mydata = request.GET.get('action',0)
    data = Blood_Donation.objects.filter(purpose="Request for Blood")
    if mydata:
        data = data.filter(status=mydata)
    return render(request, 'request_blood.html', {'data':data})

def donator_blood(request):
    mydata = request.GET.get('action',0)
    data = Blood_Donation.objects.filter(purpose="Blood Donor")
    if mydata:
        data = data.filter(status=mydata)
    return render(request, 'donator_blood.html', {'data':data})

def change_status(request,pid):
    data = Blood_Donation.objects.get(id=pid)
    url = request.GET.get('data')
    if data.status == "Approved":
        data.status = "Pending"
        data.save()
    else:
        if 'request_blood' in url:
            data.recieve_date = datetime.datetime.today()
        if 'donator_blood' in url:
            data.donation_date = datetime.datetime.today()
        data.status = "Approved"
        data.save()
    return HttpResponseRedirect(url)

def admin_home(request):
    data = UserProfile.objects.all()
    order = Order.objects.all()
    donate = Blood_Donation.objects.filter(purpose="Blood Donor")
    req = Blood_Donation.objects.filter(purpose="Request for Blood")

    d = {'data':data.count(), 'order':order.count(), 'req':req.count(), 'donate':donate.count()}
    return render(request,'admin_home.html',d)

def history(request):
    user = UserProfile.objects.get(user=request.user)
    data = Blood_Donation.objects.filter(user=user)
    return render(request, "history.html", {'data':data})

def pay_now(request, pid):
    total = 2000
    user = UserProfile.objects.get(user=request.user)
    blood = Blood_Donation.objects.get(id=pid)
    if request.method == "POST":
        messages.success(request, "Ordered Succesfully")
        return redirect("my_order")
    if request.GET.get('get') == "1":
        messages.success(request, "Ordered Succesfully")
        return redirect("my_order")
    return render(request, "payment2.html",{'total':total})

def confirm_detail(request, pid):
    user = UserProfile.objects.get(user=request.user)
    blood = Blood_Donation.objects.get(id=pid)
    if request.method == "POST":
        unit = request.POST['unit']
        desc = request.POST['desc']
        Order.objects.create(user=user, blood_donation=blood, amount=2000, status="Pending", description=desc, blood_units=unit)
        return redirect("pay_now", pid)
    return render(request, "paynow.html")

def my_order(request):
    user = UserProfile.objects.get(user=request.user)
    data = Order.objects.filter(user=user)
    return render(request, "my_order.html",{'data':data})

def all_order(request):
    data = Order.objects.filter()
    return render(request, "all_order.html",{'data':data})

def delete_order(request, pid):
    data = Order.objects.get(id=pid)
    data.delete()
    messages.success(request, "Order deleted successfully")
    return redirect('my_order')

def delete_user(request, pid):
    data = UserProfile.objects.get(id=pid)
    data.delete()
    messages.success(request, "User deleted successfully")
    return redirect('view_user')


def change_order_status(request,pid):
    data = Order.objects.get(id=pid)
    if data.status == "Delivered":
        data.status = "Pending"
        data.save()
    else:
        data.status = "Delivered"
        data.save()
    messages.success(request, "Order Status changed successfully")
    return redirect('all_order')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = UserProfile.objects.get(user__email=email)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'User not found.'})

        # Generate random OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        user.otp = otp
        user.save()

        # Send OTP via email
        if sendemail(user.user.email, user.user.first_name, otp):
            return JsonResponse({'status': True, 'message': 'OTP sent successfully.'})
        else:
            return JsonResponse({'status': False, 'message': 'Failed to send OTP.'})
    return render(request, 'forgot_password.html')


def check_password(request):
    if request.method == "POST":
        email = request.POST['email']
        otp = request.POST['password']
        try:
            user = UserProfile.objects.get(user__email=email)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'User not found.'})

        if user.otp == otp:
            # Retrieve the user's password
            password = user.password  # Make sure this is securely stored/encrypted
            if sendemail(user.user.email, user.user.first_name, f"Your password is: {password}"):
                return JsonResponse({'status': True, 'message': 'Password sent to your email.'})
            else:
                return JsonResponse({'status': False, 'message': 'Failed to send email.'})
        else:
            return JsonResponse({'status': False, 'message': 'Invalid OTP.'})
    return render(request, 'check_password.html')


def order_detail(request, pid):
    order = Order.objects.get(id=pid)
    d = {'order':order}
    return render(request, 'order_detail.html', d)

def request_detail(request, pid):
    order = Blood_Donation.objects.get(id=pid)
    d = {'order':order}
    return render(request, 'request_detail.html', d)