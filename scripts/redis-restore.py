#!/usr/bin/python3
import asyncio
from redis.asyncio import Redis, RedisCluster
from redis.asyncio.cluster import ClusterNode
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
parser.add_argument("--nodes", type=str, help="Redis cluster nodes")
parser.add_argument(
    "--input", type=str, default="dump.json", help="Input JSON file path"
)


async def restore_key(
    client: Union[Redis, RedisCluster], key: str, entry: dict[str, Any]
) -> None:
    key_type = entry.get("type")
    value = entry.get("value")

    if key_type is None:
        return

    await client.delete(key)

    if key_type == "string":
        if value is not None:
            await client.set(key, value)
    elif key_type == "list":
        if value:
            await client.rpush(key, *value)
    elif key_type == "set":
        if value:
            await client.sadd(key, *value)
    elif key_type == "zset":
        if value:
            mapping = {item["member"]: float(item["score"]) for item in value}
            if mapping:
                await client.zadd(key, mapping)
    elif key_type == "hash":
        if value:
            await client.hset(key, mapping=value)
    elif key_type == "stream":
        if value:
            for item in value:
                entry_id = item.get("id", "*")
                fields = item.get("fields", {})
                await client.xadd(key, fields, id=entry_id)


async def restore_redis(client: Redis, input: str) -> None:
    with open(input, "r", encoding="utf-8") as f:
        data: dict[str, dict[str, Any]] = json.load(f)

    tasks = []
    for key, entry in data.items():
        tasks.append(restore_key(client, key, entry))
    await asyncio.gather(*tasks)


def create_redis_client(args):
    if args.cluster:
        # In cluster mode, DB selection is not supported; ignore args.db
        url = args.url if args.url else f"redis://{args.host}:{args.port}"
        if args.nodes:
            nodes = args.nodes.split(",")
            nodes = [
                ClusterNode(host=node.split(":")[0], port=int(node.split(":")[1]))
                for node in nodes
            ]
            print(f"Creating Redis CLUSTER client from nodes: {nodes}")
            return RedisCluster(startup_nodes=nodes, decode_responses=True)
        else:
            print(f"Creating Redis CLUSTER client from URL: {url}")
            return RedisCluster.from_url(url, decode_responses=True)
    else:
        url = args.url if args.url else f"redis://{args.host}:{args.port}/{args.db}"
        print(f"Creating Redis client from URL: {url}")
        return Redis.from_url(url, decode_responses=True)


async def main():
    args = parser.parse_args()
    client = create_redis_client(args)
    try:
        result = await client.ping()
        print(f"Redis server is running: {result}")
        await restore_redis(client, args.input)
        print(f"Restored Redis DB {args.db} from {args.input}")
    finally:
        try:
            await client.aclose()
        except Exception:
            pass

    print("Done")


if __name__ == "__main__":
    asyncio.run(main())
