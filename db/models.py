from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text, Boolean, Enum, func
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class ChatType(enum.Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    is_bot = Column(Boolean, default=False, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    current_profile_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_chat_id = Column(BigInteger, unique=True, nullable=False, index=True)
    type = Column(Enum(ChatType), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    invite_link = Column(String(255), nullable=True)
    bio = Column(String(255), nullable=True)
    photo_file_id = Column(String(255), nullable=True)
    business_connection_id = Column(Integer, ForeignKey("business_connections.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="chat")
    business_connection = relationship("BusinessConnection", back_populates="chats")

    def __repr__(self):
        return f"<Chat(id={self.id}, telegram_chat_id={self.telegram_chat_id}, type={self.type})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_message_id = Column(BigInteger, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reply_to_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    text = Column(Text, nullable=True)
    sent_by_bot = Column(Boolean, default=False, nullable=False)
    business_connection_id = Column(Integer, ForeignKey("business_connections.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")
    replies = relationship("Message", remote_side=[id], backref="parent")
    business_connection = relationship("BusinessConnection", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, telegram_message_id={self.telegram_message_id}, text={self.text[:30] if self.text else None})>"


class BusinessConnection(Base):
    __tablename__ = "business_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_id = Column(String(255), unique=True, nullable=False, index=True)
    user_chat_id = Column(BigInteger, nullable=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="business_connection")
    chats = relationship("Chat", back_populates="business_connection")

    def __repr__(self):
        return f"<BusinessConnection(id={self.id}, connection_id={self.connection_id}, user_chat_id={self.user_chat_id})>"
