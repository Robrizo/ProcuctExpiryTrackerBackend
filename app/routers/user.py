from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.auth.jwt import get_password_hash, user_dependancy, verify_password
from app.config.database import db_dependency
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserUpdatePassword

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(user: user_dependancy, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication")
    user_data = db.query(User).filter(User.id == user.get("user_id")).first()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_data

@router.post("/me/update-password", response_model=UserResponse)
def update_user_password(user: user_dependancy, db: db_dependency, password_data: UserUpdatePassword):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication")
    
    user_data = db.query(User).filter(User.id == user.get("user_id")).first()
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verify the current password
    if not verify_password(password_data.current_password, user_data.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    
    # Update the password
    user_data.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(user_data)
    
    return user_data

@router.post("/me/update-user", response_model=UserResponse)
def update_user_info(user: user_dependancy, db: db_dependency, user_data: UserUpdate):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication")
    
    existing_user = db.query(User).filter(User.id == user.get("user_id")).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_user, key, value)
    
    db.commit()
    db.refresh(existing_user)
    
    return existing_user