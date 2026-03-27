from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.models.user import User, UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from fastapi import Depends

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(user_data: UserCreate):
    # Check existing email
    existing = await User.find_one(User.email == user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await User.find_one(User.username == user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        family_contact_email=user_data.family_contact_email,
    )
    await user.insert()

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await User.find_one(User.email == credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user.last_login = datetime.utcnow()
    await user.save()

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
    )


@router.get("/call-history")
async def get_call_history(current_user: User = Depends(get_current_user)):
    from app.models.call_log import CallLog
    logs = await CallLog.find(CallLog.user_id == str(current_user.id)).sort(-CallLog.call_start).limit(50).to_list()
    return [
        {
            "id": str(log.id),
            "call_start": log.call_start,
            "call_end": log.call_end,
            "caller_number": log.caller_number,
            "threat_level": log.threat_level,
            "overall_threat_score": log.overall_threat_score,
            "is_deepfake": log.is_deepfake,
            "urgency_detected": log.urgency_detected,
            "transcript": log.transcript,
            "negotiator_strategy": log.negotiator_strategy,
        }
        for log in logs
    ]
