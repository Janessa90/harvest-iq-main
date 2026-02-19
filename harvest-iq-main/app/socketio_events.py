from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models.message import Message, Conversation
from datetime import datetime


@socketio.on('connect')
def handle_connect():
    """User connects to websocket."""
    if current_user.is_authenticated:
        print(f'User {current_user.username} connected')


@socketio.on('disconnect')
def handle_disconnect():
    """User disconnects from websocket."""
    if current_user.is_authenticated:
        print(f'User {current_user.username} disconnected')


@socketio.on('join_conversation')
def handle_join_conversation(data):
    """User joins a conversation room."""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        room = f'conversation_{conversation_id}'
        join_room(room)
        print(f'User {current_user.username} joined {room}')


@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """User leaves a conversation room."""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        room = f'conversation_{conversation_id}'
        leave_room(room)
        print(f'User {current_user.username} left {room}')


@socketio.on('send_message')
def handle_send_message(data):
    """Send a message in real-time."""
    conversation_id = data.get('conversation_id')
    message_text = data.get('message', '').strip()
    
    if not message_text or not conversation_id:
        return
    
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return
    
    # Verify user is part of conversation
    if conversation.buyer_id != current_user.id and conversation.farmer_id != current_user.id:
        return
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        message=message_text
    )
    conversation.last_message_at = datetime.utcnow()
    
    db.session.add(message)
    db.session.commit()
    
    # Broadcast to room
    room = f'conversation_{conversation_id}'
    emit('new_message', {
        'id': message.id,
        'sender_id': message.sender_id,
        'sender_name': current_user.full_name or current_user.username,
        'message': message.message,
        'created_at': message.created_at.strftime('%I:%M %p'),
        'is_mine': True
    }, room=room, include_self=False)
    
    # Send to sender for confirmation
    emit('message_sent', {
        'id': message.id,
        'sender_id': message.sender_id,
        'sender_name': current_user.full_name or current_user.username,
        'message': message.message,
        'created_at': message.created_at.strftime('%I:%M %p'),
        'is_mine': True
    })


@socketio.on('typing')
def handle_typing(data):
    """Broadcast typing indicator."""
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing', False)
    
    if conversation_id:
        room = f'conversation_{conversation_id}'
        emit('user_typing', {
            'user_id': current_user.id,
            'username': current_user.full_name or current_user.username,
            'is_typing': is_typing
        }, room=room, include_self=False)