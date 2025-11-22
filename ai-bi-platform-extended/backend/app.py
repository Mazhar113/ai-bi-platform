import os
import asyncio
from fastapi import FastAPI, WebSocket, Depends
from pydantic import BaseModel
import sqlalchemy as sa
import pandas as pd
import uvicorn
import json
from typing import Any, Dict
from sklearn.ensemble import GradientBoostingRegressor
import joblib
import shap
import numpy as np

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://demo:postgres@postgres:5432/bi_demo")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

engine = sa.create_engine(DATABASE_URL, future=True)
app = FastAPI()

# Simple metadata whitelist
ALLOWED_TABLES = {"sales", "customers"}
ALLOWED_COLUMNS = {
    "sales": {"id", "date", "region", "product", "revenue", "units","tenant_id"},
    "customers": {"id", "name", "signup_date", "country"}
}

class NLQRequest(BaseModel):
    query: str

def call_llm_to_sql(nl_text: str) -> Dict[str, Any]:
    text = nl_text.lower()
    if "q3" in text or "quarter 3" in text:
        return {"table": "sales", "cols": ["date", "region", "revenue"], "where": "date >= '2023-07-01' AND date < '2023-10-01'", "group_by": ["date"]}
    if "revenue by region" in text:
        return {"table": "sales", "cols": ["region", "revenue"], "where": "", "group_by": ["region"]}
    return {"table": "sales", "cols": ["date", "revenue"], "where": "", "group_by": ["date"]}

@app.post("/nlq")
async def nlq(req: NLQRequest):
    plan = call_llm_to_sql(req.query)
    table = plan["table"]
    if table not in ALLOWED_TABLES:
        return {"error": "table not allowed"}

    cols = plan["cols"]
    cols = [c for c in cols if c in ALLOWED_COLUMNS[table]]
    group_by = plan.get("group_by", [])
    where = plan.get("where", "")
    col_sql = ", ".join(cols)
    sql = f"SELECT {col_sql} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if group_by:
        sql += " GROUP BY " + ", ".join(group_by)
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    return {"sql": sql, "data": df.to_dict(orient="records")}

# include routers
from .sql_runner import router as sql_router
from .agent import router as agent_router
from .auth import get_current_user
app.include_router(sql_router)
app.include_router(agent_router)

# Simple train endpoint for demo model
@app.post("/train")
async def train():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT tenant_id, date, region, revenue, units FROM sales", conn)

    df = df.dropna()
    # features: units, region one-hot (tenant-agnostic for demo)
    X = pd.get_dummies(df[["units", "region"]], drop_first=True)
    y = df["revenue"]
    model = GradientBoostingRegressor(n_estimators=50)
    model.fit(X, y)
    joblib.dump((model, X.columns.tolist()), "model.joblib")
    return {"status": "trained", "n": len(df)}

@app.get("/predict")
async def predict():
    model, cols = joblib.load("model.joblib")
    with engine.connect() as conn:
        latest = pd.read_sql("SELECT units, region FROM sales ORDER BY date DESC LIMIT 1", conn)
    X = pd.get_dummies(latest, drop_first=True)
    for c in cols:
        if c not in X.columns:
            X[c] = 0
    X = X[cols]
    pred = model.predict(X)[0]
    explainer = shap.Explainer(model.predict, X)
    shap_vals = explainer(X)
    feature_contribs = {c: float(shap_vals.values[0][i]) for i, c in enumerate(cols)}
    return {"prediction": float(pred), "explanation": feature_contribs}

@app.websocket("/ws/dashboard")
async def ws_dashboard(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await asyncio.sleep(2)
            msg = {"metric": "revenue", "value": float(np.random.rand() * 1000), "ts": pd.Timestamp.utcnow().isoformat()}
            await ws.send_text(json.dumps(msg))
    except Exception:
        await ws.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
