from app import db
from datetime import datetime

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='conversations_as_buyer')
    farmer = db.relationship('User', foreign_keys=[farmer_id], backref='conversations_as_farmer')
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', 
                               cascade='all, delete-orphan', order_by='Message.created_at')
    
    def get_other_user(self, current_user_id):
        """Get the other person in this conversation."""
        return self.farmer if current_user_id == self.buyer_id else self.buyer
    
    def unread_count(self, user_id):
        """Get number of unread messages for a user."""
        return self.messages.filter_by(is_read=False).filter(Message.sender_id != user_id).count()
    
    @property
    def last_message(self):
        """Get the most recent message."""
        return self.messages.order_by(Message.created_at.desc()).first()
    
    def __repr__(self):
        return f'<Conversation #{self.id}>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')
    
    def __repr__(self):
        return f'<Message #{self.id}>'