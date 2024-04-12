from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

rooms = [
    {'id': 1, "name": "Learn Python with me"},
    {'id': 2, "name": "Graphic Design"},
    {'id': 3, "name": "Frontend Development"}
]

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.method == 'POST':
        # username = request.POST.get('username')
        # password = request.POST.get('password')
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            username = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')
            return redirect('home')
        user = authenticate(request,
                             username=username, 
                             password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password does not exist!')
            return redirect('home')
        
    context = {'page': page}
    return render(request, 'login_register.html', context)


def registerPage(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during Registration!")
            

    
    context = {'page': page, 'form': form}

    return render(request, 'login_register.html', context)



def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # rooms = Room.objects.all()
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(description__icontains=q) |
        Q(name__icontains=q) | 
        Q(host__username__icontains = q)
        )
    topics = Topic.objects.all()

    room_count = rooms.count()

    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {'rooms': rooms, 
               'topics': topics, 
               'room_count': room_count,
               'room_messages': room_messages
               }
    return render(request, 'home.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'user':user, 
               'rooms':rooms,
               'room_messages': room_messages,
               'topics': topics,
               'room_count': room_count
               }

    return render(request, 'profile.html', context)


def room(request,pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    partipants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
        user = request.user,
        room = room,
         body = request.POST.get('body')   
        )
        room.participants.add(request.user)

        return redirect('room', pk=room.id)
    
    context = {'room': room, 
               'room_messages': room_messages,
               'participants': partipants
               }
    return render(request, 'room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
           room = form.save(commit=False)
           room.host = request.user
           
           return redirect('home')
    context = {'form': form}
    return render(request,'room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    context = {'form': form}

    if request.user != room.host:
        return HttpResponse("You are not allowed here")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed here")
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': message})