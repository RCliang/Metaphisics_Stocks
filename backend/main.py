from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, FastAPI
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
import uvicorn
from crud import *
from models import *
from schemas import Token
import hashlib
import futu as ft
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
from futu_api import *
from fastapi.middleware.cors import CORSMiddleware


origins = ["*"]
app = FastAPI(
    title="Futu project",
    description="Futu project 项目文档：",
    version="1.0.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)
app.mount('/static', app=StaticFiles(directory='./static'), name='static')

SECRET_KEY = "86a39e19831f33b7c8e8757d2e77a6e71b2fbbd117690e3b88f323b8bd5e2e95"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/jwt/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(plain_password: str):
    passwd_hash = hashlib.md5()
    passwd_hash.update(plain_password.encode('utf-8'))
    return passwd_hash.hexdigest()


def verify_password(plain_password: str, hashed_password: str):
    return hash_password(plain_password) == hashed_password


def jwt_get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def jwt_authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/jwt/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = jwt_authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    content = {"message": "You've successfully logged in. Welcome back!"}
    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="lax",
        secure=False,
    )
    return response


async def jwt_get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_schema)):
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credential_error
    except JWTError:
        raise credential_error
    user = get_user(db=db, username=username)
    if user is None:
        raise credential_error
    return user


async def jwt_get_current_active_user(current_user: User = Depends(jwt_get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


@app.get("/fwt/user/me")
async def jwt_read_users_me(current_user: User = Depends(jwt_get_current_active_user)):
    return current_user


@app.get("/fwt/user/active")
async def jwt_active_user(current_user: User = Depends(jwt_get_current_user), db: Session = Depends(get_db)):
    if current_user.disabled:
        active_user(db=db, username=current_user.username)
        return current_user
    else:
        return {"user": current_user.username, "status": current_user.disabled}


# @app.get("/plate_query/{plate_name}")
async def show_plate_code(plate_name: str, db: Session = Depends(get_db)):
    plate = get_plate_code(db=db, plate_name=plate_name)
    if plate:
        return plate
    else:
        raise HTTPException(status_code=404, detail="Plate not found!", headers={"X-Error": "Error"})


@app.get("/long_small/{plate_name}")
async def get_satisfied_stock(plate_name: str, db: Session = Depends(get_db)):
    plate = get_plate_code(db=db, plate_name=plate_name)
    if plate:
        filters = set_filter()
        res = query_result(filters, plate.plate_code)
        response = JSONResponse(content=res)
        return response
    else:
        raise HTTPException(status_code=404, detail="Plate not found!", headers={"X-Error": "Error"})


@app.post("/register", response_model=User)
async def user_register(user: UserInDB, db: Session = Depends(get_db)):
    await create_user(db, user)
    content = {"message": "You've successfully registered!"}
    response = JSONResponse(content=content)
    return response


if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=1)
