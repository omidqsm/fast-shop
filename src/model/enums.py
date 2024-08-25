from enum import Enum


class OrderStatus(Enum):
    created = 'created'
    paid = 'paid'
    processed = 'processed'
    sent = 'sent'
    delivered = 'delivered'
    cancelled = 'cancelled'
