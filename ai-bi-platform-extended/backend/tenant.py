from fastapi import Request, HTTPException

async def get_tenant_id(request: Request) -> int:
    tid = request.headers.get('X-Tenant-ID')
    if not tid:
        raise HTTPException(status_code=400, detail='Missing X-Tenant-ID header')
    try:
        return int(tid)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid tenant id')
