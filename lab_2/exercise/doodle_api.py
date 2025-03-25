from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI()

pools = {}


class Pool(BaseModel):
    name: str = Field(default="My pool")
    options: dict[str, int] = Field(default={"option 1": 0, "option 2": 0})

    def show_results(self) -> dict[str, int]:
        # dict(sorted(options.items(), key=lambda item: item[1], reverse = True))
        return {name: value for name, value in sorted(self.options.items(), key=lambda item: item[1], reverse=True)}


@app.get("/")
def root():
    return {"message": "Simple doodle api"}


@app.get("/v1/pools/{pool_name}")
def show_pool(pool_name: str):
    if pool_name not in pools:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pools[pool_name]


@app.get("/v2/pools/{pool_name}")
def show_pool_results(pool_name: str) -> dict[str, int]:

    if pool_name not in pools:
        raise HTTPException(status_code=404, detail='Pool not found')
    pool = pools[pool_name]

    return pool.show_results()


@app.post("/v3/pools/")
def create_pool(item: Pool):
    if item.name in pools:
        raise HTTPException(status_code=400, detail="Pool already exists")
    pools[item.name] = item
    return item


@app.put("/v4/pools/")
def update_pool(pool_name: str, updated_pool: Pool):

    if pool_name not in pools:
        raise HTTPException(status_code=400, detail='Pool not found')

    pools.pop(pool_name)
    pools[updated_pool.name] = updated_pool

    return pools[updated_pool.name]


@app.delete("/v5/pools/{pool_name}")
def delete_pool(pool_name: str):
    if pool_name not in pools:
        raise HTTPException(status_code=400, detail='Pool not found')

    pool_to_delete = pools.pop(pool_name)
    return pool_to_delete


@app.put("/v6/pools/vote/")
def cast_vote(pool_name: str, option_name: str):
    if pool_name not in pools:
        raise HTTPException(status_code=404, detail="Pool not found")
    pool = pools[pool_name]
    if option_name not in pool.options:
        raise HTTPException(status_code=400, detail="Option not found")
    pool.options[option_name] += 1
    return pool


@app.put("/v7/pools/remove_vote/")
def remove_vote(pool_name: str, option_name: str):
    if pool_name not in pools:
        raise HTTPException(status_code=404, detail="Pool not found")
    pool = pools[pool_name]
    if option_name not in pool.options:
        raise HTTPException(status_code=400, detail="Option not found")
    if pool.options[option_name] > 0:
        pool.options[option_name] -= 1
    return pool
