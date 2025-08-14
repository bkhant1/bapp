from ninja import Router

router = Router()


@router.get("/")
def list_messages(request):
    """List messages - placeholder"""
    return {"message": "Messaging API - Coming Soon"}


@router.post("/send")
def send_message(request):
    """Send message - placeholder"""
    return {"message": "Message sent - Coming Soon"} 