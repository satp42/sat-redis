# Redis From Scratch Resources

## Knowledge

### The four course spines (scraped, compiled into the vault wiki)
- [Article: "Write your own miniature Redis with Python" by Charles Leifer](https://charlesleifer.com/blog/building-a-simple-redis-server-with-python/)
  A gevent socket server, a RESP-style protocol handler, and a dict, in one file. Use for: lessons 2 to 4, the overall server shape. Caveat: its protocol is a RESP variant (adds `%` dicts, simple-string commands), so the real RESP spec wins where they differ.
- [Article: "Build Your Own Fast, Persistent KV Store" by Dinesh Gowda](https://dineshgowda.com/posts/build-your-own-persistent-kv-store/)
  Bitcask from first principles: fixed binary header (CRC, timestamp, sizes, types), append-only data file, in-memory key directory. Code in Ruby, maps to Python's `struct` + `zlib.crc32`. Use for: lesson 11, binary on-disk formats.
- [Book: _Mini-LSM_ by Alex Chi Z. (skyzh)](https://skyzh.github.io/mini-lsm/)
  Three weeks of LSM tree engine in Rust: memtable, merge iterator, blocks, SSTs, read/write paths, compaction (simple, tiered, leveled), manifest, WAL, MVCC. Use for: lesson 12 and anything about storage bigger than RAM. Rust code is reference only, the ideas port.
- [Tutorial: Tokio, by the Tokio team](https://tokio.rs/tokio/tutorial)
  Builds mini-redis in async Rust: spawning tasks, shared state behind a lock, channels, framing a byte stream into RESP frames, select, graceful shutdown. Use for: lessons 3 and 5 and 15, translated 1:1 into `asyncio`.

### Primary references
- [Redis docs: RESP protocol spec](https://redis.io/docs/latest/develop/reference/protocol-spec/)
  The ground truth for the wire format sat-redis must speak. Use for: lesson 3 onward, every reply type.
- [Redis docs: Persistence (RDB and AOF)](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
  Snapshots vs append-only file, fsync policies, AOF rewrite, trade-offs. Use for: lessons 9 and 10.
- [Redis docs: EXPIRE](https://redis.io/docs/latest/commands/expire/)
  Includes "How Redis expires keys": lazy expiry on access plus active random sampling. Use for: lesson 6.
- [Redis docs: Pub/Sub](https://redis.io/docs/latest/develop/pubsub/)
  Channel semantics, message reply format, subscribed-connection rules. Use for: lesson 8.
- [Redis docs: Diagnosing latency](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
  "Single threaded nature of Redis" section: one process, multiplexing, never block. Use for: the event-loop argument in lessons 1 and 5.
- [Redis docs: redis-benchmark](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/)
  How to benchmark, pipelining, pitfalls of comparing servers. Use for: lesson 13.
- [Redis docs: Get started](https://redis.io/docs/latest/get-started/) and [Redis FAQ](https://redis.io/faqs/)
  What Redis is, the use cases, the name. Use for: lesson 1.

### Python side (how the Rust ideas translate)
- [Python docs: asyncio Streams](https://docs.python.org/3/library/asyncio-stream.html)
  `start_server`, `StreamReader.readexactly/readuntil`, `StreamWriter.drain`. The asyncio twin of Tokio's `TcpListener` + framing. Use for: lesson 5.
- [uvloop (MagicStack)](https://github.com/MagicStack/uvloop)
  Drop-in libuv event loop, "makes asyncio 2-4x faster". Use for: lesson 13.
- [PyO3 user guide](https://pyo3.rs/)
  Rust extension modules for Python, built with maturin. Use for: lesson 14, moving a profiled hot path to Rust.

## Wisdom (Communities)
- [r/redis](https://www.reddit.com/r/redis/) for questions about Redis semantics and internals.
- [CodeCrafters "Build your own Redis" discussions](https://codecrafters.io/challenges/redis) where many people build the same thing in Python and compare approaches. Use for: sanity-checking edge cases. (Not a source for this course's code.)
- [Tokio Discord](https://discord.gg/tokio) for the async design questions when we get to the Rust hot path.

## Gaps
- No high-trust source yet for Redis's sorted-set internals (skip list + hash). Find one before lesson 7 (candidate: antirez's writing or the Redis source `t_zset.c`).
- No source yet for RDB file format details. Needed only if we write RDB-compatible snapshots in lesson 10.
