from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta

# ✅ Import custom route files
from routes import transport
from routes import room

# 🔐 JWT config
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# 🔐 OAuth2 token configuration with roles
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={"admin": "Admin access", "user": "User access"}
)

# Optional: For future use if you need role-based login form
class OAuth2PasswordRequestFormWithRole(OAuth2PasswordRequestForm):
    role: str

# 🔐 Create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🔐 Login route
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    role = "user"
    if form_data.scopes:
        role = form_data.scopes[0]

    token = create_access_token({"sub": form_data.username, "role": role})
    return {"access_token": token, "token_type": "bearer", "role": role}

# 🔐 Example protected route
@app.get("/protected")
def protected_route(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_role = payload.get("role")
        return {"message": f"Hello, {user_role}!"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Include custom routers
app.include_router(transport.router)
app.include_router(room.router)

# ✅ Welcome route
@app.get("/")
def home():
    return {"message": "Welcome to the Trip Management System!"}
