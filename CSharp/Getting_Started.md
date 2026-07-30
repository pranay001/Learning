# The Complete C# Learning Guide

A structured reference covering C# from fundamentals to advanced topics, including collections (Queue, Stack, etc.), delegates, events, generics, LINQ, async/await, and more.

---

## Table of Contents

1. [Introduction to C#](#1-introduction-to-c)
2. [Basic Syntax & Data Types](#2-basic-syntax--data-types)
3. [Control Flow](#3-control-flow)
4. [Object-Oriented Programming](#4-object-oriented-programming)
5. [Interfaces & Abstract Classes](#5-interfaces--abstract-classes)
6. [Collections](#6-collections)
7. [Generics](#7-generics)
8. [Delegates](#8-delegates)
9. [Events](#9-events)
10. [Lambda Expressions & Anonymous Methods](#10-lambda-expressions--anonymous-methods)
11. [LINQ](#11-linq)
12. [Exception Handling](#12-exception-handling)
13. [Asynchronous Programming (async/await, Tasks)](#13-asynchronous-programming-asyncawait-tasks)
14. [Multithreading](#14-multithreading)
15. [Reflection & Attributes](#15-reflection--attributes)
16. [Memory Management & IDisposable](#16-memory-management--idisposable)
17. [Nullable Reference Types & Pattern Matching](#17-nullable-reference-types--pattern-matching)
18. [Records, Structs & Value Types](#18-records-structs--value-types)
19. [Extension Methods](#19-extension-methods)
20. [Advanced Topics](#20-advanced-topics)
21. [Best Practices](#21-best-practices)

---

## 1. Introduction to C#

C# ("C Sharp") is a modern, object-oriented, type-safe programming language developed by Microsoft, running primarily on the **.NET** platform. It compiles to **Intermediate Language (IL)**, which the **CLR** (Common Language Runtime) executes via Just-In-Time (JIT) compilation.

**Key characteristics:**
- Statically typed with type inference (`var`)
- Garbage collected (automatic memory management)
- Supports OOP, functional, and imperative styles
- Cross-platform via .NET (Windows, Linux, macOS)

**Minimal program (top-level statements, C# 9+):**

```csharp
Console.WriteLine("Hello, World!");
```

**Traditional structure:**

```csharp
using System;

namespace MyApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello, World!");
        }
    }
}
```

---

## 2. Basic Syntax & Data Types

### Value Types (stored on stack, contain data directly)

| Type | Description | Size |
|---|---|---|
| `int` | Integer | 4 bytes |
| `long` | Large integer | 8 bytes |
| `float` | Single-precision float | 4 bytes |
| `double` | Double-precision float | 8 bytes |
| `decimal` | High-precision decimal (financial) | 16 bytes |
| `bool` | True/false | 1 byte |
| `char` | Single Unicode character | 2 bytes |
| `struct` | User-defined value type | varies |

### Reference Types (stored on heap, variable holds a reference)

- `string`, arrays, classes, delegates, interfaces, `object`

### Variables & Type Inference

```csharp
int age = 30;
var name = "Alice";        // compiler infers string
const double Pi = 3.14159; // compile-time constant
readonly int id;           // runtime constant, set once (in constructor)
```

### Nullable Value Types

```csharp
int? maybeNumber = null;
if (maybeNumber.HasValue) { Console.WriteLine(maybeNumber.Value); }
int result = maybeNumber ?? 0; // null-coalescing operator
```

### String Interpolation

```csharp
string message = $"Hello, {name}! You are {age} years old.";
```

---

## 3. Control Flow

```csharp
// If/else
if (age >= 18) Console.WriteLine("Adult");
else Console.WriteLine("Minor");

// Switch expression (C# 8+)
string category = age switch
{
    < 13 => "Child",
    < 20 => "Teenager",
    _ => "Adult"
};

// Loops
for (int i = 0; i < 10; i++) { }
foreach (var item in collection) { }
while (condition) { }
do { } while (condition);

// Jump statements
break; continue; return; goto Label;
```

---

## 4. Object-Oriented Programming

### Classes & Objects

```csharp
public class Person
{
    // Fields
    private string _name;

    // Auto-implemented properties
    public string Name { get; set; }
    public int Age { get; private set; }

    // Constructor
    public Person(string name, int age)
    {
        Name = name;
        Age = age;
    }

    // Method
    public void Greet() => Console.WriteLine($"Hi, I'm {Name}");
}

var p = new Person("Bob", 25);
p.Greet();
```

### The Four Pillars of OOP

1. **Encapsulation** — bundling data and methods, controlling access via `private`/`public`/`protected`/`internal`.
2. **Inheritance** — a class derives from a base class using `:`.
3. **Polymorphism** — overriding (`virtual`/`override`) and overloading methods.
4. **Abstraction** — exposing only essential features via interfaces/abstract classes.

### Inheritance & Polymorphism

```csharp
public class Animal
{
    public virtual string MakeSound() => "Some generic sound";
}

public class Dog : Animal
{
    public override string MakeSound() => "Woof!";
}

Animal a = new Dog();
Console.WriteLine(a.MakeSound()); // "Woof!" — runtime polymorphism
```

### Static Members

```csharp
public class Counter
{
    public static int Count = 0;
    public Counter() => Count++;
}
```

### Access Modifiers

| Modifier | Accessible from |
|---|---|
| `public` | Anywhere |
| `private` | Same class only |
| `protected` | Same class + derived classes |
| `internal` | Same assembly |
| `protected internal` | Same assembly OR derived classes |
| `private protected` | Same assembly AND derived classes |

---

## 5. Interfaces & Abstract Classes

```csharp
public interface IShape
{
    double Area();
    double Perimeter();
}

public abstract class ShapeBase : IShape
{
    public abstract double Area();
    public abstract double Perimeter();
    public void Describe() => Console.WriteLine($"Area: {Area()}");
}

public class Circle : ShapeBase
{
    private readonly double _radius;
    public Circle(double radius) => _radius = radius;

    public override double Area() => Math.PI * _radius * _radius;
    public override double Perimeter() => 2 * Math.PI * _radius;
}
```

**Interface vs Abstract Class:**
- Interfaces define a contract; a class can implement multiple interfaces.
- Abstract classes can hold shared implementation/state; a class can inherit only one.
- Since C# 8, interfaces can have **default method implementations**.

---

## 6. Collections

### Array

```csharp
int[] numbers = { 1, 2, 3, 4, 5 };
int[,] matrix = new int[3, 3]; // multidimensional
```

### List\<T>

Dynamic, resizable, index-based.

```csharp
List<string> names = new List<string> { "Alice", "Bob" };
names.Add("Carol");
names.Remove("Bob");
names.Sort();
```

### Dictionary\<TKey, TValue>

Key-value pairs with O(1) average lookup.

```csharp
var ages = new Dictionary<string, int>
{
    ["Alice"] = 30,
    ["Bob"] = 25
};
if (ages.TryGetValue("Alice", out int age)) Console.WriteLine(age);
```

### Queue\<T> (FIFO — First In, First Out)

A queue processes elements in the order they were added — think of a line at a checkout counter.

```csharp
Queue<string> ticketQueue = new Queue<string>();

ticketQueue.Enqueue("Customer A"); // add to the back
ticketQueue.Enqueue("Customer B");
ticketQueue.Enqueue("Customer C");

string served = ticketQueue.Dequeue(); // removes & returns "Customer A"
string next = ticketQueue.Peek();      // "Customer B" — view without removing

Console.WriteLine(ticketQueue.Count);        // 2
Console.WriteLine(ticketQueue.Contains("Customer C")); // true

foreach (var customer in ticketQueue)
{
    Console.WriteLine(customer);
}
```

**Common Queue use cases:**
- Task scheduling / job processing
- Breadth-first search (BFS) in graph/tree traversal
- Print spoolers, message buffers, producer-consumer pipelines

**Related types:**
- `PriorityQueue<TElement, TPriority>` (C# 10+) — dequeues by priority, not insertion order.
- `ConcurrentQueue<T>` — thread-safe FIFO queue in `System.Collections.Concurrent`.

```csharp
var pq = new PriorityQueue<string, int>();
pq.Enqueue("Low priority job", 3);
pq.Enqueue("High priority job", 1);
pq.Enqueue("Medium priority job", 2);
Console.WriteLine(pq.Dequeue()); // "High priority job" (lowest number = highest priority)
```

### Stack\<T> (LIFO — Last In, First Out)

```csharp
Stack<int> history = new Stack<int>();
history.Push(1);
history.Push(2);
history.Push(3);

int last = history.Pop();  // 3, removes it
int top = history.Peek();  // 2, view without removing
```

**Use cases:** undo/redo, expression evaluation, DFS traversal, call stacks.

### HashSet\<T>

Unordered collection of unique elements, backed by a hash table.

```csharp
var uniqueIds = new HashSet<int> { 1, 2, 3 };
uniqueIds.Add(2); // ignored, already exists
uniqueIds.UnionWith(new[] { 3, 4, 5 });
```

### SortedList / SortedDictionary / SortedSet

Maintain elements in sorted order automatically.

```csharp
var sorted = new SortedDictionary<string, int>();
sorted["Zed"] = 1;
sorted["Alice"] = 2; // iterating yields Alice before Zed
```

### LinkedList\<T>

Doubly-linked list — O(1) insertion/removal at known nodes, O(n) lookup.

```csharp
var linked = new LinkedList<int>();
linked.AddLast(1);
linked.AddFirst(0);
```

### Collection Comparison Table

| Collection | Order | Duplicates | Lookup | Typical Use |
|---|---|---|---|---|
| `List<T>` | Insertion | Yes | O(n) / O(1) by index | General purpose |
| `Queue<T>` | FIFO | Yes | O(n) | Sequential processing |
| `Stack<T>` | LIFO | Yes | O(n) | Undo, recursion simulation |
| `Dictionary<K,V>` | Unordered | Unique keys | O(1) avg | Fast key lookup |
| `HashSet<T>` | Unordered | No | O(1) avg | Uniqueness checks |
| `SortedDictionary<K,V>` | Sorted | Unique keys | O(log n) | Ordered key-value data |
| `LinkedList<T>` | Insertion | Yes | O(n) | Frequent insert/remove |

### Immutable & Concurrent Collections

```csharp
using System.Collections.Immutable;
var immutableList = ImmutableList.Create(1, 2, 3);

using System.Collections.Concurrent;
var concurrentDict = new ConcurrentDictionary<string, int>();
var concurrentBag = new ConcurrentBag<int>();
```

---

## 7. Generics

Generics allow types/methods to operate on data without specifying a concrete type upfront, providing type safety and performance (no boxing).

```csharp
public class Box<T>
{
    private T _item;
    public void Set(T item) => _item = item;
    public T Get() => _item;
}

var intBox = new Box<int>();
intBox.Set(42);
```

### Generic Methods

```csharp
public static T Max<T>(T a, T b) where T : IComparable<T>
{
    return a.CompareTo(b) > 0 ? a : b;
}
```

### Generic Constraints

```csharp
public class Repository<T> where T : class, IEntity, new()
{
    public T CreateNew() => new T();
}
```

| Constraint | Meaning |
|---|---|
| `where T : struct` | Value type |
| `where T : class` | Reference type |
| `where T : new()` | Has parameterless constructor |
| `where T : BaseClass` | Derives from BaseClass |
| `where T : IInterface` | Implements interface |
| `where T : notnull` | Non-nullable |

### Covariance & Contravariance

```csharp
IEnumerable<string> strings = new List<string>();
IEnumerable<object> objects = strings; // covariance (out T)

Action<object> act = obj => Console.WriteLine(obj);
Action<string> actStr = act; // contravariance (in T)
```

---

## 8. Delegates

A **delegate** is a type-safe function pointer — an object that references a method with a specific signature, enabling methods to be passed as parameters, stored in variables, and invoked dynamically.

### Declaring and Using a Delegate

```csharp
// Declare a delegate type matching a method signature
public delegate int MathOperation(int a, int b);

public static int Add(int a, int b) => a + b;
public static int Multiply(int a, int b) => a * b;

// Assign and invoke
MathOperation op = Add;
Console.WriteLine(op(3, 4)); // 7

op = Multiply;
Console.WriteLine(op(3, 4)); // 12
```

### Multicast Delegates

A delegate can reference multiple methods; invoking it calls each in order.

```csharp
public delegate void Notify(string message);

public static void LogToConsole(string msg) => Console.WriteLine($"Console: {msg}");
public static void LogToFile(string msg) => Console.WriteLine($"File: {msg}");

Notify notify = LogToConsole;
notify += LogToFile;   // combine delegates
notify("System started");
// Output:
// Console: System started
// File: System started

notify -= LogToConsole; // remove a method
```

### Built-in Generic Delegates

You rarely need to declare custom delegate types — the framework provides generic ones:

```csharp
Func<int, int, int> add = (a, b) => a + b;       // has a return value
Action<string> print = msg => Console.WriteLine(msg); // no return value
Predicate<int> isEven = n => n % 2 == 0;          // returns bool

Console.WriteLine(add(2, 3));   // 5
print("Hello");
Console.WriteLine(isEven(4));   // true
```

| Delegate | Signature | Purpose |
|---|---|---|
| `Action` | `void()` | No params, no return |
| `Action<T>` | `void(T)` | Params, no return (up to 16 params) |
| `Func<T, TResult>` | `TResult(T)` | Params + return value |
| `Predicate<T>` | `bool(T)` | Returns true/false |
| `Comparison<T>` | `int(T, T)` | Used in sorting |

### Delegates as Method Parameters (Callbacks)

```csharp
public static void ProcessNumbers(List<int> numbers, Func<int, bool> filter)
{
    foreach (var n in numbers)
        if (filter(n)) Console.WriteLine(n);
}

ProcessNumbers(new List<int> { 1, 2, 3, 4 }, n => n % 2 == 0); // prints 2, 4
```

### Why Delegates Matter

- Enable **callbacks** and **event-driven** designs.
- Form the basis of **events**, **LINQ**, and **async lambdas**.
- Allow behavior (not just data) to be passed around, similar to first-class functions.

---

## 9. Events

Events build on delegates to implement the **publisher/subscriber** pattern, restricting external code to only subscribing/unsubscribing (not invoking or reassigning).

```csharp
public class Button
{
    // Declare an event based on a delegate
    public event EventHandler Clicked;

    public void SimulateClick()
    {
        // Raise the event (null-safe invocation)
        Clicked?.Invoke(this, EventArgs.Empty);
    }
}

public class Program
{
    static void Main()
    {
        var button = new Button();
        button.Clicked += Button_Clicked; // subscribe
        button.SimulateClick();           // triggers handler
    }

    static void Button_Clicked(object sender, EventArgs e)
    {
        Console.WriteLine("Button was clicked!");
    }
}
```

### Custom Event Arguments

```csharp
public class PriceChangedEventArgs : EventArgs
{
    public decimal OldPrice { get; }
    public decimal NewPrice { get; }
    public PriceChangedEventArgs(decimal oldPrice, decimal newPrice)
    {
        OldPrice = oldPrice;
        NewPrice = newPrice;
    }
}

public class Stock
{
    public event EventHandler<PriceChangedEventArgs> PriceChanged;
    private decimal _price;

    public decimal Price
    {
        get => _price;
        set
        {
            if (value != _price)
            {
                var old = _price;
                _price = value;
                PriceChanged?.Invoke(this, new PriceChangedEventArgs(old, value));
            }
        }
    }
}
```

**Delegate vs Event:**
- A public delegate field can be overwritten (`obj.Del = null`) or invoked from outside the class.
- An event can only be `+=`/`-=` from outside; it can only be raised from within the declaring class.

---

## 10. Lambda Expressions & Anonymous Methods

```csharp
// Anonymous method (older syntax)
Func<int, int> square = delegate (int x) { return x * x; };

// Lambda expression (modern, preferred)
Func<int, int> squareLambda = x => x * x;

// Multi-statement lambda
Func<int, int, int> sumThenDouble = (a, b) =>
{
    int sum = a + b;
    return sum * 2;
};

// Lambdas capture outer variables (closures)
int factor = 10;
Func<int, int> multiplyByFactor = x => x * factor;
```

---

## 11. LINQ

**Language Integrated Query** lets you query collections, databases (via EF Core), and XML using a consistent, declarative syntax.

### Method Syntax vs Query Syntax

```csharp
var numbers = new List<int> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

// Method syntax
var evenSquares = numbers.Where(n => n % 2 == 0).Select(n => n * n).ToList();

// Query syntax
var evenSquares2 = from n in numbers
                    where n % 2 == 0
                    select n * n;
```

### Common LINQ Operators

```csharp
numbers.OrderBy(n => n);
numbers.OrderByDescending(n => n);
numbers.GroupBy(n => n % 3);
numbers.Sum();
numbers.Average();
numbers.Max();
numbers.Min();
numbers.Count(n => n > 5);
numbers.Any(n => n > 100);
numbers.All(n => n > 0);
numbers.First();
numbers.FirstOrDefault(n => n > 50);  // returns default(int) = 0 if none found
numbers.Take(3);
numbers.Skip(3);
numbers.Distinct();
numbers.Aggregate((acc, n) => acc + n);

// Joining two collections
var joined = from p in people
             join o in orders on p.Id equals o.PersonId
             select new { p.Name, o.Product };
```

### Deferred Execution

LINQ queries are **lazily evaluated** — the query doesn't run until enumerated (via `foreach`, `.ToList()`, `.Count()`, etc.).

```csharp
var query = numbers.Where(n => n > 2); // not executed yet
numbers.Add(100);
foreach (var n in query) Console.WriteLine(n); // includes 100 too
```

---

## 12. Exception Handling

```csharp
try
{
    int result = 10 / int.Parse("0");
}
catch (DivideByZeroException ex)
{
    Console.WriteLine($"Math error: {ex.Message}");
}
catch (FormatException ex) when (ex.Message.Contains("input"))
{
    Console.WriteLine("Specific format issue");
}
catch (Exception ex)
{
    Console.WriteLine($"General error: {ex.Message}");
    throw; // re-throw, preserving stack trace
}
finally
{
    Console.WriteLine("Always runs, used for cleanup");
}
```

### Custom Exceptions

```csharp
public class InsufficientFundsException : Exception
{
    public decimal ShortfallAmount { get; }
    public InsufficientFundsException(string message, decimal shortfall)
        : base(message)
    {
        ShortfallAmount = shortfall;
    }
}

throw new InsufficientFundsException("Not enough balance", 50.00m);
```

---

## 13. Asynchronous Programming (async/await, Tasks)

Asynchronous code lets long-running operations (I/O, network calls) run without blocking the calling thread.

```csharp
public async Task<string> FetchDataAsync()
{
    using var client = new HttpClient();
    string result = await client.GetStringAsync("https://example.com");
    return result;
}

public async Task RunAsync()
{
    Console.WriteLine("Starting...");
    string data = await FetchDataAsync(); // yields control until complete
    Console.WriteLine($"Received {data.Length} characters");
}
```

### Task Combinators

```csharp
Task task1 = Task.Delay(1000);
Task task2 = Task.Delay(2000);
await Task.WhenAll(task1, task2);   // wait for both
await Task.WhenAny(task1, task2);   // wait for the first to finish

Task<int> compute = Task.Run(() => ExpensiveComputation()); // offload to thread pool
int value = await compute;
```

### async/await Key Rules

- An `async` method should return `Task`, `Task<T>`, or `void` (only for event handlers).
- `await` doesn't create a new thread; it frees the current thread while waiting.
- Use `ConfigureAwait(false)` in library code to avoid deadlocks from capturing the synchronization context.
- Avoid `async void` except for event handlers, since exceptions can't be caught by the caller.

---

## 14. Multithreading

```csharp
// Raw Thread
Thread t = new Thread(() => Console.WriteLine("Running on new thread"));
t.Start();
t.Join(); // wait for completion

// Thread pool via Task
Task.Run(() => Console.WriteLine("Runs on thread pool"));

// Synchronization primitives
private static readonly object _lock = new object();
lock (_lock)
{
    // critical section — only one thread at a time
}

// Parallel loops
Parallel.For(0, 100, i => { /* process i */ });
Parallel.ForEach(collection, item => { /* process item */ });
```

**Concurrency tools:** `Monitor`, `Mutex`, `Semaphore`/`SemaphoreSlim`, `ReaderWriterLockSlim`, `Interlocked`, `CancellationToken`.

```csharp
var cts = new CancellationTokenSource();
Task.Run(() =>
{
    while (!cts.Token.IsCancellationRequested)
    {
        // do work
    }
}, cts.Token);
cts.Cancel();
```

---

## 15. Reflection & Attributes

Reflection inspects and manipulates types, methods, and members at runtime.

```csharp
Type type = typeof(Person);
Console.WriteLine(type.Name);
foreach (var prop in type.GetProperties())
    Console.WriteLine(prop.Name);

// Creating an instance dynamically
object instance = Activator.CreateInstance(type);

// Invoking a method dynamically
MethodInfo method = type.GetMethod("Greet");
method.Invoke(instance, null);
```

### Custom Attributes

```csharp
[AttributeUsage(AttributeTargets.Property)]
public class RequiredAttribute : Attribute { }

public class User
{
    [Required]
    public string Username { get; set; }
}

// Reading attributes via reflection
var prop = typeof(User).GetProperty("Username");
bool isRequired = prop.GetCustomAttributes(typeof(RequiredAttribute), false).Any();
```

---

## 16. Memory Management & IDisposable

C# uses **garbage collection** for managed memory, but unmanaged resources (file handles, network connections, DB connections) must be released explicitly via `IDisposable`.

```csharp
public class ResourceHolder : IDisposable
{
    private bool _disposed = false;
    private FileStream _stream = new FileStream("data.txt", FileMode.OpenOrCreate);

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        if (disposing)
        {
            _stream?.Dispose(); // free managed resources
        }
        _disposed = true;
    }

    ~ResourceHolder() => Dispose(false); // finalizer, backup cleanup
}

// Automatic disposal
using (var holder = new ResourceHolder())
{
    // use holder
} // Dispose() called automatically

// C# 8+ using declaration
using var holder2 = new ResourceHolder();
```

**Garbage Collection generations:** Gen 0 (short-lived), Gen 1, Gen 2 (long-lived) — objects are promoted between generations if they survive collections.

---

## 17. Nullable Reference Types & Pattern Matching

```csharp
#nullable enable

string? nullableName = null;         // explicitly nullable
string nonNullableName = "required"; // compiler warns if assigned null

// Pattern matching
object obj = 5;
if (obj is int number && number > 0)
    Console.WriteLine($"Positive int: {number}");

// Switch pattern matching
string Describe(object o) => o switch
{
    int n when n < 0 => "Negative number",
    int n => $"Number: {n}",
    string s => $"String of length {s.Length}",
    null => "Null value",
    _ => "Unknown"
};

// Record pattern matching (C# 10+)
record Point(int X, int Y);
string Classify(Point p) => p switch
{
    { X: 0, Y: 0 } => "Origin",
    { X: 0 } => "On Y-axis",
    _ => "Elsewhere"
};
```

---

## 18. Records, Structs & Value Types

### Records (immutable reference types, value-based equality)

```csharp
public record Person(string Name, int Age);

var p1 = new Person("Alice", 30);
var p2 = p1 with { Age = 31 }; // non-destructive mutation, creates a new record

Console.WriteLine(p1 == p1); // true (value-based equality)
```

### Structs (value types)

```csharp
public struct Point
{
    public int X;
    public int Y;
    public Point(int x, int y) { X = x; Y = y; }
}

// record struct (C# 10+) combines value semantics with record syntax
public record struct Coordinate(double Lat, double Lng);
```

**Struct vs Class:**

| | struct | class |
|---|---|---|
| Storage | Stack (usually) | Heap |
| Default | Value type | Reference type |
| Inheritance | No (except interfaces) | Yes |
| Null | Not nullable by default | Nullable |
| Copy behavior | Copied by value | Copied by reference |

---

## 19. Extension Methods

Extension methods add new methods to existing types without modifying their source.

```csharp
public static class StringExtensions
{
    public static bool IsPalindrome(this string s)
    {
        string clean = new string(s.Where(char.IsLetterOrDigit).ToArray()).ToLower();
        return clean == new string(clean.Reverse().ToArray());
    }
}

// Usage — looks like an instance method
bool result = "racecar".IsPalindrome(); // true
```

---

## 20. Advanced Topics

### Indexers

```csharp
public class Matrix
{
    private double[,] _data = new double[10, 10];
    public double this[int row, int col]
    {
        get => _data[row, col];
        set => _data[row, col] = value;
    }
}
```

### Operator Overloading

```csharp
public struct Vector2
{
    public double X, Y;
    public static Vector2 operator +(Vector2 a, Vector2 b)
        => new Vector2 { X = a.X + b.X, Y = a.Y + b.Y };
}
```

### Yield & Iterators

```csharp
public IEnumerable<int> Fibonacci(int count)
{
    int a = 0, b = 1;
    for (int i = 0; i < count; i++)
    {
        yield return a;
        (a, b) = (b, a + b);
    }
}
```

### Tuples & Deconstruction

```csharp
(string Name, int Age) person = ("Alice", 30);
var (name, age) = person;

public (int Min, int Max) GetRange(int[] nums) => (nums.Min(), nums.Max());
```

### Span\<T> & Memory\<T>

High-performance, allocation-free access to contiguous memory (arrays, stack memory, strings).

```csharp
Span<int> span = stackalloc int[5] { 1, 2, 3, 4, 5 };
Span<int> slice = span.Slice(1, 3);
```

### Dependency Injection (conceptual)

```csharp
public interface ILogger { void Log(string message); }
public class ConsoleLogger : ILogger
{
    public void Log(string message) => Console.WriteLine(message);
}

public class OrderService
{
    private readonly ILogger _logger;
    public OrderService(ILogger logger) => _logger = logger; // constructor injection
}
```

### Reflection-based Serialization (System.Text.Json)

```csharp
var json = System.Text.Json.JsonSerializer.Serialize(person);
var obj = System.Text.Json.JsonSerializer.Deserialize<Person>(json);
```

### Expression Trees

```csharp
Expression<Func<int, bool>> expr = n => n > 5;
// Can be inspected/compiled at runtime, used heavily by EF Core to translate LINQ to SQL
Func<int, bool> compiled = expr.Compile();
```

### Unsafe Code & Pointers

```csharp
unsafe
{
    int x = 10;
    int* p = &x;
    Console.WriteLine(*p);
}
```

---

## 21. Best Practices

- Prefer `List<T>`/`Dictionary<K,V>` over arrays unless size is fixed and performance-critical.
- Use `Queue<T>` for FIFO scenarios (task processing, BFS) and `Stack<T>` for LIFO (undo, DFS).
- Favor `Func`/`Action`/`Predicate` over custom delegate types unless a domain-specific name adds clarity.
- Use `events` (not raw public delegates) when exposing notifications from a class.
- Always dispose unmanaged resources with `using`/`IDisposable`.
- Prefer `async`/`await` for I/O-bound work; use `Task.Run` sparingly for CPU-bound work.
- Enable nullable reference types (`#nullable enable`) in new projects to catch null bugs at compile time.
- Use LINQ for readability, but be mindful of performance in hot paths (it introduces some overhead).
- Follow SOLID principles; prefer interfaces and dependency injection for testable, decoupled code.

---

*This guide covers C# from fundamentals through advanced runtime and language features. For hands-on practice, try implementing a small project (e.g., a task scheduler using `Queue<T>` and events, or an order-processing pipeline using LINQ and async/await) to reinforce these concepts.*
