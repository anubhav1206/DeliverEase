from django.shortcuts import render
from .models import Buyer, Seller
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import login, authenticate

# Create your views here.
def check_user_exists(email):
    '''This function makes sure that the user who is trying to register with a email
    doesn't exits already in the table '''
    buyer_exists = Buyer.objects.filter(email=email).exists()
    seller_exists = Seller.objects.filter(email=email).exists()
    if buyer_exists or seller_exists:
        return True
    else:
        return False


def user_signup(username, password1, password2, address, phoneNo, email, user_type, experience='None'):
    '''This function is used to register the user on our website'''
    user = check_user_exists(email=email)

    if (user == True):
        print(f'user: {user}')

        error_message =  'Account already exists.'
        url = reverse('login') # this gives the url saved with the name "login" from urls.py
        print(url)
        return url, error_message
    # this make sure that all the parameters of lenght are met before registering the user
    elif len(email) < 4:
        error_message = 'Email must be greater than 3 characters.'
    elif len(username) < 2:
        error_message = 'First name must be greater than 1 character.'
    elif len(password1) < 7:
        error_message = 'Password must be at least 7 characters.'
    elif password1 != password2:
        error_message = 'Passwords don\'t match.'

    elif (user == False):
        if user_type == 'Seller':
            ## adds the user to the seller table
            new_user = Seller(email=email, name=username,
                              password=password1, experience=experience,
                              phoneNo=phoneNo, address=address)
            url = '/seller/home'
            error_message = 'Account created successfully'
        elif user_type == 'Buyer':
            ## adds the user to the buyer table
            new_user = Buyer(email=email, name=username, password=password1,
                             phoneNo=phoneNo, address=address)
            url = '/buyer/home'
            error_message = 'Account created successfully'
        url += f'/?email={email}'## adds the email of the user in the actual url to create a
        # get request to the home page so that user email is accessible

        new_user.save()
        print(f"new user {new_user}")
        print(f"url {url}")
        print(f'message: {error_message}')
        return url, error_message


def user_login(email, password):
    '''This function is used to login the user on our website'''
    try:
        user = Seller.objects.get(email=email)
        user_type = 'Seller'
    except Seller.DoesNotExist:
        try:
            user = Buyer.objects.get(email=email)
            user_type = 'Buyer'
        except Buyer.DoesNotExist:
            # Handle the case when no user with the given email is found in both Seller and Buyer models
            user = None
            user_type = None

    print(user_type, user)
    if user:
        if (user.password == password):
            message = 'Logged in successfully!'
            if user_type == 'Seller':
                url = '/seller/home'

            if user_type == 'Buyer':
                url = '/buyer/home'
            url  += f'/?email={email}'
            return url, message
        else:
            url = '/auth/login'
            message = 'Incorrect password, try again.'
            return url, message
    if user_type == 'None':
        url = '/auth/login'
        message = 'Account does not exist.'
        return url, message


def buyer_signup(request):
    '''This function is executed on the buyer signup page '''

    if request.method == 'POST':
        # retrives all the details filled in by the user
        username = request.POST['fullName']
        password = request.POST['password']
        confPassword = request.POST['confirmPassword']
        phoneNo = request.POST['phoneNo']
        email = request.POST['email']
        address = request.POST['address']
        ## register the buyer on our web
        try:
            url, message = user_signup(username=username, password1=password, password2=confPassword, phoneNo=phoneNo,
                        email=email, address=address, user_type='Buyer')
            messages.warning(request, message)
            print(message)
        except Exception as error:
            print(error)
            messages.error(request, 'Please fill all the details')


            return HttpResponseRedirect (reverse('buyer_signup'))

        return HttpResponseRedirect (url)
## deletes the different details stored in the session
    try:
        del request.session['buyer_id']

    except:
        try:
            del request.session['id']
        except:
            pass


    return render(request, 'userAuth/buyerSignup.html')

def seller_signup(request):
    '''This function is executed on the seller signup page '''

    if request.method == 'POST':
        username = request.POST['fullName']
        password = request.POST['password']
        confPassword = request.POST['confirmPassword']
        phoneNo = request.POST['phoneNo']
        email = request.POST['email']
        workExperience = request.POST['workExperience']
        address = request.POST['address']
        try:
            url, message = user_signup(username=username, password1=password, password2=confPassword, phoneNo=phoneNo,
                        email=email, address=address, user_type='Seller', experience=workExperience)
        except:
            return  HttpResponseRedirect (reverse('seller_signup'))
        messages.warning(request, message)
        return HttpResponseRedirect(url)

    try:
        del request.session['buyer_id']

    except:
        try:
            del request.session['id']
        except:
            pass

    return render(request, 'userAuth/sellerSignup.html')


def login_user(request):
    '''This function is executed on the login page '''

    if request.method == 'POST':
        # retrives the data entered by the user
        email = request.POST['email']
        password = request.POST['password']

        print(f" 1{email}, {password}")
        ## authenticates the user and redirect it to the actual page
        try:
            url, message = user_login(email=email, password=password)
        except:
            return HttpResponseRedirect(reverse('login'))
        messages.warning(request, message)
        print(f'url: {url}')
        return HttpResponseRedirect (url)
    try:
        del request.session['id']
    except:
        try:
            del request.session['buyer_id']

        except:
            pass
        pass
    return render(request, 'userAuth/login.html')
