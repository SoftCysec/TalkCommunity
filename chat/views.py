from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from chat.models import ChatRoom, ChatMessage
from chat.serializers import ChatRoomSerializer, ChatMessageSerializer

@csrf_exempt
@api_view(['POST'])
def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_rooms(request):
    chat_rooms = request.user.chat_rooms.all()
    serializer = ChatRoomSerializer(chat_rooms, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    serializer = ChatRoomSerializer(data=request.data)
    if serializer.is_valid():
        chat_room = serializer.save()
        chat_room.members.add(request.user)
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, room_id):
    chat_room = ChatRoom.objects.get(id=room_id)
    messages = chat_room.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_chat_message(request, room_id):
    chat_room = ChatRoom.objects.get(id=room_id)
    serializer = ChatMessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save(sender=request.user, room=chat_room)
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)
