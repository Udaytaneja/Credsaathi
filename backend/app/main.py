from fastapi import FastAPI

app = FastAPI(
    title="CredSaathi API",
    description="Backend API for the CredSaathi financial platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "credsaathi-backend",
        "version": "0.1.0",
    }