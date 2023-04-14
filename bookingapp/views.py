from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

# def index(request):
#     return HttpResponse("book kar")

from django.shortcuts import render
from decimal import Decimal

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Flight, Booking
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal


import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context


def home(request):
    if request.user.is_authenticated:
        return render(request, 'myapp/home.html')
    else:
        return render(request, 'myapp/signin.html')


@login_required(login_url='signin')
def findflight(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        flight_list = Flight.objects.filter(source=source_r, dest=dest_r, date=date_r)
        if flight_list:
            return render(request, 'myapp/list.html', locals())
        else:
            context["error"] = "Sorry no flights availiable"
            return render(request, 'myapp/findflight.html', context)
    else:
        return render(request, 'myapp/findflight.html')



def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('flight_id')
        seats_r = int(request.POST.get('no_seats'))
        flight_obj = Flight.objects.get(id=id_r)
        if flight_obj:
            if flight_obj.rem >= int(seats_r):
                flight_name_r = flight_obj.flight_name
                cost = int(seats_r) * flight_obj.price
                source_r = flight_obj.source
                dest_r = flight_obj.dest
                nos_r = Decimal(flight_obj.nos)
                price_r = flight_obj.price
                date_r = flight_obj.date
                time_r = flight_obj.time
                username_r = request.user.username
                email_r = request.user.email
                userid_r = request.user.id
                rem_r = flight_obj.rem - seats_r
                Flight.objects.filter(id=id_r).update(rem=rem_r)
                book = Booking.objects.create(name=username_r, email=email_r, userid=userid_r, flight_name=flight_name_r,
                                           source=source_r, flight_id=id_r,
                                           dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                           status='BOOKED')
                print('------------book id-----------', book.id)
                # book.save()
                return render(request, 'myapp/bookings.html', locals())
            else:
                context["error"] = "Sorry select fewer number of seats"
                return render(request, 'myapp/findflight.html', context)

    else:
        return render(request, 'myapp/findflight.html')


@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('flight_id')
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Booking.objects.get(id=id_r)
            flight = Flight.objects.get(id=book.flight_id)
            rem_r = flight.rem + book.nos
            Flight.objects.filter(id=book.flight_id).update(rem=rem_r)

            Booking.objects.filter(id=id_r).update(status='CANCELLED')
            Booking.objects.filter(id=id_r).update(nos=0)
            return redirect(seebookings)
        except Booking.DoesNotExist:
            context["error"] = "Sorry You have not booked "
            return render(request, 'myapp/error.html', context)
    else:
        return render(request, 'myapp/findflight.html')

@login_required(login_url='signin')
def deleterecord(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('flight_idd')
        try:
            book = Booking.objects.get(id=id_r)

            flight = Flight.objects.get(id=book.flight_id)
            rem_r = flight.rem + book.nos
            Flight.objects.filter(id=book.flight_id).update(rem=rem_r)



            Booking.objects.filter(id=id_r).delete()

            Booking.objects.filter(id=id_r).update(nos=0)
            return redirect(seebookings)


        except Booking.DoesNotExist:
            context["error"] = "Sorry You have not booked "
            return render(request, 'myapp/error.html', context)
    else:
        return render(request, 'myapp/findflight.html')

    # context = {}
    # if request.method == 'POST':
    #     id_r = request.POST.get('flight_id')
    #     try:
    #         bookid = Booking.objects.get(id=id_r)
    #         flight = Flight.objects.get(id=bookid.flight_id)
    #         left = bookid + flight
    #         Flight.objects.filter(id=bookid.flight_id).delete(left)
    #         return redirect(seebookings)
    #     except Booking.DoesNotExist:
    #         context["error"] = "Sorry You have not booked "







@login_required(login_url='signin')
def seebookings(request,new={}):
    context = {}
    id_r = request.user.id
    book_list = Booking.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'myapp/booklist.html', locals())
    else:
        context["error"] = "Sorry no flight booked"
        return render(request, 'myapp/findflight.html', context)


def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')
        user = User.objects.create_user(name_r, email_r, password_r, )
        if user:
            login(request, user)
            return render(request, 'myapp/thank.html')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signup.html', context)
    else:
        return render(request, 'myapp/signup.html', context)


def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            # username = request.session['username']
            context["user"] = name_r
            context["id"] = request.user.id
            return render(request, 'myapp/success.html', context)
            # return HttpResponseRedirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)


def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'myapp/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return




#
# def delete(request, id):
#     data = get_object_or_404(CRUD, id=id)
#     data.delete()
#     return redirect('home')
def download_pdf_view(request,pk):
    book = Booking.objects.filter(id=pk)
    print(book)
    #dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={

        'id':book[0].flight_id,
        'Flightname':book[0].flight_name,
        'tag':book[0].flight,
        'serialno':book[0].source,
        'location':book[0].dest,
        'issuedescription':book[0].price,
        'assignedengineer':book[0].id,
        'issueraisedon':book[0].id,
        'issuesolvedon':book[0].id,
        'comments':book[0].id,
    }
    return render_to_pdf('myapp/download_bill.html',dict)
