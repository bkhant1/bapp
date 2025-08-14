from django.db import models
from django.conf import settings


class BookExchange(models.Model):
    """Book exchange between users"""
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('returned', 'Returned'),  # For temporary exchanges
    ]
    
    EXCHANGE_TYPE_CHOICES = [
        ('permanent', 'Permanent Exchange'),
        ('temporary', 'Temporary Loan'),
    ]
    
    # Users involved
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='exchange_requests_sent'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='exchange_requests_received'
    )
    
    # Books involved
    requested_book = models.ForeignKey(
        'books.UserBook', 
        on_delete=models.CASCADE, 
        related_name='exchange_requests'
    )
    offered_book = models.ForeignKey(
        'books.UserBook', 
        on_delete=models.CASCADE, 
        related_name='exchange_offers',
        blank=True, 
        null=True
    )
    
    # Exchange details
    exchange_type = models.CharField(max_length=20, choices=EXCHANGE_TYPE_CHOICES, default='permanent')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    message = models.TextField(max_length=1000, blank=True)
    
    # For temporary exchanges
    loan_duration_days = models.PositiveIntegerField(blank=True, null=True)
    return_by_date = models.DateField(blank=True, null=True)
    
    # Meeting details
    meeting_location = models.TextField(blank=True)
    meeting_date = models.DateTimeField(blank=True, null=True)
    shipping_address = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'exchanges_book_exchange'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Exchange: {self.requester.display_name} -> {self.requested_book.book.title}"


class ExchangeRating(models.Model):
    """Rating and feedback for completed exchanges"""
    exchange = models.ForeignKey(BookExchange, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exchange_ratings_given')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exchange_ratings_received')
    
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    
    # Specific feedback areas
    communication_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    book_condition_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    timeliness_rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True)
    
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exchanges_rating'
        unique_together = ['exchange', 'rater']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rating for exchange {self.exchange.id} by {self.rater.display_name}"


class ExchangeMessage(models.Model):
    """Messages between users about an exchange"""
    exchange = models.ForeignKey(BookExchange, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exchange_messages_sent')
    content = models.TextField()
    
    # Message metadata
    is_system_message = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'exchanges_message'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.display_name} in exchange {self.exchange.id}"
