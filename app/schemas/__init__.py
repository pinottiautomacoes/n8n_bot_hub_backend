from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.instance import Instance, InstanceCreate, InstanceUpdate, InstanceInDB
from app.schemas.bot import Bot, BotCreate, BotUpdate, BotInDB
from app.schemas.business_hour import BusinessHour, BusinessHourCreate, BusinessHourUpdate, BusinessHourInDB
from app.schemas.contact import Contact, ContactCreate, ContactUpdate, ContactInDB
from app.schemas.conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationInDB
from app.schemas.message import Message, MessageCreate, MessageInDB
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentInDB
from app.schemas.blocked_period import BlockedPeriod, BlockedPeriodCreate, BlockedPeriodUpdate, BlockedPeriodInDB
from app.schemas.webhook import WebhookMessage, N8nIncoming, N8nOutgoing

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Instance", "InstanceCreate", "InstanceUpdate", "InstanceInDB",
    "Bot", "BotCreate", "BotUpdate", "BotInDB",
    "BusinessHour", "BusinessHourCreate", "BusinessHourUpdate", "BusinessHourInDB",
    "Contact", "ContactCreate", "ContactUpdate", "ContactInDB",
    "Conversation", "ConversationCreate", "ConversationUpdate", "ConversationInDB",
    "Message", "MessageCreate", "MessageInDB",
    "Appointment", "AppointmentCreate", "AppointmentUpdate", "AppointmentInDB",
    "BlockedPeriod", "BlockedPeriodCreate", "BlockedPeriodUpdate", "BlockedPeriodInDB",
    "WebhookMessage", "N8nIncoming", "N8nOutgoing",
]

