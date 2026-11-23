# Teaching notes

## Workspace layout
- Repo root `~/Desktop/sat-redis/` is the *project*: README, the Python package the learner writes, tests.
- `course/` is the /teach workspace (this folder). Run /teach from here.
- Scraped sources live in `../.firecrawl/pages/` (gitignored, not republished) and in a private notes vault, compiled into a personal wiki.

## Learner preferences
- Knows Python. No Rust. No Redis. Assume nothing about networking or storage either.
- Visual learner: plain words and an everyday picture first, then the official term. Every jargon word gets a term card with a tiny SVG. Dense jargon lessons get rejected.
- Wants the "senior engineer without a coding agent" mental model: why this order, what to test first, what to measure, what to deliberately leave crude.
- Uses Cursor. Suggest turning off Tab autocomplete and the agent for the `sat_redis/` folder so the code is really theirs. They can still ask the teacher (Claude) anything.
- Wants Rust's performance ideas carried into Python. Answer given in lesson 1: Redis's speed is mostly architecture (single-threaded event loop, in-memory, pipelining), which ports to asyncio. The language tax is real, attacked late with uvloop, a faster parser, multiple processes, and PyO3 for measured hot paths.

## Teaching contract for code lessons
- Each code lesson ships: the idea, a picture, a spec, a failing test file the learner copies in, and hints in rungs. Never a full solution unless asked.
- Run the learner's tests and real `redis-cli` against their code when they say they're done, then review like a senior engineer would in a PR.

## Planned arc (adjust to evidence)
1. What Redis is, use cases, play with the real one  ← lesson 0001
2. Sockets: an echo server with the stdlib, poked with `nc`  ← lesson 0002 (shipped 2026-11-19, spec tests/test_echo.py, 7 pass + 1 xfail when done)
3. RESP: TCP is a stream, so framing; a parser tested on partial reads  ← lesson 0003 (shipped 2026-11-23, spec tests/test_resp.py, pure parse/encode, done = 30 passed + 1 xfail)
4. Commands: PING/ECHO/SET/GET, real redis-cli connects (milestone)
5. Many clients: threads vs the event loop, asyncio (Tokio's model, translated)
6. Expiry: lazy + active
7. More types: INCR, lists, hashes, sorted sets
8. Pub/Sub
9. Persistence I: append-only file, fsync policies, replay on boot
10. Persistence II: snapshots and AOF rewrite
11. Storage engine I: Bitcask (hash index over a log, CRC, struct)
12. Storage engine II: LSM (memtable, SSTs, merge iterator, compaction, WAL)
13. Benchmark + profile: redis-benchmark, py-spy, pipelining, uvloop
14. Multi-core + Rust: processes with SO_REUSEPORT, PyO3 hot path
15. Production polish: graceful shutdown, config, logging, packaging

## Progress
- 2026-11-19: learner reports lesson 0001 done. Score line not pasted yet. Lesson 0002 shipped.
- 2026-11-20: lesson 0002 quiz 5/6 (missed Q2: thought one loop serves two clients at once). Recall answer had the two loops right. Gaps: pictured `accept` as polling (it blocks) and `recv(1024)` as fixed-size envelopes (it returns whatever has arrived, up to 1024). server.py was correct except the name `server_forever`, so tests could not import `serve_forever`. Next: rename, go green, commit, then lesson 0003 (RESP parser).
- 2026-11-23: learner green on lesson 0002 (renamed serve_forever, committed). Lesson 0003 shipped: RESP parse/encode as pure functions, 23 tests incl. every-byte partial cuts. Lesson 2 quiz recall gaps (accept blocks, recv is not fixed-size) are re-addressed in 0003 recall and the three-outcomes picture.
