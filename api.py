from fastapi import APIRouter

from app.routers import ca_profiles, clients, dashboard, firms, health, users, matches, applications, tracker, billing, notifications, documents, knowledge, copilot, auth

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(tracker.router, prefix="/tracker", tags=["tracker"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ca_profiles.router, prefix="/ca-profiles", tags=["ca-profiles"])
api_router.include_router(firms.router, prefix="/firms", tags=["firms"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(auth.router, tags=["auth"])
