from datetime import datetime, timezone
from io import BytesIO
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .clients import LiveTdSynnexClient, MockTdSynnexClient
from .config import get_settings
from .export import create_quote
from .matching import match_products
from .models import COUNTRIES, ExportRequest, SearchRequest, SearchResponse

settings=get_settings()
app=FastAPI(title=settings.app_name, version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["Content-Type"])


def client():
    return MockTdSynnexClient() if settings.td_synnex_mode == "mock" else LiveTdSynnexClient(settings)


@app.get("/api/health")
async def health(): return {"status":"ok","mode":settings.td_synnex_mode}


@app.get("/api/options")
async def options(): return {"countries":COUNTRIES,"currencies":["USD","JMD","BBD","TTD","MXN","BRL","COP"],"default_country":"Jamaica"}


@app.post("/api/search",response_model=SearchResponse)
async def search(request: SearchRequest):
    try: products=await client().search_products(request)
    except NotImplementedError as exc: raise HTTPException(503,str(exc)) from exc
    except Exception as exc: raise HTTPException(502,"TD SYNNEX service is temporarily unavailable") from exc
    recommendations,regional,lifecycle=match_products(products,request)
    return SearchResponse(recommendations=recommendations,regional_verification=regional,lifecycle_verification=lifecycle,retrieved_at=datetime.now(timezone.utc))


@app.post("/api/export")
async def export(payload: ExportRequest):
    data=create_quote(payload)
    return StreamingResponse(BytesIO(data),media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=product-match-quote.xlsx","X-Content-Type-Options":"nosniff"})

