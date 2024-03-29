import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Request, status
import uvicorn


from api.appplications import router as application_router
from api.statistics import router as stat_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# Allow all origins, allow all methods, allow all headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(application_router)
app.include_router(stat_router)

if __name__ == '__main__':
    logger.info('CatCode core api starting up')
    uvicorn.run('main:app')
