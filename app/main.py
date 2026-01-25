from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from app.schema import schema
from app.database import get_db, init_db
from app.routes.views import router as view_router
from app.routes.payments import router as payment_router
from app.routes.views import templates # Import templates to add extension
from app.i18n import get_locale, get_translations
from contextlib import asynccontextmanager
from fastapi import Request

# Lifespan context to initialize DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

async def get_context(db=Depends(get_db)):
    return {"db": db}

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(lifespan=lifespan, title="Handi Temple Management")

# I18n Middleware / Context Processor
@app.middleware("http")
async def add_translation_context(request: Request, call_next):
    locale = get_locale(request)
    translations = get_translations(locale)

    # Inject gettext into the template environment for this request
    # Since templates is a global object, modifying env.globals is tricky for concurrent requests
    # if we change it globally.
    # BETTER APPROACH: Pass it in the response context in the router, OR use a custom context processor.
    # However, FastAPI/Starlette Jinja2Templates doesn't fully support per-request env globals easily
    # without passing it every time.
    # STRATEGY: We will add a helper to `request.state` and use a custom function in templates,
    # or rely on the router to pass `_`.
    # Let's try adding it to request.state and having a global function that checks request context?
    # No, simpler: We will make `_` available in all templates via `templates.env.globals` BUT
    # it needs to be dynamic.
    # Standard Python web way: use context vars.

    # Simple Async Way for Demo:
    # We will pass the translation function into the `request` scope so view functions can grab it.
    request.state.gettext = translations.gettext

    response = await call_next(request)
    return response

# We need to make sure the view router uses this.
# We'll patch the view router to inject `_` into the context.
# See app/routes/views.py modification plan.

app.include_router(graphql_app, prefix="/graphql")
app.include_router(view_router)
app.include_router(payment_router)
