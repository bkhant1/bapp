from django.conf import settings
from django.db import models


class PrivateMessage(models.Model):
    """Private messages between users"""

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField()
    subject = models.CharField(max_length=200, blank=True)

    # Message metadata
    is_read = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_recipient = models.BooleanField(default=False)

    # Optional book reference
    related_book = models.ForeignKey(
        "books.Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_messages",
    )

    # Thread reference for replies
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "messaging_private_message"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Message from {self.sender.display_name} to {self.recipient.display_name}"
        )

    def mark_as_read(self):
        if not self.is_read:
            from django.utils import timezone

            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class BookDiscussion(models.Model):
    """Public discussions about books"""

    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="discussions"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_discussions",
    )

    # Discussion settings
    is_public = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)

    # Moderation
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0)
    participants_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messaging_book_discussion"
        ordering = ["-is_pinned", "-last_activity_at"]

    def __str__(self):
        return f"Discussion: {self.title} about {self.book.title}"


class DiscussionComment(models.Model):
    """Comments in book discussions"""

    discussion = models.ForeignKey(
        BookDiscussion, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="discussion_comments",
    )
    content = models.TextField()

    # Threading support
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    # Moderation
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_comments", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "messaging_discussion_comment"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.display_name} in {self.discussion.title}"

    def save(self, *args, **kwargs):
        # Update discussion last activity
        if not self.pk:  # New comment
            from django.utils import timezone

            self.discussion.last_activity_at = timezone.now()
            self.discussion.save(update_fields=["last_activity_at"])

        super().save(*args, **kwargs)


class MessageAttachment(models.Model):
    """File attachments for messages"""

    ATTACHMENT_TYPES = [
        ("image", "Image"),
        ("document", "Document"),
        ("other", "Other"),
    ]

    message = models.ForeignKey(
        PrivateMessage, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="message_attachments/")
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # in bytes
    file_type = models.CharField(
        max_length=10, choices=ATTACHMENT_TYPES, default="other"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messaging_attachment"

    def __str__(self):
        return f"Attachment: {self.file_name}"

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)


class Conversation(models.Model):
    """Conversation threads between users"""

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    last_message = models.ForeignKey(
        PrivateMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "messaging_conversation"
        ordering = ["-updated_at"]

    def __str__(self):
        participant_names = [p.display_name for p in self.participants.all()[:2]]
        return f"Conversation: {', '.join(participant_names)}"
