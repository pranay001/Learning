# The Complete gRPC Guide (C# / .NET)

An extensive, example-driven reference for **gRPC** — covering Protocol Buffers, all four messaging patterns, error handling, interceptors, security, performance, and production concerns — using C#/.NET as the primary implementation language.

---

## Table of Contents

1. [Introduction to gRPC](#1-introduction-to-grpc)
2. [Protocol Buffers (protobuf) Fundamentals](#2-protocol-buffers-protobuf-fundamentals)
3. [Project Setup](#3-project-setup)
4. [Messaging Pattern 1: Unary RPC](#4-messaging-pattern-1-unary-rpc)
5. [Messaging Pattern 2: Server Streaming RPC](#5-messaging-pattern-2-server-streaming-rpc)
6. [Messaging Pattern 3: Client Streaming RPC](#6-messaging-pattern-3-client-streaming-rpc)
7. [Messaging Pattern 4: Bidirectional Streaming RPC](#7-messaging-pattern-4-bidirectional-streaming-rpc)
8. [Error Handling & Status Codes](#8-error-handling--status-codes)
9. [Deadlines, Timeouts & Cancellation](#9-deadlines-timeouts--cancellation)
10. [Metadata & Headers](#10-metadata--headers)
11. [Interceptors (Middleware)](#11-interceptors-middleware)
12. [Authentication & Security](#12-authentication--security)
13. [Client-Side Load Balancing & Channels](#13-client-side-load-balancing--channels)
14. [gRPC-Web & Browser Support](#14-grpc-web--browser-support)
15. [Testing gRPC Services](#15-testing-grpc-services)
16. [Performance & Best Practices](#16-performance--best-practices)
17. [gRPC vs REST](#17-grpc-vs-rest)
18. [Quick Reference](#18-quick-reference)

---

## 1. Introduction to gRPC

**gRPC** ("gRPC Remote Procedure Calls") is a high-performance, open-source RPC framework originally developed by Google. It uses:

- **HTTP/2** as the transport protocol (multiplexed streams, header compression, bidirectional streaming)
- **Protocol Buffers (protobuf)** as the default interface definition language (IDL) and binary serialization format
- **Strongly-typed contracts** shared between client and server via `.proto` files, from which code is generated for many languages (C#, Java, Go, Python, etc.)

### Why gRPC?

| Benefit | Explanation |
|---|---|
| Performance | Binary serialization (protobuf) is smaller and faster to (de)serialize than JSON |
| Streaming | Native support for client, server, and bidirectional streaming over a single connection |
| Strong contracts | `.proto` files are the single source of truth; generated code eliminates hand-written DTOs/clients |
| Polyglot | First-class code generation for many languages, ideal for microservices in mixed stacks |
| HTTP/2 features | Multiplexing (many concurrent calls on one TCP connection), header compression, flow control |

### The Four Messaging Patterns (Overview)

| Pattern | Client sends | Server sends | Analogy |
|---|---|---|---|
| **Unary** | 1 message | 1 message | A normal function call / REST request-response |
| **Server streaming** | 1 message | stream of messages | Subscribing to a feed after one request |
| **Client streaming** | stream of messages | 1 message | Uploading a stream of data, get one summary back |
| **Bidirectional streaming** | stream of messages | stream of messages | A live chat / real-time two-way channel |

We'll cover all four in depth with complete, runnable C# examples.

---

## 2. Protocol Buffers (protobuf) Fundamentals

### Basic .proto Syntax

```protobuf
syntax = "proto3";

option csharp_namespace = "GreeterApp";

package greet;

// Service definition
service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply);
}

// Message definitions
message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

Each field has a unique **field number** (`= 1`, `= 2`, ...) used in the binary wire encoding — these numbers must never be reused or changed once a message ships to production, as doing so breaks wire compatibility.

### Scalar Types

| Proto Type | C# Type | Notes |
|---|---|---|
| `double` | `double` | |
| `float` | `float` | |
| `int32` | `int` | Inefficient for negative numbers |
| `int64` | `long` | |
| `uint32` | `uint` | |
| `uint64` | `ulong` | |
| `sint32` / `sint64` | `int` / `long` | Efficient encoding for negative numbers |
| `fixed32` / `fixed64` | `uint` / `ulong` | Faster for large values, fixed-width |
| `bool` | `bool` | |
| `string` | `string` | UTF-8 |
| `bytes` | `ByteString` | Raw binary data |

### Composite Types

```protobuf
message Address {
  string street = 1;
  string city = 2;
  string zip_code = 3;
}

message Person {
  string name = 1;
  int32 age = 2;
  Address home_address = 3;         // nested message
  repeated string phone_numbers = 4; // list/array
  map<string, string> attributes = 5; // dictionary

  enum Status {
    UNKNOWN = 0; // proto3 enums MUST have a zero value as default
    ACTIVE = 1;
    INACTIVE = 2;
  }
  Status status = 6;

  oneof contact_method {          // exactly one of these fields is set
    string email = 7;
    string phone = 8;
  }
}
```

### Well-Known Types

```protobuf
import "google/protobuf/timestamp.proto";
import "google/protobuf/duration.proto";
import "google/protobuf/empty.proto";
import "google/protobuf/wrappers.proto"; // nullable scalars, e.g. google.protobuf.Int32Value

message Event {
  string name = 1;
  google.protobuf.Timestamp occurred_at = 2;
  google.protobuf.Duration processing_time = 3;
}

service Housekeeping {
  rpc ClearCache (google.protobuf.Empty) returns (google.protobuf.Empty);
}
```

In C#, `Timestamp` maps to a type with `.ToDateTime()` / `Timestamp.FromDateTime(...)` helpers.

### Versioning & Backward Compatibility Rules

| Safe change | Unsafe change |
|---|---|
| Adding a new field with a new number | Reusing a field number for a different field |
| Adding a new RPC method | Renaming a field number/changing its type incompatibly |
| Adding values to an enum | Removing a field still used by old clients |
| Marking a field `reserved` after removal | Changing a field from singular to `repeated` (or vice versa) |

```protobuf
message Person {
  reserved 4, 5;           // reserve removed field numbers so they're never reused
  reserved "old_field_name"; // reserve removed field names too
}
```

---

## 3. Project Setup

### Server Project

```bash
dotnet new grpc -o GreeterServer
cd GreeterServer
```

This scaffolds:

```
GreeterServer/
├── Protos/
│   └── greet.proto
├── Services/
│   └── GreeterService.cs
├── appsettings.json
├── Program.cs
└── GreeterServer.csproj
```

### .csproj Configuration

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Grpc.AspNetCore" Version="2.63.0" />
  </ItemGroup>

  <ItemGroup>
    <Protobuf Include="Protos\greet.proto" GrpcServices="Server" />
  </ItemGroup>
</Project>
```

### Program.cs (Server)

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddGrpc();

var app = builder.Build();
app.MapGrpcService<GreeterService>();
app.MapGet("/", () => "This server only supports gRPC clients. Use a gRPC-capable client.");

app.Run();
```

### Client Project

```bash
dotnet new console -o GreeterClient
cd GreeterClient
dotnet add package Grpc.Net.Client
dotnet add package Google.Protobuf
dotnet add package Grpc.Tools
```

```xml
<ItemGroup>
  <Protobuf Include="Protos\greet.proto" GrpcServices="Client" />
</ItemGroup>
```

---

## 4. Messaging Pattern 1: Unary RPC

The simplest and most common pattern: one request, one response — conceptually identical to a normal method call or a REST GET/POST.

### Proto Definition

```protobuf
syntax = "proto3";
option csharp_namespace = "GreeterApp";
package greet;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply);
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

### Server Implementation

```csharp
using Grpc.Core;
using GreeterApp;

public class GreeterService : Greeter.GreeterBase
{
    private readonly ILogger<GreeterService> _logger;

    public GreeterService(ILogger<GreeterService> logger)
    {
        _logger = logger;
    }

    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
    {
        _logger.LogInformation("Received request for {Name}", request.Name);

        return Task.FromResult(new HelloReply
        {
            Message = $"Hello, {request.Name}!"
        });
    }
}
```

### Client Implementation

```csharp
using Grpc.Net.Client;
using GreeterApp;

using var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new Greeter.GreeterClient(channel);

var reply = await client.SayHelloAsync(new HelloRequest { Name = "Alice" });
Console.WriteLine($"Server response: {reply.Message}");
```

### When to Use Unary

- CRUD-style operations (get/create/update/delete a resource)
- Any request-response interaction that doesn't need incremental data
- Default choice unless you specifically need streaming semantics

---

## 5. Messaging Pattern 2: Server Streaming RPC

Client sends **one** request; server responds with a **stream** of messages over time, then closes the stream. Useful for subscriptions, large result sets returned incrementally, or live feeds.

### Proto Definition

```protobuf
service StockTicker {
  rpc WatchPrice (WatchPriceRequest) returns (stream PriceUpdate);
}

message WatchPriceRequest {
  string symbol = 1;
}

message PriceUpdate {
  string symbol = 1;
  double price = 2;
  int64 timestamp_unix_ms = 3;
}
```

### Server Implementation

```csharp
public class StockTickerService : StockTicker.StockTickerBase
{
    public override async Task WatchPrice(
        WatchPriceRequest request,
        IServerStreamWriter<PriceUpdate> responseStream,
        ServerCallContext context)
    {
        var random = new Random();
        decimal price = 100m;

        // Keep streaming until the client disconnects or cancels
        while (!context.CancellationToken.IsCancellationRequested)
        {
            price += (decimal)(random.NextDouble() * 2 - 1); // random walk

            await responseStream.WriteAsync(new PriceUpdate
            {
                Symbol = request.Symbol,
                Price = (double)price,
                TimestampUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
            });

            await Task.Delay(1000, context.CancellationToken);
        }
    }
}
```

### Client Implementation

```csharp
using var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new StockTicker.StockTickerClient(channel);

using var cts = new CancellationTokenSource();
using var call = client.WatchPrice(new WatchPriceRequest { Symbol = "MSFT" }, cancellationToken: cts.Token);

try
{
    await foreach (var update in call.ResponseStream.ReadAllAsync(cts.Token))
    {
        Console.WriteLine($"{update.Symbol}: ${update.Price:F2} at {update.TimestampUnixMs}");
    }
}
catch (RpcException ex) when (ex.StatusCode == StatusCode.Cancelled)
{
    Console.WriteLine("Stream cancelled by client.");
}
```

### Manual Stream Reading (Alternative to await foreach)

```csharp
using var call = client.WatchPrice(new WatchPriceRequest { Symbol = "MSFT" });

while (await call.ResponseStream.MoveNext(CancellationToken.None))
{
    var update = call.ResponseStream.Current;
    Console.WriteLine($"{update.Symbol}: ${update.Price:F2}");
}
```

### When to Use Server Streaming

- Live data feeds (stock prices, sensor readings, log tailing)
- Returning large datasets incrementally instead of one huge payload
- Progress updates for a long-running server-side operation

---

## 6. Messaging Pattern 3: Client Streaming RPC

Client sends a **stream** of messages; the server processes them and returns **one** final response once the client finishes sending.

### Proto Definition

```protobuf
service FileUploader {
  rpc UploadFile (stream FileChunk) returns (UploadSummary);
}

message FileChunk {
  bytes content = 1;
  int32 sequence_number = 2;
}

message UploadSummary {
  int32 total_chunks_received = 1;
  int64 total_bytes = 2;
  string file_id = 3;
}
```

### Server Implementation

```csharp
public class FileUploaderService : FileUploader.FileUploaderBase
{
    public override async Task<UploadSummary> UploadFile(
        IAsyncStreamReader<FileChunk> requestStream,
        ServerCallContext context)
    {
        int chunkCount = 0;
        long totalBytes = 0;

        await foreach (var chunk in requestStream.ReadAllAsync())
        {
            chunkCount++;
            totalBytes += chunk.Content.Length;
            // In a real system: write chunk.Content to disk/blob storage here
        }

        return new UploadSummary
        {
            TotalChunksReceived = chunkCount,
            TotalBytes = totalBytes,
            FileId = Guid.NewGuid().ToString()
        };
    }
}
```

### Client Implementation

```csharp
using var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new FileUploader.FileUploaderClient(channel);

using var call = client.UploadFile();

byte[] fileBytes = await File.ReadAllBytesAsync("large-file.bin");
const int chunkSize = 64 * 1024; // 64 KB chunks
int sequenceNumber = 0;

for (int offset = 0; offset < fileBytes.Length; offset += chunkSize)
{
    int length = Math.Min(chunkSize, fileBytes.Length - offset);
    var chunk = new FileChunk
    {
        Content = Google.Protobuf.ByteString.CopyFrom(fileBytes, offset, length),
        SequenceNumber = sequenceNumber++
    };

    await call.RequestStream.WriteAsync(chunk);
}

await call.RequestStream.CompleteAsync(); // signal no more chunks

UploadSummary summary = await call.ResponseAsync;
Console.WriteLine($"Uploaded {summary.TotalBytes} bytes in {summary.TotalChunksReceived} chunks. File ID: {summary.FileId}");
```

### When to Use Client Streaming

- File/data uploads sent in chunks
- Aggregating a batch of client-generated events into a single summary
- IoT devices sending a burst of telemetry that's summarized server-side

---

## 7. Messaging Pattern 4: Bidirectional Streaming RPC

Both client and server send independent streams of messages over the **same connection**, which can be read/written concurrently and asynchronously (either side can send at any time, in any order relative to the other).

### Proto Definition

```protobuf
service ChatService {
  rpc Chat (stream ChatMessage) returns (stream ChatMessage);
}

message ChatMessage {
  string user = 1;
  string text = 2;
  int64 timestamp_unix_ms = 3;
}
```

### Server Implementation

```csharp
public class ChatServiceImpl : ChatService.ChatServiceBase
{
    // A naive in-memory broadcast list; a real system would use a proper pub-sub mechanism
    private static readonly List<IServerStreamWriter<ChatMessage>> _connectedClients = new();
    private static readonly object _lock = new();

    public override async Task Chat(
        IAsyncStreamReader<ChatMessage> requestStream,
        IServerStreamWriter<ChatMessage> responseStream,
        ServerCallContext context)
    {
        lock (_lock) { _connectedClients.Add(responseStream); }

        try
        {
            // Read incoming messages from THIS client and broadcast to all clients
            await foreach (var message in requestStream.ReadAllAsync(context.CancellationToken))
            {
                Console.WriteLine($"[{message.User}]: {message.Text}");

                List<IServerStreamWriter<ChatMessage>> recipientsSnapshot;
                lock (_lock) { recipientsSnapshot = new List<IServerStreamWriter<ChatMessage>>(_connectedClients); }

                foreach (var recipient in recipientsSnapshot)
                {
                    try { await recipient.WriteAsync(message); }
                    catch { /* recipient disconnected; ignore for this simple example */ }
                }
            }
        }
        finally
        {
            lock (_lock) { _connectedClients.Remove(responseStream); }
        }
    }
}
```

### Client Implementation

```csharp
using var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new ChatService.ChatServiceClient(channel);

using var call = client.Chat();

// Task 1: continuously read incoming messages from the server
var readTask = Task.Run(async () =>
{
    await foreach (var message in call.ResponseStream.ReadAllAsync())
    {
        Console.WriteLine($"{message.User}: {message.Text}");
    }
});

// Task 2: send messages typed by the user
var writeTask = Task.Run(async () =>
{
    while (true)
    {
        string? line = Console.ReadLine();
        if (string.IsNullOrEmpty(line)) break;

        await call.RequestStream.WriteAsync(new ChatMessage
        {
            User = "Alice",
            Text = line,
            TimestampUnixMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
        });
    }
    await call.RequestStream.CompleteAsync();
});

await Task.WhenAll(readTask, writeTask);
```

### When to Use Bidirectional Streaming

- Real-time chat, collaborative editing, multiplayer game state sync
- Continuous two-way negotiation protocols
- Streaming translation/transcription (send audio chunks, receive text chunks concurrently)

### Concurrency Note

On a single bidirectional call, gRPC allows **one writer at a time per direction** — i.e., you shouldn't call `RequestStream.WriteAsync` concurrently from multiple threads without your own synchronization, since the underlying stream write is not inherently thread-safe for concurrent writers.

---

## 8. Error Handling & Status Codes

gRPC uses a well-defined set of **status codes** (distinct from HTTP status codes, though gRPC over HTTP/2 does map onto HTTP status codes at the transport level).

### Common Status Codes

| Code | Meaning | Typical Cause |
|---|---|---|
| `OK` (0) | Success | — |
| `CANCELLED` (1) | Operation cancelled by caller | Client cancelled the request |
| `INVALID_ARGUMENT` (3) | Client sent invalid data | Bad input validation |
| `DEADLINE_EXCEEDED` (4) | Operation didn't complete in time | Timeout/deadline expired |
| `NOT_FOUND` (5) | Requested entity doesn't exist | Missing resource |
| `ALREADY_EXISTS` (6) | Entity already exists | Duplicate create attempt |
| `PERMISSION_DENIED` (7) | Caller lacks permission | AuthZ failure |
| `RESOURCE_EXHAUSTED` (8) | Rate limit / quota exceeded | Too many requests |
| `FAILED_PRECONDITION` (9) | System not in required state | e.g., deleting a non-empty directory |
| `UNAUTHENTICATED` (16) | Missing/invalid credentials | AuthN failure |
| `UNAVAILABLE` (14) | Service temporarily unavailable | Server down, network issue — safe to retry |
| `INTERNAL` (13) | Internal server error | Unhandled exception |

### Throwing Errors on the Server

```csharp
public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
{
    if (string.IsNullOrWhiteSpace(request.Name))
    {
        throw new RpcException(new Status(
            StatusCode.InvalidArgument,
            "Name must not be empty"));
    }

    if (request.Name == "banned-user")
    {
        throw new RpcException(new Status(
            StatusCode.PermissionDenied,
            "This user is not allowed to use this service"));
    }

    return Task.FromResult(new HelloReply { Message = $"Hello, {request.Name}!" });
}
```

### Rich Error Details (google.rpc.Status)

```protobuf
import "google/rpc/error_details.proto";
```

```csharp
using Google.Rpc;
using Grpc.Core;
using Grpc.Core.Utils;

var badRequest = new Google.Rpc.BadRequest();
badRequest.FieldViolations.Add(new Google.Rpc.BadRequest.Types.FieldViolation
{
    Field = "name",
    Description = "Name must not be empty"
});

var status = new Google.Rpc.Status
{
    Code = (int)Google.Rpc.Code.InvalidArgument,
    Message = "Validation failed"
};
status.Details.Add(Google.Protobuf.WellKnownTypes.Any.Pack(badRequest));

throw status.ToRpcException();
```

### Handling Errors on the Client

```csharp
try
{
    var reply = await client.SayHelloAsync(new HelloRequest { Name = "" });
}
catch (RpcException ex) when (ex.StatusCode == StatusCode.InvalidArgument)
{
    Console.WriteLine($"Bad request: {ex.Status.Detail}");
}
catch (RpcException ex) when (ex.StatusCode == StatusCode.Unavailable)
{
    Console.WriteLine("Server unreachable — consider retrying");
}
catch (RpcException ex)
{
    Console.WriteLine($"RPC failed with {ex.StatusCode}: {ex.Status.Detail}");
}
```

### Retry Policies (Client-Side)

```csharp
var defaultMethodConfig = new MethodConfig
{
    Names = { MethodName.Default },
    RetryPolicy = new RetryPolicy
    {
        MaxAttempts = 5,
        InitialBackoff = TimeSpan.FromSeconds(1),
        MaxBackoff = TimeSpan.FromSeconds(5),
        BackoffMultiplier = 1.5,
        RetryableStatusCodes = { StatusCode.Unavailable }
    }
};

var channel = GrpcChannel.ForAddress("https://localhost:5001", new GrpcChannelOptions
{
    ServiceConfig = new ServiceConfig { MethodConfigs = { defaultMethodConfig } }
});
```

---

## 9. Deadlines, Timeouts & Cancellation

Unlike simple timeouts, a gRPC **deadline** is an absolute point in time that propagates across service calls — if service A calls service B which calls service C, the same overall deadline can flow through the whole chain.

### Setting a Deadline on the Client

```csharp
var deadline = DateTime.UtcNow.AddSeconds(3);

try
{
    var reply = await client.SayHelloAsync(
        new HelloRequest { Name = "Alice" },
        deadline: deadline);
}
catch (RpcException ex) when (ex.StatusCode == StatusCode.DeadlineExceeded)
{
    Console.WriteLine("Request timed out");
}
```

### Using CancellationToken

```csharp
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(3));

try
{
    var reply = await client.SayHelloAsync(
        new HelloRequest { Name = "Alice" },
        cancellationToken: cts.Token);
}
catch (RpcException ex) when (ex.StatusCode == StatusCode.Cancelled)
{
    Console.WriteLine("Request was cancelled");
}
```

### Respecting Deadlines on the Server

```csharp
public override async Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
{
    // context.CancellationToken fires automatically when the deadline is exceeded
    // or the client cancels — always pass it into downstream async calls
    await SomeExpensiveWorkAsync(context.CancellationToken);

    if (context.CancellationToken.IsCancellationRequested)
    {
        throw new RpcException(new Status(StatusCode.Cancelled, "Request was cancelled"));
    }

    return new HelloReply { Message = $"Hello, {request.Name}!" };
}
```

---

## 10. Metadata & Headers

Metadata is key-value data sent alongside RPCs — analogous to HTTP headers — useful for auth tokens, tracing IDs, or custom routing hints.

### Sending Metadata from the Client

```csharp
var headers = new Metadata
{
    { "authorization", $"Bearer {accessToken}" },
    { "x-request-id", Guid.NewGuid().ToString() }
};

var reply = await client.SayHelloAsync(
    new HelloRequest { Name = "Alice" },
    headers: headers);
```

### Reading Metadata on the Server

```csharp
public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
{
    var requestId = context.RequestHeaders.GetValue("x-request-id");
    Console.WriteLine($"Handling request {requestId}");

    return Task.FromResult(new HelloReply { Message = $"Hello, {request.Name}!" });
}
```

### Sending Response Metadata (Trailers) from the Server

```csharp
public override async Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
{
    // Response headers must be sent before any response message
    await context.WriteResponseHeadersAsync(new Metadata
    {
        { "x-server-version", "1.4.0" }
    });

    // Trailers are sent automatically at the end; you can add custom ones:
    context.ResponseTrailers.Add("x-processed-at", DateTime.UtcNow.ToString("o"));

    return new HelloReply { Message = $"Hello, {request.Name}!" };
}
```

### Reading Response Headers/Trailers on the Client

```csharp
using var call = client.SayHelloAsync(new HelloRequest { Name = "Alice" });

var responseHeaders = await call.ResponseHeadersAsync;
Console.WriteLine($"Server version: {responseHeaders.GetValue("x-server-version")}");

var reply = await call;

var trailers = call.GetTrailers();
Console.WriteLine($"Processed at: {trailers.GetValue("x-processed-at")}");
```

---

## 11. Interceptors (Middleware)

Interceptors let you inject cross-cutting logic (logging, auth, metrics) around every RPC call, similar to ASP.NET Core middleware.

### Server-Side Interceptor

```csharp
public class LoggingInterceptor : Interceptor
{
    private readonly ILogger<LoggingInterceptor> _logger;
    public LoggingInterceptor(ILogger<LoggingInterceptor> logger) => _logger = logger;

    public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
        TRequest request,
        ServerCallContext context,
        UnaryServerMethod<TRequest, TResponse> continuation)
    {
        var stopwatch = Stopwatch.StartNew();
        try
        {
            var response = await continuation(request, context);
            _logger.LogInformation("{Method} succeeded in {Elapsed}ms",
                context.Method, stopwatch.ElapsedMilliseconds);
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "{Method} failed after {Elapsed}ms",
                context.Method, stopwatch.ElapsedMilliseconds);
            throw;
        }
    }
}
```

Register it:

```csharp
builder.Services.AddGrpc(options =>
{
    options.Interceptors.Add<LoggingInterceptor>();
});
```

### Client-Side Interceptor

```csharp
public class AuthInterceptor : Interceptor
{
    private readonly string _token;
    public AuthInterceptor(string token) => _token = token;

    public override TResponse BlockingUnaryCall<TRequest, TResponse>(
        TRequest request,
        ClientInterceptorContext<TRequest, TResponse> context,
        BlockingUnaryCallContinuation<TRequest, TResponse> continuation)
    {
        var headers = context.Options.Headers ?? new Metadata();
        headers.Add("authorization", $"Bearer {_token}");

        var newOptions = context.Options.WithHeaders(headers);
        var newContext = new ClientInterceptorContext<TRequest, TResponse>(
            context.Method, context.Host, newOptions);

        return continuation(request, newContext);
    }
}

var channel = GrpcChannel.ForAddress("https://localhost:5001");
var invoker = channel.Intercept(new AuthInterceptor(accessToken));
var client = new Greeter.GreeterClient(invoker);
```

### Interceptor Chain Order

Multiple interceptors run in the order registered for outgoing calls, and in reverse order for the response path — like nested middleware.

---

## 12. Authentication & Security

### Transport Security (TLS)

gRPC in production always runs over TLS. `Grpc.AspNetCore` uses Kestrel's built-in HTTPS support:

```csharp
// appsettings.json
{
  "Kestrel": {
    "Endpoints": {
      "Grpc": {
        "Url": "https://localhost:5001",
        "Protocols": "Http2"
      }
    }
  }
}
```

### Token-Based Authentication (JWT)

```csharp
// Server: standard ASP.NET Core JWT auth applies directly to gRPC services
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = "https://identity.example.com";
        options.Audience = "grpc-api";
    });
builder.Services.AddAuthorization();

app.UseAuthentication();
app.UseAuthorization();
app.MapGrpcService<GreeterService>().RequireAuthorization();
```

```csharp
[Authorize]
public class SecureService : Secure.SecureBase
{
    public override Task<Reply> GetSecret(Request request, ServerCallContext context)
    {
        var userName = context.GetHttpContext().User.Identity?.Name;
        return Task.FromResult(new Reply { Message = $"Hello {userName}, here's your secret." });
    }
}
```

### mTLS (Mutual TLS) — Client Certificate Authentication

```csharp
// Server: require client certificates
builder.WebHost.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(https =>
    {
        https.ClientCertificateMode = ClientCertificateMode.RequireCertificate;
    });
});

// Client: attach a certificate to the channel
var handler = new HttpClientHandler();
handler.ClientCertificates.Add(new X509Certificate2("client.pfx", "password"));

var channel = GrpcChannel.ForAddress("https://localhost:5001", new GrpcChannelOptions
{
    HttpHandler = handler
});
```

### Per-Call Credentials

```csharp
var credentials = CallCredentials.FromInterceptor((context, metadata) =>
{
    metadata.Add("authorization", $"Bearer {GetFreshToken()}");
    return Task.CompletedTask;
});

var channel = GrpcChannel.ForAddress("https://localhost:5001", new GrpcChannelOptions
{
    Credentials = ChannelCredentials.Create(new SslCredentials(), credentials)
});
```

---

## 13. Client-Side Load Balancing & Channels

### Channel Reuse

A `GrpcChannel` manages an underlying HTTP/2 connection and should be **reused** across many calls rather than created per-request (channel creation is relatively expensive; the underlying connection supports many concurrent multiplexed calls).

```csharp
// Good: one long-lived channel, shared client
public class GreeterClientWrapper : IDisposable
{
    private readonly GrpcChannel _channel;
    private readonly Greeter.GreeterClient _client;

    public GreeterClientWrapper(string address)
    {
        _channel = GrpcChannel.ForAddress(address);
        _client = new Greeter.GreeterClient(_channel);
    }

    public Task<HelloReply> SayHelloAsync(string name) =>
        _client.SayHelloAsync(new HelloRequest { Name = name }).ResponseAsync;

    public void Dispose() => _channel.Dispose();
}
```

### Using IHttpClientFactory (Recommended in ASP.NET Core apps)

```csharp
builder.Services
    .AddGrpcClient<Greeter.GreeterClient>(options =>
    {
        options.Address = new Uri("https://localhost:5001");
    })
    .ConfigureChannel(options =>
    {
        options.MaxRetryAttempts = 5;
    });

// Injected wherever needed:
public class MyController
{
    private readonly Greeter.GreeterClient _client;
    public MyController(Greeter.GreeterClient client) => _client = client;
}
```

### Client-Side Load Balancing (Multiple Server Instances)

```csharp
var channel = GrpcChannel.ForAddress("dns:///my-service.internal:5001", new GrpcChannelOptions
{
    Credentials = ChannelCredentials.Insecure,
    ServiceConfig = new ServiceConfig
    {
        LoadBalancingConfigs = { new RoundRobinConfig() }
    }
});
```

This resolves multiple A/AAAA records behind a DNS name and round-robins calls across them — useful in Kubernetes with headless services.

### Keepalive Settings (Detecting Dead Connections)

```csharp
var channel = GrpcChannel.ForAddress("https://localhost:5001", new GrpcChannelOptions
{
    HttpHandler = new SocketsHttpHandler
    {
        PooledConnectionIdleTimeout = TimeSpan.FromMinutes(5),
        KeepAlivePingDelay = TimeSpan.FromSeconds(30),
        KeepAlivePingTimeout = TimeSpan.FromSeconds(10),
        EnableMultipleHttp2Connections = true
    }
});
```

---

## 14. gRPC-Web & Browser Support

Browsers can't natively make HTTP/2 trailer-based gRPC calls, so **gRPC-Web** provides a compatible protocol variant with a small translation layer.

### Server Configuration

```csharp
dotnet add package Grpc.AspNetCore.Web
```

```csharp
var app = builder.Build();

app.UseGrpcWeb(); // enable gRPC-Web middleware

app.MapGrpcService<GreeterService>().EnableGrpcWeb();
```

### Client (JavaScript/TypeScript, for reference)

```javascript
import { GreeterClient } from './generated/greet_grpc_web_pb';
import { HelloRequest } from './generated/greet_pb';

const client = new GreeterClient('https://localhost:5001');
const request = new HelloRequest();
request.setName('Alice');

client.sayHello(request, {}, (err, response) => {
  console.log(response.getMessage());
});
```

**Limitation:** gRPC-Web supports unary and server-streaming calls; client-streaming and bidirectional-streaming are **not** supported in browsers due to underlying HTTP/1.1-style limitations of the browser fetch/XHR APIs (unless using experimental Fetch streaming or a proxy like Envoy configured accordingly).

---

## 15. Testing gRPC Services

### Unit Testing a Service Directly (No Network)

```csharp
using Grpc.Core;
using Xunit;

public class GreeterServiceTests
{
    [Fact]
    public async Task SayHello_ValidName_ReturnsGreeting()
    {
        var service = new GreeterService(NullLogger<GreeterService>.Instance);
        var context = TestServerCallContext.Create(); // from Grpc.Core.Testing, or a hand-rolled fake

        var reply = await service.SayHello(new HelloRequest { Name = "Alice" }, context);

        Assert.Equal("Hello, Alice!", reply.Message);
    }
}
```

### In-Memory Integration Testing (WebApplicationFactory)

```csharp
dotnet add package Grpc.Net.Client.Testing
```

```csharp
public class GreeterIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    public GreeterIntegrationTests(WebApplicationFactory<Program> factory) => _factory = factory;

    [Fact]
    public async Task SayHello_EndToEnd_ReturnsExpectedMessage()
    {
        var handler = _factory.Server.CreateHandler();
        using var channel = GrpcChannel.ForAddress(_factory.Server.BaseAddress, new GrpcChannelOptions
        {
            HttpHandler = handler
        });

        var client = new Greeter.GreeterClient(channel);
        var reply = await client.SayHelloAsync(new HelloRequest { Name = "Bob" });

        Assert.Equal("Hello, Bob!", reply.Message);
    }
}
```

### Testing Streaming Methods

```csharp
[Fact]
public async Task WatchPrice_ReturnsMultipleUpdates()
{
    var service = new StockTickerService();
    var responseStream = new TestServerStreamWriter<PriceUpdate>(); // hand-rolled or from a test helper library
    var cts = new CancellationTokenSource();
    var context = TestServerCallContext.Create(cancellationToken: cts.Token);

    var task = service.WatchPrice(new WatchPriceRequest { Symbol = "MSFT" }, responseStream, context);

    await Task.Delay(2500);
    cts.Cancel();
    await task;

    Assert.True(responseStream.Messages.Count >= 2);
}
```

### Mocking a gRPC Client (for testing consumers of a gRPC client)

```csharp
using Moq;

var mockClient = new Mock<Greeter.GreeterClient>();
mockClient
    .Setup(c => c.SayHelloAsync(It.IsAny<HelloRequest>(), null, null, default))
    .Returns(CreateAsyncUnaryCall(new HelloReply { Message = "Hello, Test!" }));

// Helper to wrap a value as an AsyncUnaryCall<T>
static AsyncUnaryCall<T> CreateAsyncUnaryCall<T>(T response) =>
    new AsyncUnaryCall<T>(
        Task.FromResult(response),
        Task.FromResult(new Metadata()),
        () => Status.DefaultSuccess,
        () => new Metadata(),
        () => { });
```

---

## 16. Performance & Best Practices

- **Reuse channels.** Creating a new `GrpcChannel` per call is expensive; share one per target service.
- **Use streaming for large/incremental data** instead of one giant unary response — reduces peak memory and latency-to-first-byte.
- **Set deadlines on every call.** A call without a deadline can hang indefinitely if the server misbehaves.
- **Keep messages reasonably small.** Very large single messages (multi-GB) should be chunked via streaming rather than sent as one `bytes` field.
- **Design `.proto` files defensively.** Reserve removed field numbers, avoid renaming/retyping fields, keep new fields optional with sensible defaults.
- **Use interceptors for cross-cutting concerns** (logging, auth, tracing) instead of duplicating logic in every service method.
- **Enable compression for large payloads** (gzip is supported natively):
  ```csharp
  var client = new Greeter.GreeterClient(channel);
  var callOptions = new CallOptions().WithCompressionLevel(CompressionLevel.Optimal);
  ```
- **Monitor and propagate context deadlines** across service-to-service calls in a microservices chain to avoid one slow downstream call cascading into unbounded latency upstream.
- **Prefer `async`/`await` throughout** service implementations; avoid blocking calls (`.Result`, `.Wait()`) which can starve the thread pool under load.
- **Version your services carefully** — add new RPCs/fields rather than breaking existing ones; consider a new service name (`GreeterV2`) for breaking changes.

---

## 17. gRPC vs REST

| Aspect | gRPC | REST (JSON over HTTP/1.1) |
|---|---|---|
| Transport | HTTP/2 | Typically HTTP/1.1 (HTTP/2 possible but less common) |
| Payload format | Protobuf (binary) | JSON (text) |
| Contract | Strongly typed `.proto`, generated code | Often loosely typed (OpenAPI optional) |
| Streaming | Native (all 4 patterns) | Limited (SSE, WebSockets needed for real streaming) |
| Browser support | Needs gRPC-Web layer | Native |
| Human readability | Not directly readable (binary) | Readable JSON |
| Performance | Generally faster (smaller payloads, multiplexing) | Slower for high-throughput/low-latency needs |
| Tooling maturity | Strong in backend/microservices | Universal, simplest for public APIs |
| Best fit | Internal microservice-to-microservice communication, streaming, polyglot systems | Public-facing APIs, simple CRUD, broad client compatibility (including browsers without extra layers) |

**Rule of thumb:** use gRPC for internal service-to-service communication (especially with streaming needs or performance-sensitive paths), and REST/JSON (or GraphQL) for public-facing APIs consumed directly by browsers or third parties.

---

## 18. Quick Reference

### Messaging Pattern Syntax Summary

```protobuf
service Example {
  rpc Unary (Req) returns (Res);                       // 1 -> 1
  rpc ServerStream (Req) returns (stream Res);          // 1 -> many
  rpc ClientStream (stream Req) returns (Res);          // many -> 1
  rpc BidiStream (stream Req) returns (stream Res);     // many -> many
}
```

### C# Server Method Signatures

| Pattern | Server Override Signature |
|---|---|
| Unary | `Task<Res> Method(Req request, ServerCallContext context)` |
| Server streaming | `Task Method(Req request, IServerStreamWriter<Res> responseStream, ServerCallContext context)` |
| Client streaming | `Task<Res> Method(IAsyncStreamReader<Req> requestStream, ServerCallContext context)` |
| Bidirectional | `Task Method(IAsyncStreamReader<Req> requestStream, IServerStreamWriter<Res> responseStream, ServerCallContext context)` |

### C# Client Call Signatures

| Pattern | Client Call |
|---|---|
| Unary | `await client.MethodAsync(request)` |
| Server streaming | `client.Method(request)` then `await foreach (var m in call.ResponseStream.ReadAllAsync())` |
| Client streaming | `client.Method()`, loop `await call.RequestStream.WriteAsync(msg)`, then `await call.RequestStream.CompleteAsync()`, then `await call.ResponseAsync` |
| Bidirectional | `client.Method()`, read and write both streams concurrently via separate tasks |

### Common Status Codes At a Glance

| Code | Retryable? |
|---|---|
| `UNAVAILABLE` | Yes |
| `DEADLINE_EXCEEDED` | Sometimes (idempotent operations only) |
| `RESOURCE_EXHAUSTED` | Yes, with backoff |
| `INVALID_ARGUMENT` | No — fix the request |
| `NOT_FOUND` | No |
| `PERMISSION_DENIED` / `UNAUTHENTICATED` | No — fix credentials |
| `INTERNAL` | No, unless known transient bug |

---

*Practice idea: build a small "order processing" system with three RPCs on one service — a unary `PlaceOrder`, a server-streaming `WatchOrderStatus` (pushing status updates as an order moves through fulfillment), and a bidirectional `SupportChat` for live customer support tied to that order — then add a logging interceptor and JWT authentication across all three.*
