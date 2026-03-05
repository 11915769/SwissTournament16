from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth_routes import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.tournament_public import router as tournament_router
from app.routers.swiss_admin import router as swiss_admin_router
from app.routers.bracket_admin import router as bracket_admin_router
from app.routers.bracket_public import router as bracket_public_router
from dotenv import load_dotenv

if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200",
                   "https://5d82-2a02-8388-6681-ba00-b49f-5e11-3ec1-7837.ngrok-free.app",
                   "https://kniffelswiss16.web.app",
                   "https://kniffelswiss16.firebaseapp.com",
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(tournament_router)
app.include_router(swiss_admin_router)
app.include_router(bracket_admin_router)
app.include_router(bracket_public_router)
