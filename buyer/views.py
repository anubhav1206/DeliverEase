from django.shortcuts import render
from userAuth.models import Buyer,  Seller
from .models import Job
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import random
from django.urls import reverse


def index(request):
    '''This function allows the seller to visit the home page via GET method'''

    email = request.GET.get('email', 'None') #gets the email of the buyer passed in the get request


    ## this is the block  that verifies the user is actually logged into the session
    if email == 'None':
        if 'buyer_id' in request.session:
            pass
        else:
            return HttpResponseRedirect('/auth/login')


    try:
        buyer = Buyer.objects.get(email=email)
    except:
        id = request.session['buyer_id']
        buyer = Buyer.objects.get(pk=id)
    else:
        request.session['buyer_id'] = buyer.id

    return render(request, 'buyer/buyer_homepage.html')


def add_job(request):
    '''This function allows the buyer to visit the  page via 2 methods:
    1) GET : The seller is shown  the job form to create a new job
    2) POST : The details entered are extracted and a job is created.
    '''
    if request.method == 'POST':
        # gets the id of the buyer in the session
        id = request.session['buyer_id']
        print(f'id {id}')
        current_buyer = Buyer.objects.get(id=id)

        # retrieves the data entered by the user in the job form
        pickup_address = request.POST['pickup_address']
        pickup_time1 = request.POST['pickup_time']
        pickup_date = request.POST['pickup_date']
        delivery_address = request.POST['delivery_address']
        delivery_time1 = request.POST['delivery_time']
        delivery_date = request.POST['delivery_date']
        delivery_pincode = request.POST['delivery_pincode']
        pickup_pincode = request.POST['pickup_pincode']
        # makes sure the pincode is a int and proceeds to save the job
        try:
            delivery_pincode = int(delivery_pincode)
            pickup_pincode = int(pickup_pincode)
        except:
            return HttpResponseRedirect(reverse('add_job'))
        try:
            new_job = Job(pickup_address=pickup_address, pickup_time=pickup_time1,
                          delivery_address=delivery_address, pickup_pincode=pickup_pincode,
                          delivery_time=delivery_time1, created_by=current_buyer,
                          delivery_pincode=delivery_pincode)
        except:
            return HttpResponseRedirect(reverse('add_job'))
        else:
            print(new_job)
            new_job.save()
        return HttpResponseRedirect (reverse('my_orders'))

    elif request.method == 'GET':

        if 'buyer_id' in request.session:
            print(request.session['buyer_id'])

        else:
            return HttpResponseRedirect('/auth/login')

        return render(request, 'buyer/add_job.html')



def my_orders(request):
    '''This function allows the buyer to visit the  page via 2 methods:
    1) GET : The buyer is shown all the jobs created by him
    2) POST : The job_id of the job selected by the buyer is retrieved and saved in the session.
    '''
    if request.method == 'POST':
        job_id = request.POST['job_id']
        request.session['job_id'] = job_id
        return HttpResponseRedirect (reverse('check_order'))
    else:
        if 'buyer_id' in request.session:
            print(request.session['buyer_id'])
        else:
            return HttpResponseRedirect('/auth/login')

        try:
            del request.session['job_id'] # deletes a job_id if exsts in the session
        except:
            pass
        id = request.session['buyer_id']
        buyer =  Buyer.objects.filter(id=id)
        all_job = Job.objects.filter(created_by=id)
        return render(request, 'buyer/my_orders.html', {
            'jobs': all_job, 'buyer': buyer
        })


def check_order(request):
    '''This function allows the buyer to visit the  page via 2 methods:
    1) GET : The buyer is shown the details of the job
    2) POST : The job_id of the job selected by the buyer is retrieved and saved in the session.
    '''

    if request.method == 'POST':
        return HttpResponseRedirect (reverse('get_otp'))

    if 'buyer_id' in request.session:
        pass
    else:
        return HttpResponseRedirect('/auth/login')
    ## checks if a job_id exists in the session
    try:
        job_id = request.session['job_id']
    except:
        return HttpResponseRedirect(reverse('my_orders'))
    print(job_id)
    job = Job.objects.get(pk=job_id)
    return render(request, 'buyer/check_order.html', {
        'job': job
    })


def get_otp(request):
    '''This function allows the buyer to visit the  page via 2 methods:
        1) GET : An otp is generated and saved with the job. The buyer is shown the otp of the job if the job is assigned
        2) POST : The review and rating by the buyer regarding the service is obtained and  saved.
        '''

    if request.method == 'POST':
        job_id = request.session['job_id']
        get_job = Job.objects.get(id=job_id)
        try:
            review = request.POST['review']
            rating = request.POST['rating']
            get_job.review  = review
            get_job.rating = rating
            get_job.save()
        except:
            print(get_job)
            print(review, rating)
            return HttpResponseRedirect(reverse('get_otp'))
        return render(request, 'buyer/thank_you.html')
    if 'buyer_id' in request.session:
        pass
    else:
        return HttpResponseRedirect('/auth/login')

    job_id = request.session['job_id']
    get_job = Job.objects.get(id=job_id)
    try:
        seller_id = get_job.assigned_to.id
        seller = Seller.objects.filter(pk=seller_id)

    except:
        return render(request, 'buyer/final_page.html')
    else:
        otp = random.randint(100000, 999999)
        print(otp)
        get_job.otp = otp
        get_job.save()

        print(f'job otp {get_job.otp}')
        return render(request, 'buyer/final_page.html', {
        'seller': seller,
        'otp': otp,
        'job': get_job
        }   )