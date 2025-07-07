# The FastAPI application instance

from fastapi import FastAPI
from routers import chat
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="RAN Realtime search",
    description=(
        "A scalable, empathetic, professor-level AI chatbot "
        "Ask a question within the allowed topics and receive a thorough, cited answer."
    ),
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Register the chat router
app.include_router(chat.router)
@app.get("/health")
def health():
    return {'Message': 'Keep calm, App running!'}
@app.on_event("startup")
async def on_startup():
    print("🚀 API starting up...")

@app.on_event("shutdown")
async def on_shutdown():
    print("🛑 API shutting down...")
