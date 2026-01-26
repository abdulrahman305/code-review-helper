# Performance Patterns and Anti-Patterns

## Database Performance

### N+1 Query Problem

**Anti-pattern:**
```python
# Fetches N+1 queries: 1 for users, N for each user's orders
users = User.objects.all()
for user in users:
    orders = user.orders.all()  # Query per user!
```

**Solution:**
```python
# Single query with JOIN
users = User.objects.prefetch_related('orders').all()
```

### Missing Indexes

**Symptoms:**
- Slow queries on large tables
- Full table scans in explain plans

**Solution:**
- Add indexes on frequently queried columns
- Composite indexes for multi-column queries
- Covering indexes for read-heavy queries

### Unbounded Queries

**Anti-pattern:**
```sql
SELECT * FROM logs WHERE created_at > '2024-01-01'
-- Could return millions of rows
```

**Solution:**
```sql
SELECT * FROM logs WHERE created_at > '2024-01-01' LIMIT 1000
-- Always paginate large result sets
```

## Memory Performance

### String Concatenation in Loops

**Anti-pattern:**
```python
result = ""
for item in items:
    result += str(item)  # Creates new string each iteration
```

**Solution:**
```python
result = "".join(str(item) for item in items)  # Single allocation
```

### Unbounded Collections

**Anti-pattern:**
```python
cache = {}
def get_data(key):
    if key not in cache:
        cache[key] = fetch_from_db(key)  # Cache grows forever
    return cache[key]
```

**Solution:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)  # Bounded cache with LRU eviction
def get_data(key):
    return fetch_from_db(key)
```

### Large Object Retention

**Anti-pattern:**
```python
def process_files(file_paths):
    all_data = []
    for path in file_paths:
        data = read_large_file(path)  # Keeps all in memory
        all_data.append(data)
    return process(all_data)
```

**Solution:**
```python
def process_files(file_paths):
    for path in file_paths:
        data = read_large_file(path)
        yield process_chunk(data)  # Stream processing
```

## CPU Performance

### Repeated Computation

**Anti-pattern:**
```python
for item in items:
    config = load_config()  # Reloads every iteration
    process(item, config)
```

**Solution:**
```python
config = load_config()  # Load once
for item in items:
    process(item, config)
```

### Inefficient Algorithms

**Anti-pattern:**
```python
def find_duplicates(items):
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other:  # O(n²)
                duplicates.append(item)
    return duplicates
```

**Solution:**
```python
from collections import Counter

def find_duplicates(items):
    counts = Counter(items)  # O(n)
    return [item for item, count in counts.items() if count > 1]
```

### Regex Compilation

**Anti-pattern:**
```python
def validate_emails(emails):
    for email in emails:
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):  # Compiles each time
            yield email
```

**Solution:**
```python
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')  # Compile once

def validate_emails(emails):
    for email in emails:
        if EMAIL_PATTERN.match(email):
            yield email
```

## I/O Performance

### Synchronous I/O in Async Context

**Anti-pattern:**
```python
async def fetch_all(urls):
    results = []
    for url in urls:
        response = requests.get(url)  # Blocks event loop!
        results.append(response.json())
    return results
```

**Solution:**
```python
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)  # Concurrent
        return [await r.json() for r in responses]
```

### Missing Connection Pooling

**Anti-pattern:**
```python
def query_db(sql):
    conn = psycopg2.connect(...)  # New connection per query
    result = conn.execute(sql)
    conn.close()
    return result
```

**Solution:**
```python
from psycopg2 import pool

db_pool = pool.ThreadedConnectionPool(1, 20, ...)

def query_db(sql):
    conn = db_pool.getconn()
    try:
        return conn.execute(sql)
    finally:
        db_pool.putconn(conn)
```

## Network Performance

### Chatty APIs

**Anti-pattern:**
```python
user = api.get_user(id)
profile = api.get_profile(id)
settings = api.get_settings(id)
# 3 round trips
```

**Solution:**
```python
# Single batch request
data = api.get_user_with_details(id, include=['profile', 'settings'])
```

### Missing Compression

**Solution:**
- Enable gzip/brotli compression for responses > 1KB
- Use binary protocols (protobuf, msgpack) for internal services

### No Caching Headers

**Solution:**
- Set Cache-Control headers for static resources
- Use ETags for conditional requests
- Implement stale-while-revalidate patterns

## Profiling Commands

### Python
```bash
python -m cProfile -s cumtime script.py
python -m memory_profiler script.py
```

### Node.js
```bash
node --prof script.js
node --inspect script.js  # Chrome DevTools profiling
```

### Database
```sql
EXPLAIN ANALYZE SELECT ...;
```
