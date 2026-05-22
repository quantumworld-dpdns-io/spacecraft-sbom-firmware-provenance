from sbom_provenance.api.routes.health import router as health_router
from sbom_provenance.api.routes.sbom import router as sbom_router
from sbom_provenance.api.routes.firmware import router as firmware_router
from sbom_provenance.api.routes.provenance import router as provenance_router
from sbom_provenance.api.routes.approval import router as approval_router
from sbom_provenance.api.routes.security import router as security_router
from sbom_provenance.api.routes.search import router as search_router

__all__ = [
    "health_router",
    "sbom_router",
    "firmware_router",
    "provenance_router",
    "approval_router",
    "security_router",
    "search_router",
]
