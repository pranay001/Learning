# C# Events, Threads, Tasks & Concurrent Collections — Deep Dive

An extensive, example-driven reference on four closely related areas of C#: **events**, **threads**, **tasks (async/await)**, and **concurrent queues**. These topics matter together because real-world concurrent systems typically use threads/tasks to do work in parallel, thread-safe collections to pass data between them, and events to notify other parts of the application when something happens.

---

## Table of Contents

1. [Events](#1-events)
2. [Threads](#2-threads)
3. [Tasks & async/await](#3-tasks--asyncawait)
4. [Concurrent Queues](#4-concurrent-queues)
5. [Putting It All Together: Producer-Consumer Pipeline](#5-putting-it-all-together-producer-consumer-pipeline)
6. [Common Pitfalls](#6-common-pitfalls)
7. [Quick Reference Tables](#7-quick-reference-tables)

---

## 1. Events

### 1.1 What Is an Event?

An **event** is a member that allows a class (the *publisher*) to notify other classes (*subscribers*) when something happens, without knowing anything about who's listening. Events are built on top of **delegates** but restrict external code so it can only subscribe (`+=`) or unsubscribe (`-=`) — it cannot invoke the event or overwrite the entire subscriber list.

### 1.2 Basic Event Example

```csharp
public class Alarm
{
    // Step 1: declare the event using the built-in EventHandler delegate
    public event EventHandler Triggered;

    public void Trip()
    {
        Console.WriteLine("Alarm tripped!");
        // Step 2: raise the event, using ?. to avoid a NullReferenceException
        // if no one has subscribed yet
        Triggered?.Invoke(this, EventArgs.Empty);
    }
}

public class Program
{
    public static void Main()
    {
        var alarm = new Alarm();

        // Step 3: subscribe using a named method
        alarm.Triggered += OnAlarmTriggered;

        // Subscribe using a lambda too — you can have multiple subscribers
        alarm.Triggered += (sender, e) => Console.WriteLine("Security team notified.");

        alarm.Trip();

        // Unsubscribe when no longer needed
        alarm.Triggered -= OnAlarmTriggered;
    }

    private static void OnAlarmTriggered(object sender, EventArgs e)
    {
        Console.WriteLine("Logging: alarm event received.");
    }
}
```

**Output:**
```
Alarm tripped!
Logging: alarm event received.
Security team notified.
```

### 1.3 Custom EventArgs (Passing Data with an Event)

```csharp
public class OrderPlacedEventArgs : EventArgs
{
    public string OrderId { get; }
    public decimal Total { get; }

    public OrderPlacedEventArgs(string orderId, decimal total)
    {
        OrderId = orderId;
        Total = total;
    }
}

public class OrderProcessor
{
    public event EventHandler<OrderPlacedEventArgs> OrderPlaced;

    public void PlaceOrder(string orderId, decimal total)
    {
        // ... business logic ...
        OrderPlaced?.Invoke(this, new OrderPlacedEventArgs(orderId, total));
    }
}

var processor = new OrderProcessor();
processor.OrderPlaced += (sender, e) =>
    Console.WriteLine($"Order {e.OrderId} placed for ${e.Total}");

processor.PlaceOrder("ORD-1001", 249.99m);
```

### 1.4 Custom Delegate-Based Events

You don't have to use `EventHandler`; any delegate type works.

```csharp
public delegate void PriceChangedHandler(decimal oldPrice, decimal newPrice);

public class Stock
{
    public event PriceChangedHandler PriceChanged;
    private decimal _price;

    public decimal Price
    {
        get => _price;
        set
        {
            if (value == _price) return;
            decimal old = _price;
            _price = value;
            PriceChanged?.Invoke(old, value);
        }
    }
}

var stock = new Stock();
stock.PriceChanged += (oldP, newP) =>
    Console.WriteLine($"Price moved from {oldP:C} to {newP:C}");
stock.Price = 105.50m;
```

### 1.5 Events and Thread Safety

Raising an event that has multiple subscribers running on different threads can cause race conditions. A common safe pattern:

```csharp
public class SafeNotifier
{
    private readonly object _lock = new object();
    private EventHandler _updated;

    public event EventHandler Updated
    {
        add { lock (_lock) { _updated += value; } }
        remove { lock (_lock) { _updated -= value; } }
    }

    public void Notify()
    {
        EventHandler handler;
        lock (_lock) { handler = _updated; } // snapshot to avoid mid-invoke changes
        handler?.Invoke(this, EventArgs.Empty);
    }
}
```

### 1.6 Weak Events (Avoiding Memory Leaks)

If a subscriber never unsubscribes, the publisher holds a reference to it, preventing garbage collection. For long-lived publishers, consider unsubscribing explicitly (e.g., in `Dispose`) or using patterns like `WeakEventManager` (common in WPF).

```csharp
public class Widget : IDisposable
{
    private readonly Alarm _alarm;
    public Widget(Alarm alarm)
    {
        _alarm = alarm;
        _alarm.Triggered += OnTriggered;
    }

    private void OnTriggered(object sender, EventArgs e) => Console.WriteLine("Widget reacting...");

    public void Dispose() => _alarm.Triggered -= OnTriggered; // prevent leak
}
```

---

## 2. Threads

### 2.1 Creating and Starting a Thread

A `Thread` represents an actual OS-level thread. Creating one directly gives fine control but comes with more overhead than using the thread pool (via `Task`).

```csharp
using System.Threading;

Thread worker = new Thread(() =>
{
    for (int i = 0; i < 5; i++)
    {
        Console.WriteLine($"Worker thread: {i}");
        Thread.Sleep(500);
    }
});

worker.Start();
Console.WriteLine("Main thread continues immediately...");

worker.Join(); // block main thread until worker finishes
Console.WriteLine("Worker finished.");
```

### 2.2 Passing Data to a Thread

```csharp
void ProcessItem(object data)
{
    string item = (string)data;
    Console.WriteLine($"Processing {item} on thread {Thread.CurrentThread.ManagedThreadId}");
}

Thread t = new Thread(ProcessItem);
t.Start("Order #42");
```

### 2.3 Background vs Foreground Threads

```csharp
Thread bgThread = new Thread(() => Console.WriteLine("Background work"));
bgThread.IsBackground = true; // process can exit even if this thread is still running
bgThread.Start();
```

### 2.4 Thread Naming and Priority

```csharp
Thread t = new Thread(DoWork) { Name = "ImageProcessor", Priority = ThreadPriority.AboveNormal };
t.Start();
```

### 2.5 Synchronization Primitives

Multiple threads accessing shared state need coordination to avoid race conditions.

**`lock` (Monitor):**

```csharp
private static readonly object _lockObj = new object();
private static int _counter = 0;

void Increment()
{
    lock (_lockObj)
    {
        _counter++; // only one thread at a time can execute this block
    }
}
```

**`Interlocked` (lock-free atomic operations, faster for simple cases):**

```csharp
private static int _counter = 0;
void IncrementAtomic() => Interlocked.Increment(ref _counter);
```

**`Mutex` (cross-process synchronization):**

```csharp
using var mutex = new Mutex(false, "Global\\MyAppMutex");
if (mutex.WaitOne(TimeSpan.FromSeconds(5)))
{
    try { /* critical section, even across processes */ }
    finally { mutex.ReleaseMutex(); }
}
```

**`SemaphoreSlim` (limit concurrent access to a resource):**

```csharp
var semaphore = new SemaphoreSlim(3); // max 3 concurrent threads

async Task AccessResourceAsync(int id)
{
    await semaphore.WaitAsync();
    try
    {
        Console.WriteLine($"Task {id} entered the resource");
        await Task.Delay(1000);
    }
    finally
    {
        semaphore.Release();
    }
}
```

**`ReaderWriterLockSlim` (many readers, one writer):**

```csharp
var rwLock = new ReaderWriterLockSlim();
var data = new List<int>();

void Read()
{
    rwLock.EnterReadLock();
    try { Console.WriteLine(data.Count); }
    finally { rwLock.ExitReadLock(); }
}

void Write(int value)
{
    rwLock.EnterWriteLock();
    try { data.Add(value); }
    finally { rwLock.ExitWriteLock(); }
}
```

### 2.6 Thread Pool

Manually creating threads is expensive; the **thread pool** reuses a pool of worker threads.

```csharp
ThreadPool.QueueUserWorkItem(state =>
{
    Console.WriteLine("Running on a pooled thread");
});
```

In modern C#, `Task.Run` is the preferred way to schedule work on the thread pool (see Section 3).

### 2.7 Parallel Loops (Data Parallelism)

```csharp
using System.Threading.Tasks;

Parallel.For(0, 10, i =>
{
    Console.WriteLine($"Processing index {i} on thread {Thread.CurrentThread.ManagedThreadId}");
});

var items = new List<string> { "a", "b", "c", "d" };
Parallel.ForEach(items, item =>
{
    Console.WriteLine($"Processing {item}");
});

// With options: limit degree of parallelism
Parallel.ForEach(items, new ParallelOptions { MaxDegreeOfParallelism = 2 }, item =>
{
    Console.WriteLine($"Limited processing {item}");
});
```

---

## 3. Tasks & async/await

### 3.1 Task vs Thread

A `Task` represents an asynchronous operation — it may or may not use a dedicated thread. CPU-bound tasks typically run on the thread pool; I/O-bound tasks (network, disk, database) often don't occupy a thread at all while waiting.

```csharp
Task task = Task.Run(() =>
{
    Console.WriteLine($"Running on thread {Thread.CurrentThread.ManagedThreadId}");
});
task.Wait(); // blocking wait (avoid in async code — prefer await)
```

### 3.2 Task with a Return Value

```csharp
Task<int> computeTask = Task.Run(() =>
{
    int result = 0;
    for (int i = 0; i < 1000000; i++) result += i;
    return result;
});

int total = computeTask.Result; // blocking — prefer 'await computeTask' in async methods
Console.WriteLine(total);
```

### 3.3 async/await Basics

```csharp
public async Task<string> DownloadContentAsync(string url)
{
    using var client = new HttpClient();
    string content = await client.GetStringAsync(url); // frees the thread while waiting
    return content;
}

public async Task RunAsync()
{
    Console.WriteLine("Starting download...");
    string result = await DownloadContentAsync("https://example.com");
    Console.WriteLine($"Downloaded {result.Length} characters");
}
```

### 3.4 Running Tasks Concurrently

```csharp
public async Task DownloadMultipleAsync()
{
    Task<string> t1 = DownloadContentAsync("https://example.com/a");
    Task<string> t2 = DownloadContentAsync("https://example.com/b");
    Task<string> t3 = DownloadContentAsync("https://example.com/c");

    string[] results = await Task.WhenAll(t1, t2, t3); // runs concurrently, waits for all
    Console.WriteLine($"Total length: {results.Sum(r => r.Length)}");
}
```

### 3.5 Task.WhenAny (First to Complete)

```csharp
Task<string> fastest = await Task.WhenAny(
    DownloadContentAsync("https://mirror1.example.com"),
    DownloadContentAsync("https://mirror2.example.com")
);
Console.WriteLine($"Fastest response length: {fastest.Result.Length}");
```

### 3.6 Cancellation

```csharp
public async Task DoWorkAsync(CancellationToken token)
{
    for (int i = 0; i < 10; i++)
    {
        token.ThrowIfCancellationRequested();
        Console.WriteLine($"Step {i}");
        await Task.Delay(500, token);
    }
}

var cts = new CancellationTokenSource();
cts.CancelAfter(2000); // auto-cancel after 2 seconds

try
{
    await DoWorkAsync(cts.Token);
}
catch (OperationCanceledException)
{
    Console.WriteLine("Work was cancelled.");
}
```

### 3.7 Exception Handling in Tasks

```csharp
public async Task RiskyOperationAsync()
{
    try
    {
        await Task.Run(() => throw new InvalidOperationException("Something broke"));
    }
    catch (InvalidOperationException ex)
    {
        Console.WriteLine($"Caught: {ex.Message}");
    }
}

// When using .Result or .Wait() on a faulted task, exceptions are wrapped
// in an AggregateException:
try
{
    Task t = Task.Run(() => throw new Exception("fail"));
    t.Wait();
}
catch (AggregateException ex)
{
    foreach (var inner in ex.InnerExceptions)
        Console.WriteLine(inner.Message);
}
```

### 3.8 Progress Reporting

```csharp
public async Task ProcessWithProgressAsync(IProgress<int> progress)
{
    for (int i = 0; i <= 100; i += 10)
    {
        await Task.Delay(200);
        progress?.Report(i);
    }
}

var progressHandler = new Progress<int>(percent => Console.WriteLine($"{percent}% complete"));
await ProcessWithProgressAsync(progressHandler);
```

### 3.9 ValueTask (Performance Optimization)

For hot paths where a result is often available synchronously, `ValueTask<T>` avoids allocating a `Task` object.

```csharp
public ValueTask<int> GetCachedValueAsync(int key)
{
    if (_cache.TryGetValue(key, out int value))
        return new ValueTask<int>(value); // no allocation, synchronous path

    return new ValueTask<int>(LoadFromDatabaseAsync(key)); // falls back to real Task
}
```

### 3.10 async Streams (IAsyncEnumerable)

```csharp
public async IAsyncEnumerable<int> GenerateNumbersAsync()
{
    for (int i = 0; i < 5; i++)
    {
        await Task.Delay(300);
        yield return i;
    }
}

await foreach (var number in GenerateNumbersAsync())
{
    Console.WriteLine(number);
}
```

---

## 4. Concurrent Queues

### 4.1 Why ConcurrentQueue\<T>?

`Queue<T>` is **not thread-safe** — concurrent `Enqueue`/`Dequeue` calls from multiple threads can corrupt internal state. `System.Collections.Concurrent.ConcurrentQueue<T>` is a lock-free, thread-safe FIFO queue designed for exactly this scenario.

```csharp
using System.Collections.Concurrent;

ConcurrentQueue<string> queue = new ConcurrentQueue<string>();

// Enqueue is safe from any thread, no explicit locking needed
queue.Enqueue("Item 1");
queue.Enqueue("Item 2");

// TryDequeue instead of Dequeue — returns false if the queue is empty
// rather than throwing, since another thread might empty it between check and access
if (queue.TryDequeue(out string item))
{
    Console.WriteLine($"Dequeued: {item}");
}

// TryPeek — view the next item without removing it
if (queue.TryPeek(out string next))
{
    Console.WriteLine($"Next up: {next}");
}

Console.WriteLine($"Count: {queue.Count}"); // approximate under heavy concurrency
Console.WriteLine($"IsEmpty: {queue.IsEmpty}");
```

### 4.2 Multi-Producer, Multi-Consumer Example

```csharp
using System.Collections.Concurrent;

var queue = new ConcurrentQueue<int>();
var random = new Random();

// 3 producer tasks, each adding 5 items
var producers = Enumerable.Range(1, 3).Select(producerId => Task.Run(() =>
{
    for (int i = 0; i < 5; i++)
    {
        int item = producerId * 100 + i;
        queue.Enqueue(item);
        Console.WriteLine($"Producer {producerId} enqueued {item}");
        Thread.Sleep(random.Next(50, 150));
    }
})).ToArray();

// 2 consumer tasks, each pulling items until told to stop
var cts = new CancellationTokenSource();
var consumers = Enumerable.Range(1, 2).Select(consumerId => Task.Run(() =>
{
    while (!cts.IsCancellationRequested || !queue.IsEmpty)
    {
        if (queue.TryDequeue(out int item))
        {
            Console.WriteLine($"Consumer {consumerId} processed {item}");
        }
        else
        {
            Thread.Sleep(20);
        }
    }
})).ToArray();

Task.WaitAll(producers);
cts.Cancel(); // signal consumers to wind down once queue drains
Task.WaitAll(consumers);
Console.WriteLine("All work complete.");
```

### 4.3 Comparing Concurrent Collections

| Type | Order | Best for |
|---|---|---|
| `ConcurrentQueue<T>` | FIFO | Producer-consumer, task scheduling |
| `ConcurrentStack<T>` | LIFO | Concurrent undo-style operations |
| `ConcurrentBag<T>` | Unordered | Work-stealing scenarios where order doesn't matter |
| `ConcurrentDictionary<K,V>` | Unordered (keyed) | Thread-safe caches, counters |
| `BlockingCollection<T>` | Configurable (wraps a `ConcurrentQueue`/`Bag`/`Stack`) | Bounded producer-consumer with blocking waits |

### 4.4 BlockingCollection\<T> — A Higher-Level Producer-Consumer Wrapper

Unlike `ConcurrentQueue<T>`, which requires consumers to poll (`TryDequeue`), `BlockingCollection<T>` lets a consumer **block and wait** until an item is available, and supports a maximum capacity (backpressure).

```csharp
using System.Collections.Concurrent;

// Bounded to 10 items — producers block if the queue is full
var blockingQueue = new BlockingCollection<int>(boundedCapacity: 10);

var producer = Task.Run(() =>
{
    for (int i = 0; i < 20; i++)
    {
        blockingQueue.Add(i); // blocks if capacity is reached
        Console.WriteLine($"Produced {i}");
    }
    blockingQueue.CompleteAdding(); // signal no more items will be added
});

var consumer = Task.Run(() =>
{
    // GetConsumingEnumerable blocks until an item arrives or CompleteAdding() is called
    foreach (var item in blockingQueue.GetConsumingEnumerable())
    {
        Console.WriteLine($"Consumed {item}");
        Thread.Sleep(100); // simulate slower consumer, causing producer backpressure
    }
});

await Task.WhenAll(producer, consumer);
```

### 4.5 ConcurrentQueue with async Consumers

Combining a `ConcurrentQueue<T>` with a `SemaphoreSlim` gives you async-friendly signaling (avoiding busy polling):

```csharp
public class AsyncQueue<T>
{
    private readonly ConcurrentQueue<T> _queue = new();
    private readonly SemaphoreSlim _signal = new(0);

    public void Enqueue(T item)
    {
        _queue.Enqueue(item);
        _signal.Release(); // wake up one waiting consumer
    }

    public async Task<T> DequeueAsync(CancellationToken token = default)
    {
        await _signal.WaitAsync(token); // waits without spinning
        _queue.TryDequeue(out T item);
        return item;
    }
}

var asyncQueue = new AsyncQueue<string>();

var consumerTask = Task.Run(async () =>
{
    for (int i = 0; i < 3; i++)
    {
        string item = await asyncQueue.DequeueAsync();
        Console.WriteLine($"Async consumed: {item}");
    }
});

asyncQueue.Enqueue("first");
asyncQueue.Enqueue("second");
asyncQueue.Enqueue("third");

await consumerTask;
```

---

## 5. Putting It All Together: Producer-Consumer Pipeline

A realistic example combining **events**, **tasks**, and **concurrent queues**: an order-processing pipeline that queues incoming orders, processes them on background tasks, and raises an event once each order finishes.

```csharp
using System.Collections.Concurrent;

public class OrderCompletedEventArgs : EventArgs
{
    public string OrderId { get; }
    public OrderCompletedEventArgs(string orderId) => OrderId = orderId;
}

public class OrderPipeline
{
    private readonly ConcurrentQueue<string> _pendingOrders = new();
    private readonly CancellationTokenSource _cts = new();
    private readonly List<Task> _workers = new();

    // Event raised on the worker thread when an order finishes
    public event EventHandler<OrderCompletedEventArgs> OrderCompleted;

    public void Enqueue(string orderId) => _pendingOrders.Enqueue(orderId);

    public void StartWorkers(int workerCount)
    {
        for (int i = 0; i < workerCount; i++)
        {
            int workerId = i;
            _workers.Add(Task.Run(() => WorkerLoop(workerId, _cts.Token)));
        }
    }

    private void WorkerLoop(int workerId, CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            if (_pendingOrders.TryDequeue(out string orderId))
            {
                Console.WriteLine($"Worker {workerId} processing {orderId}");
                Thread.Sleep(300); // simulate work
                OrderCompleted?.Invoke(this, new OrderCompletedEventArgs(orderId));
            }
            else
            {
                Thread.Sleep(50); // avoid busy-spinning when queue is empty
            }
        }
    }

    public async Task StopAsync()
    {
        _cts.Cancel();
        await Task.WhenAll(_workers);
    }
}

// Usage
var pipeline = new OrderPipeline();
pipeline.OrderCompleted += (sender, e) =>
    Console.WriteLine($"✔ Order {e.OrderId} completed.");

pipeline.StartWorkers(workerCount: 3);

for (int i = 1; i <= 6; i++)
    pipeline.Enqueue($"ORD-{i:000}");

await Task.Delay(2000);   // let workers process
await pipeline.StopAsync();
```

This pattern is the foundation of many real systems: web request queues, background job processors, and message-driven microservices.

---

## 6. Common Pitfalls

| Pitfall | Why it's a problem | Fix |
|---|---|---|
| Using `Dequeue()` on a plain `Queue<T>` across threads | Not thread-safe, can corrupt state or throw | Use `ConcurrentQueue<T>` with `TryDequeue` |
| `async void` methods (other than event handlers) | Exceptions can't be caught by the caller, can crash the process | Use `async Task` |
| Calling `.Result` or `.Wait()` on an async method from a UI/sync context | Can deadlock due to synchronization context capture | Use `await` all the way, or `ConfigureAwait(false)` in libraries |
| Forgetting to unsubscribe from events | Publisher keeps subscriber alive → memory leak | Unsubscribe in `Dispose`, or use weak event patterns |
| Busy-waiting with a `while` loop and `Thread.Sleep` polling a queue | Wastes CPU cycles | Prefer `BlockingCollection<T>` or a semaphore-signaled async queue |
| Raising events without a null check | `NullReferenceException` if there are no subscribers | Use `?.Invoke(...)` |
| Sharing mutable state across threads without synchronization | Race conditions, corrupted data | Use `lock`, `Interlocked`, or concurrent collections |
| Overusing `Task.Run` for I/O-bound work | Wastes thread-pool threads unnecessarily | Use natively async APIs (e.g., `HttpClient.GetAsync`) instead |
| Ignoring `OperationCanceledException` | Can cause silent failures or confusing error handling | Explicitly catch and handle cancellation |

---

## 7. Quick Reference Tables

### Events

| Concept | Syntax |
|---|---|
| Declare | `public event EventHandler<T> Name;` |
| Subscribe | `obj.Name += handler;` |
| Unsubscribe | `obj.Name -= handler;` |
| Raise (null-safe) | `Name?.Invoke(this, args);` |

### Threads

| Concept | Syntax |
|---|---|
| Create | `new Thread(() => {...})` |
| Start | `thread.Start();` |
| Wait for completion | `thread.Join();` |
| Background thread | `thread.IsBackground = true;` |
| Atomic increment | `Interlocked.Increment(ref counter);` |
| Mutual exclusion | `lock (obj) { ... }` |

### Tasks

| Concept | Syntax |
|---|---|
| Run on thread pool | `Task.Run(() => {...})` |
| Await | `await SomeAsyncMethod();` |
| Wait for all | `await Task.WhenAll(t1, t2);` |
| Wait for any | `await Task.WhenAny(t1, t2);` |
| Delay | `await Task.Delay(1000);` |
| Cancel | `CancellationTokenSource` + `token.ThrowIfCancellationRequested()` |

### Concurrent Queues

| Concept | Syntax |
|---|---|
| Create | `new ConcurrentQueue<T>()` |
| Add | `queue.Enqueue(item);` |
| Remove (safe) | `queue.TryDequeue(out var item)` |
| Peek (safe) | `queue.TryPeek(out var item)` |
| Bounded blocking queue | `new BlockingCollection<T>(capacity)` |
| Consume until done | `foreach (var x in bc.GetConsumingEnumerable())` |

---

*Practice idea: extend the producer-consumer pipeline in Section 5 to use `BlockingCollection<T>` instead of manual polling, and add a `CancellationToken`-aware `OrderFailed` event for orders that throw exceptions during processing.*
