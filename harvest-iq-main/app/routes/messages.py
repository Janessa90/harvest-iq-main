from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.message import Conversation, Message
from app.models.user import User
from datetime import datetime

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/')
@login_required
def inbox():
    """Show all conversations for the current user."""
    conversations = Conversation.query.filter(
        (Conversation.buyer_id == current_user.id) | 
        (Conversation.farmer_id == current_user.id)
    ).order_by(Conversation.last_message_at.desc()).all()
    
    return render_template('messages/inbox.html', conversations=conversations)


@messages_bp.route('/chat/<int:user_id>')
@login_required
def chat_with_user(user_id):
    """Start or continue a conversation with a specific user."""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.id == current_user.id:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('messages.inbox'))
    
    # Determine who is buyer and who is farmer
    if current_user.is_farmer and other_user.is_farmer:
        flash('Farmers cannot message each other.', 'warning')
        return redirect(url_for('messages.inbox'))
    
    if not current_user.is_farmer and not other_user.is_farmer:
        flash('Buyers cannot message each other.', 'warning')
        return redirect(url_for('messages.inbox'))
    
    buyer_id = current_user.id if not current_user.is_farmer else other_user.id
    farmer_id = current_user.id if current_user.is_farmer else other_user.id
    
    # Find or create conversation
    conversation = Conversation.query.filter_by(
        buyer_id=buyer_id,
        farmer_id=farmer_id
    ).first()
    
    if not conversation:
        conversation = Conversation(buyer_id=buyer_id, farmer_id=farmer_id)
        db.session.add(conversation)
        db.session.commit()
    
    # Mark all messages as read
    conversation.messages.filter_by(is_read=False).filter(
        Message.sender_id != current_user.id
    ).update({'is_read': True})
    db.session.commit()
    
    messages = conversation.messages.order_by(Message.created_at.asc()).all()
    
    return render_template('messages/chat.html', 
                          conversation=conversation, 
                          other_user=other_user,
                          messages=messages)


@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a message via AJAX."""
    conversation_id = request.json.get('conversation_id')
    message_text = request.json.get('message', '').strip()
    
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Verify user is part of this conversation
    if conversation.buyer_id != current_user.id and conversation.farmer_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        message=message_text
    )
    conversation.last_message_at = datetime.utcnow()
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'sender_id': message.sender_id,
            'message': message.message,
            'created_at': message.created_at.strftime('%I:%M %p'),
            'sender_name': current_user.full_name or current_user.username
        }
    })


@messages_bp.route('/mark-read/<int:conversation_id>', methods=['POST'])
@login_required
def mark_read(conversation_id):
    """Mark all messages in a conversation as read."""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    conversation.messages.filter_by(is_read=False).filter(
        Message.sender_id != current_user.id
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'success': True})