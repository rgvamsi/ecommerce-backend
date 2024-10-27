from fastapi import APIRouter, HTTPException, status, Depends
from app.controllers.user_manager import UserManager
from app.models.users_model import User, UserLogin,UserUpdateModel,PasswordReset
from app.middleware.auth import get_current_user

router = APIRouter()

user_manager=UserManager()

@router.post("/users/signup",status_code=status.HTTP_201_CREATED)
def signup(user: User):
    try:
        return user_manager.create_user(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.post("/users/login",status_code=status.HTTP_202_ACCEPTED)
def login(user_login: UserLogin):
    try:
        return user_manager.login_user(user_login)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.get("/users/me",status_code=status.HTTP_200_OK)
def read_current_user(current_user: str = Depends(get_current_user)):
    try:
        return user_manager.read_current_user(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.post("/refresh-token",status_code=status.HTTP_201_CREATED)
def create_new_token(refresh_token: str):
    try:
        return user_manager.create_new_access_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.post("/users/logout",status_code=status.HTTP_202_ACCEPTED)
def logout(refresh_token: str):
    try:
        return user_manager.logout_user(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: str):
    try:
        return user_manager.get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.get("/users", status_code=status.HTTP_200_OK)
def get_all_users(current_user: dict = Depends(get_current_user)):
    try:
        return user_manager.users_list(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.put("/users/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def update_user(user_id: str, updated_data: UserUpdateModel):
    try:
        return user_manager.update_user(user_id, updated_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: str):
    try:
        return user_manager.delete_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.post("/users/request-password-reset", status_code=status.HTTP_200_OK)
def request_password_reset(current_user: str = Depends(get_current_user)):
    try:
        return user_manager.request_password_reset(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.post("/users/reset-password/{token}", status_code=status.HTTP_200_OK)
def reset_password( token: str, request: PasswordReset):
    try:
        return user_manager.reset_password(token, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
