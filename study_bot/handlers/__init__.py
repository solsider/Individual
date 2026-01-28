from .common import router as common_router
from .study import router as study_router
from .timer import router as timer_router

routers = [common_router, study_router, timer_router]
