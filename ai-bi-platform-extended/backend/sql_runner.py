from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any
import pandas as pd
from .tenant import get_tenant_id
from .app import engine, ALLOWED_TABLES, ALLOWED_COLUMNS

router = APIRouter()

class SQLRequest(BaseModel):
    sql: str

@router.post('/sql/run')
async def run_sql(req: SQLRequest, tenant_id: int = Depends(get_tenant_id)) -> Any:
    sql = req.sql.strip()
    if not sql.lower().startswith('select'):
        return {'error': 'only SELECT statements are allowed'}

    if ';' in sql:
        return {'error': 'multiple statements not allowed'}

    # Force tenant filter
    if 'where' in sql.lower():
        sql = sql + f" AND tenant_id = {tenant_id}"
    else:
        sql = sql + f" WHERE tenant_id = {tenant_id}"

    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    return {'sql': sql, 'data': df.to_dict(orient='records')}
