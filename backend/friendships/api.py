from ninja import Router

router = Router()


@router.get("/")
def list_friendships(request):
    """List friendships - placeholder"""
    return {"message": "Friendships API - Coming Soon"}


@router.post("/request")
def send_friend_request(request):
    """Send friend request - placeholder"""
    return {"message": "Friend request sent - Coming Soon"}
