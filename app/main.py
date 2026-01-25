from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from app.schema import schema
from app.database import get_db, init_db
from app.routes.views import router as view_router
from contextlib import asynccontextmanager

# Lifespan context to initialize DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

async def get_context(db=Depends(get_db)):
    return {"db": db}

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(lifespan=lifespan, title="Handi Temple Management")

app.include_router(graphql_app, prefix="/graphql")
app.include_router(view_router)
