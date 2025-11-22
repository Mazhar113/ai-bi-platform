from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict
from .tenant import get_tenant_id

router = APIRouter()

class AgentRequest(BaseModel):
    query: str

@router.post('/agent/run')
async def run_agent(req: AgentRequest, tenant_id: int = Depends(get_tenant_id)) -> Dict[str, Any]:
    from .app import call_llm_to_sql, ALLOWED_COLUMNS, engine
    plan = call_llm_to_sql(req.query)
    if 'where' in plan and plan['where']:
        plan['where'] += f" AND tenant_id = {tenant_id}"
    else:
        plan['where'] = f"tenant_id = {tenant_id}"

    table = plan['table']
    cols = [c for c in plan['cols'] if c in ALLOWED_COLUMNS.get(table, [])]
    col_sql = ', '.join(cols)
    sql = f"SELECT {col_sql} FROM {table}"
    if plan.get('where'):
        sql += ' WHERE ' + plan['where']
    if plan.get('group_by'):
        sql += ' GROUP BY ' + ', '.join(plan['group_by'])

    import pandas as pd
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)

    narrative = f"Executed plan with {len(df)} rows."
    return {'plan': plan, 'sql': sql, 'data': df.to_dict(orient='records'), 'narrative': narrative}
