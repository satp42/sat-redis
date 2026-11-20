# sat-redis

A Redis clone written from scratch in Python, by hand, as a learning project.

The goal is a production-shaped server: the official `redis-cli`, `redis-benchmark`, and client libraries should be able to talk to it, it should survive `kill -9` without losing data, and it should handle hundreds of concurrent clients. Every line of the server is hand-written (no coding agent). An AI tutor writes the course, the specs, and the tests, and reviews the code.

## What is Redis?

Redis is a dictionary that lives in its own program and answers questions over the network. The name stands for **RE**mote **DI**ctionary **S**erver. Because it keeps data in memory, it is fast, so teams put it next to their main database for caching, sessions, rate limiting, leaderboards, job queues, and live messaging.

A Python `dict` dies with your process and only your process can see it. Redis moves that dictionary into a separate server so every machine running your app sees the same data, and writes it to disk so it survives restarts.

## Architecture (the plan)

```
4. Keyspace     a dict of keys, values, and expiry times    ──┐
3. Commands     SET GET INCR EXPIRE LPUSH ZADD PUBLISH …      │  Persistence:
2. Protocol     RESP bytes  <->  ["SET", "k", "v"]            │  AOF, snapshots,
1. Network      one asyncio event loop, many connections      │  Bitcask, LSM tree
                                                            ──┘
```

Real Redis executes commands on a single thread, in an event loop. That design ports directly to Python's `asyncio`. The Python-vs-C speed gap gets measured with `redis-benchmark` and attacked late, in order: pipelining, `uvloop`, multiple processes, and moving profiled hot paths to Rust with PyO3.

## Roadmap

- [x] 1. Understand Redis and its use cases (play with the real one)
- [ ] 2. Sockets: a stdlib echo server
- [ ] 3. RESP: a framing-aware parser, tested on partial reads
- [ ] 4. `PING` / `ECHO` / `SET` / `GET`: real `redis-cli` connects
- [ ] 5. Many clients with `asyncio`
- [ ] 6. Key expiry: lazy and active
- [ ] 7. `INCR`, lists, hashes, sorted sets
- [ ] 8. Pub/Sub
- [ ] 9. Append-only file and `fsync` policies
- [ ] 10. Snapshots and AOF rewrite
- [ ] 11. Bitcask storage engine
- [ ] 12. LSM tree storage engine
- [ ] 13. Benchmarking and profiling
- [ ] 14. Multi-core and a Rust hot path via PyO3
- [ ] 15. Production polish: graceful shutdown, config, logging

## Repo layout

| Path | What |
| --- | --- |
| `sat_redis/` | The server (written by hand, appears from lesson 2) |
| `tests/` | Tests, many checked against real Redis's replies |
| `course/` | The course: `lessons/` (open in a browser), `reference/` cheat sheets, `MISSION.md`, `RESOURCES.md` |

Start at [`course/lessons/0001-redis-is-a-shared-dictionary-in-its-own-program.html`](course/lessons/0001-redis-is-a-shared-dictionary-in-its-own-program.html).

## Sources the course is built on

- Charles Leifer, [Write your own miniature Redis with Python](https://charlesleifer.com/blog/building-a-simple-redis-server-with-python/)
- Dinesh Gowda, [Build Your Own Fast, Persistent KV Store](https://dineshgowda.com/posts/build-your-own-persistent-kv-store/) (Bitcask)
- Alex Chi Z., [Mini-LSM: Build an LSM tree storage engine in a week](https://skyzh.github.io/mini-lsm/)
- The [Tokio tutorial](https://tokio.rs/tokio/tutorial), which builds mini-redis in Rust (its async design maps onto `asyncio`)
- The official [Redis docs](https://redis.io/docs/latest/), especially the [RESP spec](https://redis.io/docs/latest/develop/reference/protocol-spec/) and [persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

## License

MIT
