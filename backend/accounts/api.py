from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from pydantic import BaseModel
from typing import List
import jwt
from datetime import datetime, timedelta
from django.conf import settings

from .models import User, UserProfile

router = Router()


# Pydantic schemas
class UserRegisterSchema(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    confirm_password: str


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserSchema(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    bio: str
    location: str
    is_profile_public: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# JWT Bearer token authentication
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.JWT_SETTINGS['SECRET_KEY'], algorithms=[settings.JWT_SETTINGS['ALGORITHM']])
            user_id = payload.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                return user
        except (jwt.InvalidTokenError, User.DoesNotExist):
            pass
        return None


auth = JWTAuth()


def create_tokens(user):
    """Create access and refresh tokens for a user"""
    access_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_SETTINGS['ACCESS_TOKEN_EXPIRE_MINUTES'])
    }
    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=settings.JWT_SETTINGS['REFRESH_TOKEN_EXPIRE_DAYS'])
    }
    
    access_token = jwt.encode(access_payload, settings.JWT_SETTINGS['SECRET_KEY'], algorithm=settings.JWT_SETTINGS['ALGORITHM'])
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SETTINGS['SECRET_KEY'], algorithm=settings.JWT_SETTINGS['ALGORITHM'])
    
    return access_token, refresh_token


@router.post("/register", response=TokenSchema)
def register(request, data: UserRegisterSchema):
    """Register a new user"""
    if data.password != data.confirm_password:
        return {"error": "Passwords do not match"}, 400
    
    if User.objects.filter(email=data.email).exists():
        return {"error": "Email already exists"}, 400
    
    if User.objects.filter(username=data.username).exists():
        return {"error": "Username already exists"}, 400
    
    # Create user
    user = User.objects.create(
        email=data.email,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        password=make_password(data.password)
    )
    
    # Create user profile
    UserProfile.objects.create(user=user)
    
    # Generate tokens
    access_token, refresh_token = create_tokens(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response=TokenSchema)
def login(request, data: UserLoginSchema):
    """Login user"""
    user = authenticate(request, username=data.email, password=data.password)
    
    if not user:
        return {"error": "Invalid credentials"}, 401
    
    # Generate tokens
    access_token, refresh_token = create_tokens(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response=UserSchema, auth=auth)
def get_current_user(request):
    """Get current user profile"""
    return request.auth

@router.get("/users/{user_id}", response=UserSchema, auth=auth)
def get_user(request, user_id: int):
    """Get user by ID"""
    user = get_object_or_404(User, id=user_id)
    return user 