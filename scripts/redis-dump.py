#!/usr/bin/python3
import asyncio
from redis.asyncio import Redis, RedisCluster
import argparse
import json
from typing import Any, Union


parser = argparse.ArgumentParser(description="Redis Dump to JSON File Tool")
parser.add_argument("--url", type=str, help="Redis server URL")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Redis server host")
parser.add_argument("--port", type=int, default=6379, help="Redis server port")
parser.add_argument("--db", type=int, default=0, help="Redis database number")
parser.add_argument(
    "--cluster", action="store_true", default=False, help="Use Redis cluster"
)
parser.add_argument("--output", type=str, default="dump.json", help="Output JSON file path")



async def dump_redis(client: Union[Redis, RedisCluster], output:str) -> None:
    dump: dict[str, dict[str, Any]] = {}
    async for key in client.scan_iter(match="*", count=1000):
        key_type = await client.type(key)
        value: Any
        if key_type == "string":
            value = await client.get(key)
        elif key_type == "list":
            value = await client.lrange(key, 0, -1)
        elif key_type == "set":
            members = await client.smembers(key)
            value = sorted(list(members))
        elif key_type == "zset":
            z: list[tuple[str, float]] = await client.zrange(key, 0, -1, withscores=True)
            value = [{"member": member, "score": float(score)} for member, score in z]
        elif key_type == "hash":
            value = await client.hgetall(key)
        elif key_type == "stream":
            entries = await client.xrange(key, min="-", max="+")
            value = [{"id": entry_id, "fields": fields} for entry_id, fields in entries]
        else:
            value = None
        dump[key] = {"type": key_type, "value": value}

    with open(output, "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=2)




def create_redis_client(args):

    url = args.url if args.url else f"redis://{args.host}:{args.port}/{args.db}"
    print(f"Creating Redis client from URL: {url}")
    return RedisCluster.from_url(url, decode_responses=True) if args.cluster else Redis.from_url(url, decode_responses=True)

async def main():
    args = parser.parse_args()
    client = create_redis_client(args)
    try:
        result = await client.ping()
        print(f"Redis server is running: {result}")
        await dump_redis(client, args.output)
        print(f"Dumped Redis DB {args.db} to {args.output}")
    finally:
        try:
            await client.aclose()
        except Exception:
            pass

    

if __name__ == "__main__":
    asyncio.run(main())