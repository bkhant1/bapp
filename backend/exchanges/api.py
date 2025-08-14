from ninja import Router

router = Router()


@router.get("/")
def list_exchanges(request):
    """List book exchanges - placeholder"""
    return {"message": "Exchanges API - Coming Soon"}


@router.post("/request")
def request_exchange(request):
    """Request book exchange - placeholder"""
    return {"message": "Exchange requested - Coming Soon"} 