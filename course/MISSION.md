# Mission: Build sat-redis, a production-shaped Redis in Python, by hand

## Why
Understand how a real database server works by writing one: sat-redis, a Redis clone in Python that the official `redis-cli`, `redis-benchmark`, and client libraries can talk to. Every line is typed by hand in Cursor, the way a senior engineer would build it without a coding agent, so the understanding is real and the repo is proof of it.

## Success looks like
- The real `redis-cli` connects to sat-redis and runs `SET/GET/DEL/INCR/EXPIRE/TTL`, lists, hashes, sorted sets, and `PUBLISH/SUBSCRIBE`.
- `kill -9` the server mid-write, restart it, and the data is back (append-only file + snapshots, then a log-structured store).
- `redis-benchmark` with hundreds of concurrent clients runs against it, and the numbers are compared to real Redis and explained.
- Every design choice (event loop, RESP framing, lazy + active expiry, fsync policy, log-structured storage, compaction) can be explained from first principles, out loud, without notes.
- Where profiling proves Python is the bottleneck, one hot path is moved to Rust with PyO3, and the speedup is measured.

## Constraints
- Python, which Satwik knows. Zero Rust and zero Redis knowledge at the start.
- Started from scratch: no idea what Redis is. Lessons must be ELI5 and visual first.
- Hand-written code in Cursor. The teacher gives specs, tests, hints, and reviews, not finished implementations.
- Public repo on GitHub: `sat-redis`.

## Out of scope (for now)
- Replication, Redis Cluster, Sentinel.
- Lua scripting, modules, ACLs, RESP3-only features.
