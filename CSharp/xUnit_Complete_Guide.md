# The Complete xUnit Testing Guide (C#)

An extensive, example-driven reference for **xUnit.net**, the testing framework used by the .NET runtime team itself and the default choice in many modern .NET project templates.

---

## Table of Contents

1. [Introduction & Setup](#1-introduction--setup)
2. [Test Structure Basics](#2-test-structure-basics)
3. [Setup & Teardown (Constructor / IDisposable / Fixtures)](#3-setup--teardown-constructor--idisposable--fixtures)
4. [Assertions](#4-assertions)
5. [Theory & InlineData (Parameterized Tests)](#5-theory--inlinedata-parameterized-tests)
6. [MemberData & ClassData](#6-memberdata--classdata)
7. [Shared Context: Class Fixtures & Collection Fixtures](#7-shared-context-class-fixtures--collection-fixtures)
8. [Exception Testing](#8-exception-testing)
9. [Async Test Support](#9-async-test-support)
10. [Mocking with xUnit (Moq / NSubstitute)](#10-mocking-with-xunit-moq--nsubstitute)
11. [Test Output & Diagnostics](#11-test-output--diagnostics)
12. [Test Collections & Parallelism](#12-test-collections--parallelism)
13. [Skipping & Conditional Tests](#13-skipping--conditional-tests)
14. [Custom Attributes & Extensibility](#14-custom-attributes--extensibility)
15. [Running Tests (CLI & CI)](#15-running-tests-cli--ci)
16. [xUnit vs NUnit: Key Differences](#16-xunit-vs-nunit-key-differences)
17. [Best Practices](#17-best-practices)
18. [Quick Reference Tables](#18-quick-reference-tables)

---

## 1. Introduction & Setup

**xUnit.net** is an open-source testing framework created by the original inventor of NUnit v2, designed to be leaner, more extensible, and more aligned with modern .NET idioms — e.g., using constructors instead of `[SetUp]`, and `IDisposable` instead of `[TearDown]`.

### Installing xUnit

```bash
dotnet new xunit -n MyApp.Tests
cd MyApp.Tests
dotnet add reference ../MyApp/MyApp.csproj
```

Or add manually to an existing class library:

```bash
dotnet add package xunit
dotnet add package xunit.runner.visualstudio
dotnet add package Microsoft.NET.Test.Sdk
```

### Minimal .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.10.0" />
    <PackageReference Include="xunit" Version="2.8.1" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.8" />
  </ItemGroup>
</Project>
```

### Your First Test

```csharp
using Xunit;

namespace MyApp.Tests
{
    public class CalculatorTests
    {
        [Fact]
        public void Add_TwoPositiveNumbers_ReturnsSum()
        {
            // Arrange
            var calculator = new Calculator();

            // Act
            int result = calculator.Add(2, 3);

            // Assert
            Assert.Equal(5, result);
        }
    }
}
```

Note: xUnit test classes need **no `[TestFixture]`-style attribute** — any public class containing `[Fact]`/`[Theory]` methods is automatically discovered.

Run with:

```bash
dotnet test
```

---

## 2. Test Structure Basics

### Core Attributes

| Attribute | Purpose |
|---|---|
| `[Fact]` | A single, non-parameterized test |
| `[Theory]` | A parameterized test, combined with a data attribute |
| `[InlineData(...)]` | Inline data for a `[Theory]` |
| `[MemberData(...)]` | Data sourced from a property/method/field |
| `[ClassData(...)]` | Data sourced from a class implementing `IEnumerable<object[]>` |

```csharp
public class StringUtilsTests
{
    [Fact]
    public void Reverse_SimpleString_ReturnsReversedString()
    {
        string result = StringUtils.Reverse("hello");
        Assert.Equal("olleh", result);
    }

    [Fact]
    public void Reverse_EmptyString_ReturnsEmptyString()
    {
        Assert.Equal("", StringUtils.Reverse(""));
    }
}
```

### Naming Conventions

```csharp
[Fact]
public void Withdraw_AmountExceedsBalance_ThrowsInsufficientFundsException() { }

[Fact]
public void Withdraw_ValidAmount_DecreasesBalance() { }
```

---

## 3. Setup & Teardown (Constructor / IDisposable / Fixtures)

xUnit deliberately has **no `[SetUp]`/`[TearDown]` attributes**. Instead, it leans on plain C# mechanisms:

- The **constructor** runs before each test (equivalent to `[SetUp]`).
- **`IDisposable.Dispose()`** runs after each test (equivalent to `[TearDown]`).
- **`IClassFixture<T>`** and **`ICollectionFixture<T>`** handle one-time setup/teardown shared across tests (equivalent to `[OneTimeSetUp]`/`[OneTimeTearDown]`).

### Per-Test Setup/Teardown

```csharp
public class DatabaseTests : IDisposable
{
    private readonly SqlConnection _connection;

    // Constructor = runs before EACH test (like [SetUp])
    public DatabaseTests()
    {
        _connection = new SqlConnection("TestConnectionString");
        _connection.Open();
    }

    [Fact]
    public void Query_ValidSql_ReturnsResults()
    {
        Assert.Equal(ConnectionState.Open, _connection.State);
    }

    // Dispose = runs after EACH test (like [TearDown])
    public void Dispose()
    {
        _connection?.Close();
        _connection?.Dispose();
    }
}
```

Since a **new instance of the test class is created for every test method**, there's no risk of state leaking between tests — this is a deliberate xUnit design choice (test isolation by default).

### One-Time Setup/Teardown via IClassFixture

```csharp
// This object is created ONCE and shared across all tests in the class
public class DatabaseFixture : IDisposable
{
    public SqlConnection Connection { get; }

    public DatabaseFixture()
    {
        Console.WriteLine("Opening test database connection pool...");
        Connection = new SqlConnection("TestConnectionString");
        Connection.Open();
    }

    public void Dispose()
    {
        Console.WriteLine("Closing test database connection pool.");
        Connection.Dispose();
    }
}

public class DatabaseIntegrationTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _fixture;

    public DatabaseIntegrationTests(DatabaseFixture fixture)
    {
        _fixture = fixture; // injected by xUnit
    }

    [Fact]
    public void Query_UsesSharedConnection_ReturnsResults()
    {
        Assert.Equal(ConnectionState.Open, _fixture.Connection.State);
    }
}
```

### Execution Order

```
DatabaseFixture() constructor          <- once, before any test
  new DatabaseIntegrationTests(fixture) -> Test1 -> (instance discarded)
  new DatabaseIntegrationTests(fixture) -> Test2 -> (instance discarded)
DatabaseFixture.Dispose()               <- once, after all tests
```

### Shared Setup via Base Class

```csharp
public abstract class TestBase
{
    protected Calculator Calculator { get; }

    protected TestBase()
    {
        Calculator = new Calculator();
    }
}

public class CalculatorAdditionTests : TestBase
{
    [Fact]
    public void Add_TwoNumbers_ReturnsSum()
    {
        Assert.Equal(4, Calculator.Add(2, 2));
    }
}
```

---

## 4. Assertions

xUnit uses a single, static `Assert` class (no separate "constraint model" like NUnit) with clear, purpose-specific methods.

### Equality & Comparison

```csharp
Assert.Equal(5, result);
Assert.NotEqual(0, result);
Assert.True(result > 0);
Assert.False(result < 0);
Assert.Null(errorMessage);
Assert.NotNull(user);
Assert.Same(referenceA, referenceB);       // same object reference
Assert.NotSame(referenceA, referenceB);
Assert.Equal(1.0, 1.0001, precision: 2);   // floating point tolerance (decimal places)
Assert.InRange(value, 1, 10);
Assert.NotInRange(value, 100, 200);
```

### Strings

```csharp
Assert.StartsWith("Hello", "Hello World");
Assert.EndsWith("World", "Hello World");
Assert.Contains("lo Wo", "Hello World");
Assert.DoesNotContain("xyz", "Hello World");
Assert.Equal("hello", "HELLO", ignoreCase: true);
Assert.Matches(@"^\d+$", "12345"); // regex
```

### Collections

```csharp
var list = new List<int> { 1, 2, 3, 4, 5 };

Assert.Equal(5, list.Count);
Assert.Contains(3, list);
Assert.DoesNotContain(99, list);
Assert.Empty(new List<int>());
Assert.NotEmpty(list);
Assert.All(list, item => Assert.True(item > 0));
Assert.Single(new List<int> { 42 }); // asserts exactly one element, and returns it
Assert.Equal(new[] { 1, 2, 3, 4, 5 }, list); // sequence equality, order matters
Assert.Equivalent(new[] { 5, 4, 3, 2, 1 }, list); // same elements, order-independent (xUnit 2.5+)

// Collection with per-item inspectors, in order
Assert.Collection(list,
    item => Assert.Equal(1, item),
    item => Assert.Equal(2, item),
    item => Assert.Equal(3, item),
    item => Assert.Equal(4, item),
    item => Assert.Equal(5, item));
```

### Types & Null

```csharp
Assert.IsType<ArgumentNullException>(exception);   // exact type match
Assert.IsAssignableFrom<Exception>(exception);      // base type / interface match
Assert.Null(obj);
Assert.NotNull(obj);
```

### Custom Failure Messages

xUnit's `Assert` methods generally don't take a custom message parameter (a deliberate design choice — xUnit favors descriptive test names and rich default failure output over custom messages). Where supported:

```csharp
Assert.True(result == 5, $"Expected 5 but got {result}");
```

---

## 5. Theory & InlineData (Parameterized Tests)

```csharp
public class MathTests
{
    [Theory]
    [InlineData(2, 3, 5)]
    [InlineData(-1, 1, 0)]
    [InlineData(0, 0, 0)]
    [InlineData(100, 200, 300)]
    public void Add_VariousInputs_ReturnsExpectedSum(int a, int b, int expected)
    {
        var calc = new Calculator();
        Assert.Equal(expected, calc.Add(a, b));
    }

    [Theory]
    [InlineData(10, 2, 5)]
    [InlineData(9, 3, 3)]
    public void Divide_VariousInputs_ReturnsQuotient(int a, int b, int expected)
    {
        var calc = new Calculator();
        Assert.Equal(expected, calc.Divide(a, b));
    }
}
```

Unlike NUnit's `TestCase`, xUnit's `InlineData` values must be **compile-time constants** (no `ExpectedResult` return-value pattern — assert explicitly in the method body instead).

### Naming Individual Theory Cases

xUnit auto-generates readable names from the inline arguments (e.g., `Add_VariousInputs_ReturnsExpectedSum(a: 2, b: 3, expected: 5)`), so there's no separate `TestName` property needed like in NUnit.

---

## 6. MemberData & ClassData

### MemberData — Data from a Static Property or Method

```csharp
public class DiscountTests
{
    public static IEnumerable<object[]> DiscountCases()
    {
        yield return new object[] { 100m, "REGULAR", 100m };
        yield return new object[] { 100m, "VIP", 80m };
        yield return new object[] { 100m, "EMPLOYEE", 50m };
    }

    [Theory]
    [MemberData(nameof(DiscountCases))]
    public void ApplyDiscount_VariousTiers_ReturnsCorrectPrice(decimal price, string tier, decimal expected)
    {
        var pricing = new PricingEngine();
        Assert.Equal(expected, pricing.ApplyDiscount(price, tier));
    }
}
```

### MemberData from a Separate Class

```csharp
public class OrderTestData
{
    public static IEnumerable<object[]> ValidOrders()
    {
        yield return new object[] { new Order { Total = 50m } };
        yield return new object[] { new Order { Total = 500m } };
    }
}

public class OrderValidationTests
{
    [Theory]
    [MemberData(nameof(OrderTestData.ValidOrders), MemberType = typeof(OrderTestData))]
    public void Validate_ValidOrders_ReturnsTrue(Order order)
    {
        Assert.True(OrderValidator.Validate(order));
    }
}
```

### ClassData — Data from a Dedicated Class

```csharp
public class DivisionTestData : IEnumerable<object[]>
{
    public IEnumerator<object[]> GetEnumerator()
    {
        yield return new object[] { 10, 2, 5 };
        yield return new object[] { 9, 3, 3 };
        yield return new object[] { 100, 4, 25 };
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}

public class DivisionTests
{
    [Theory]
    [ClassData(typeof(DivisionTestData))]
    public void Divide_VariousInputs_ReturnsQuotient(int a, int b, int expected)
    {
        Assert.Equal(expected, new Calculator().Divide(a, b));
    }
}
```

### Reading Test Data from a CSV/File

```csharp
public class CsvTestData
{
    public static IEnumerable<object[]> FromFile()
    {
        foreach (var line in File.ReadLines("testdata.csv").Skip(1))
        {
            var parts = line.Split(',');
            yield return new object[]
            {
                int.Parse(parts[0]),
                int.Parse(parts[1]),
                int.Parse(parts[2])
            };
        }
    }
}

public class FileBasedTests
{
    [Theory]
    [MemberData(nameof(CsvTestData.FromFile), MemberType = typeof(CsvTestData))]
    public void Add_FromCsvFile_ReturnsExpected(int a, int b, int expected)
    {
        Assert.Equal(expected, new Calculator().Add(a, b));
    }
}
```

---

## 7. Shared Context: Class Fixtures & Collection Fixtures

### IClassFixture\<T> — Shared Within One Test Class

(See Section 3 for the full example.) Use when setup is expensive but safe to share **within a single class**.

### ICollectionFixture\<T> — Shared Across Multiple Test Classes

```csharp
// The fixture itself
public class SharedDatabaseFixture : IDisposable
{
    public SqlConnection Connection { get; }

    public SharedDatabaseFixture()
    {
        Connection = new SqlConnection("TestConnectionString");
        Connection.Open();
        Console.WriteLine("Shared database connection opened once for the whole collection.");
    }

    public void Dispose() => Connection.Dispose();
}

// Define a "collection" that groups test classes together
[CollectionDefinition("Database collection")]
public class DatabaseCollection : ICollectionFixture<SharedDatabaseFixture>
{
    // This class has no code; it's just a marker combining the fixture
    // with the collection name via attributes.
}

// Multiple test classes can now share the SAME fixture instance
[Collection("Database collection")]
public class UserRepositoryTests
{
    private readonly SharedDatabaseFixture _fixture;
    public UserRepositoryTests(SharedDatabaseFixture fixture) => _fixture = fixture;

    [Fact]
    public void GetUser_ExistingId_ReturnsUser()
    {
        Assert.Equal(ConnectionState.Open, _fixture.Connection.State);
    }
}

[Collection("Database collection")]
public class OrderRepositoryTests
{
    private readonly SharedDatabaseFixture _fixture;
    public OrderRepositoryTests(SharedDatabaseFixture fixture) => _fixture = fixture;

    [Fact]
    public void GetOrder_ExistingId_ReturnsOrder()
    {
        Assert.Equal(ConnectionState.Open, _fixture.Connection.State);
    }
}
```

**Important side effect:** test classes in the same `[Collection]` never run in parallel with each other (they share state), while classes in different collections can run in parallel.

### IAsyncLifetime — Async Setup/Teardown

For fixtures or test classes needing **asynchronous** initialization/cleanup (e.g., spinning up a Testcontainers database):

```csharp
public class AsyncDatabaseFixture : IAsyncLifetime
{
    public SqlConnection Connection { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        Connection = new SqlConnection("TestConnectionString");
        await Connection.OpenAsync();
    }

    public async Task DisposeAsync()
    {
        await Connection.DisposeAsync();
    }
}

public class AsyncIntegrationTests : IClassFixture<AsyncDatabaseFixture>
{
    private readonly AsyncDatabaseFixture _fixture;
    public AsyncIntegrationTests(AsyncDatabaseFixture fixture) => _fixture = fixture;

    [Fact]
    public void Connection_IsOpen()
    {
        Assert.Equal(ConnectionState.Open, _fixture.Connection.State);
    }
}
```

---

## 8. Exception Testing

```csharp
[Fact]
public void Withdraw_AmountExceedsBalance_ThrowsException()
{
    var account = new BankAccount(100m);

    var ex = Assert.Throws<InvalidOperationException>(() => account.Withdraw(200m));
    Assert.Equal("Insufficient funds", ex.Message);
}

[Fact]
public async Task FetchDataAsync_InvalidUrl_ThrowsHttpRequestException()
{
    var client = new ApiClient();
    await Assert.ThrowsAsync<HttpRequestException>(() => client.FetchDataAsync("invalid-url"));
}

[Fact]
public void Divide_ByNonZero_DoesNotThrow()
{
    var exception = Record.Exception(() => new Calculator().Divide(10, 1));
    Assert.Null(exception); // xUnit has no Assert.DoesNotThrow — use Record.Exception instead
}

[Fact]
public void Withdraw_NegativeAmount_ThrowsArgumentExceptionOrSubclass()
{
    var account = new BankAccount(100m);
    var ex = Assert.ThrowsAny<ArgumentException>(() => account.Withdraw(-10m));
    Assert.Contains("negative", ex.Message);
}
```

---

## 9. Async Test Support

xUnit natively supports `async Task` `[Fact]`/`[Theory]` methods.

```csharp
public class AsyncServiceTests
{
    [Fact]
    public async Task GetUserAsync_ValidId_ReturnsUser()
    {
        var service = new UserService();
        User user = await service.GetUserAsync(1);

        Assert.NotNull(user);
        Assert.Equal(1, user.Id);
    }

    [Fact]
    public async Task GetUserAsync_InvalidId_ReturnsNull()
    {
        var service = new UserService();
        User? user = await service.GetUserAsync(-1);

        Assert.Null(user);
    }

    [Theory]
    [InlineData(1)]
    [InlineData(2)]
    [InlineData(3)]
    public async Task GetUserAsync_MultipleValidIds_ReturnsMatchingUser(int id)
    {
        var service = new UserService();
        User? user = await service.GetUserAsync(id);
        Assert.Equal(id, user!.Id);
    }
}
```

### Test Timeouts

```csharp
[Fact(Timeout = 1000)] // fails if test takes longer than 1000ms
public async Task FastOperation_CompletesQuickly()
{
    await Task.Delay(200);
}
```

---

## 10. Mocking with xUnit (Moq / NSubstitute)

Like NUnit, xUnit has no built-in mocking framework — pair it with **Moq** or **NSubstitute**.

### Using Moq

```csharp
dotnet add package Moq
```

```csharp
using Moq;

public interface IEmailService
{
    Task SendAsync(string to, string subject, string body);
}

public class NotificationServiceTests
{
    private readonly Mock<IEmailService> _emailServiceMock;
    private readonly NotificationService _sut;

    public NotificationServiceTests()
    {
        _emailServiceMock = new Mock<IEmailService>();
        _sut = new NotificationService(_emailServiceMock.Object);
    }

    [Fact]
    public async Task NotifyUser_ValidUser_SendsEmail()
    {
        _emailServiceMock
            .Setup(s => s.SendAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
            .Returns(Task.CompletedTask);

        await _sut.NotifyUser("alice@example.com", "Welcome!");

        _emailServiceMock.Verify(
            s => s.SendAsync("alice@example.com", "Welcome!", It.IsAny<string>()),
            Times.Once);
    }

    [Fact]
    public async Task NotifyUser_EmailServiceThrows_PropagatesException()
    {
        _emailServiceMock
            .Setup(s => s.SendAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
            .ThrowsAsync(new InvalidOperationException("SMTP down"));

        await Assert.ThrowsAsync<InvalidOperationException>(
            () => _sut.NotifyUser("bob@example.com", "Hi"));
    }
}
```

### Using NSubstitute

```csharp
dotnet add package NSubstitute
```

```csharp
using NSubstitute;

public class NotificationServiceNSubstituteTests
{
    [Fact]
    public async Task NotifyUser_ValidUser_SendsEmail()
    {
        var emailService = Substitute.For<IEmailService>();
        var sut = new NotificationService(emailService);

        await sut.NotifyUser("alice@example.com", "Welcome!");

        await emailService.Received(1).SendAsync("alice@example.com", "Welcome!", Arg.Any<string>());
    }
}
```

---

## 11. Test Output & Diagnostics

xUnit uses constructor-injected `ITestOutputHelper` instead of a static context object.

```csharp
public class DiagnosticTests
{
    private readonly ITestOutputHelper _output;

    public DiagnosticTests(ITestOutputHelper output)
    {
        _output = output; // injected automatically by xUnit
    }

    [Fact]
    public void ComplexCalculation_LogsIntermediateValues()
    {
        _output.WriteLine("Starting calculation...");
        int result = 2 + 2;
        _output.WriteLine($"Result: {result}");

        Assert.Equal(4, result);
    }
}
```

This output shows up in `dotnet test` verbose output and IDE test explorers, scoped correctly per test (unlike `Console.WriteLine`, which can interleave confusingly under parallel execution).

---

## 12. Test Collections & Parallelism

By default, **xUnit runs test classes in parallel** (but tests within the same class run sequentially), which is the opposite default from NUnit.

### Disabling Parallelism

```csharp
// In AssemblyInfo.cs or any file in the test project
[assembly: CollectionBehavior(DisableTestParallelization = true)]
```

### Controlling Max Parallel Threads

```csharp
[assembly: CollectionBehavior(MaxParallelThreads = 4)]
```

### Grouping Tests to Run Sequentially

As shown in Section 7, tests sharing a `[Collection("name")]` never run in parallel with each other — useful for tests that share a real database or other stateful resource.

```csharp
[CollectionDefinition("Sequential", DisableParallelization = true)]
public class SequentialCollection { }

[Collection("Sequential")]
public class FileSystemTests
{
    [Fact]
    public void WriteFile_ThenReadFile_ReturnsSameContent() { }
}
```

---

## 13. Skipping & Conditional Tests

```csharp
[Fact(Skip = "Not implemented yet — see JIRA-1234")]
public void FeatureNotYetImplemented_Test() { }

[Theory(Skip = "Flaky in CI — investigating")]
[InlineData(1)]
public void FlakyParameterizedTest(int value) { }

// Conditional skip at runtime (no built-in attribute — common workaround):
[Fact]
public void ConditionallySkippedAtRuntime()
{
    if (Environment.GetEnvironmentVariable("RUN_SLOW_TESTS") != "true")
    {
        return; // xUnit has no Assert.Ignore — simplest approach is an early return
                // or use a custom "SkippableFact" from the Xunit.SkippableFact package
    }

    // test body
}
```

For richer runtime-conditional skipping, many teams add the community package `Xunit.SkippableFact`:

```csharp
dotnet add package Xunit.SkippableFact
```

```csharp
[SkippableFact]
public void RequiresDockerDaemon_Test()
{
    Skip.IfNot(DockerHelper.IsDockerRunning(), "Docker is not available in this environment");
    // test body
}
```

---

## 14. Custom Attributes & Extensibility

### Custom Fact Attribute (e.g., category-like grouping via Traits)

xUnit uses **Traits** instead of NUnit's `[Category]`:

```csharp
public class PaymentGatewayTests
{
    [Fact]
    [Trait("Category", "Integration")]
    [Trait("Speed", "Slow")]
    public void ProcessPayment_ValidCard_Succeeds() { }

    [Fact]
    [Trait("Category", "Unit")]
    [Trait("Speed", "Fast")]
    public void ValidateCardNumber_Luhn_ReturnsTrue() { }
}
```

Run by trait:

```bash
dotnet test --filter "Category=Unit"
dotnet test --filter "Speed!=Slow"
```

### Custom Trait Attribute (Reusable Category Attribute)

```csharp
public class CategoryAttribute : Attribute, ITraitAttribute
{
    // Implemented via Xunit.Sdk.TraitDiscoverer for full custom behavior;
    // simpler teams typically just wrap [Trait("Category", "X")] in their own attribute:
}

[AttributeUsage(AttributeTargets.Method)]
public class IntegrationTestAttribute : Attribute
{
    // Combine with [Trait] directly in most real projects:
}

// In practice, most teams just do:
public class MyIntegrationTests
{
    [Fact]
    [Trait("Category", "Integration")]
    public void Example_IntegrationTest() { }
}
```

### Custom Test Framework Extensions (Advanced)

xUnit's extensibility model (`ITestFramework`, `IXunitTestCase`, `BeforeAfterTestAttribute`) allows deep customization:

```csharp
public class RetryAttribute : Xunit.Sdk.BeforeAfterTestAttribute
{
    public override void Before(MethodInfo methodUnderTest)
    {
        Console.WriteLine($"Before {methodUnderTest.Name}");
    }

    public override void After(MethodInfo methodUnderTest)
    {
        Console.WriteLine($"After {methodUnderTest.Name}");
    }
}

[Fact]
[Retry]
public void SomeTest() { }
```

For true automatic retries, the community package `Xunit.Retry` or manual retry loops are common, since xUnit deliberately doesn't include one out of the box (to discourage masking flaky tests).

---

## 15. Running Tests (CLI & CI)

```bash
# Run all tests
dotnet test

# Run a specific class
dotnet test --filter "FullyQualifiedName~CalculatorTests"

# Run a specific test
dotnet test --filter "Name=Add_TwoPositiveNumbers_ReturnsSum"

# Run by trait
dotnet test --filter "Category=Integration"

# Generate a test results file (TRX format for CI)
dotnet test --logger "trx;LogFileName=results.trx"

# Collect code coverage (with coverlet, built into the xunit template)
dotnet test --collect:"XPlat Code Coverage"
```

### GitHub Actions Example

```yaml
name: Run Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - run: dotnet restore
      - run: dotnet test --logger "trx" --results-directory TestResults
```

---

## 16. xUnit vs NUnit: Key Differences

| Aspect | xUnit | NUnit |
|---|---|---|
| Test class marker | None needed (any public class) | `[TestFixture]` |
| Single test | `[Fact]` | `[Test]` |
| Parameterized test | `[Theory]` + `[InlineData]`/`[MemberData]`/`[ClassData]` | `[TestCase]` / `[TestCaseSource]` |
| Per-test setup | Constructor | `[SetUp]` |
| Per-test teardown | `IDisposable.Dispose()` | `[TearDown]` |
| One-time setup (class) | `IClassFixture<T>` constructor | `[OneTimeSetUp]` |
| One-time setup (multiple classes) | `ICollectionFixture<T>` + `[Collection]` | `[OneTimeSetUp]` in a shared base, or static state |
| Async setup/teardown | `IAsyncLifetime` | `async` `[SetUp]`/`[TearDown]` supported directly |
| Test instance lifetime | New instance per test (isolation by default) | Usually one instance per fixture (shared) |
| Default parallelism | Classes run in parallel by default | Sequential by default, opt-in via `[Parallelizable]` |
| Skip a test | `[Fact(Skip = "reason")]` | `[Ignore("reason")]` |
| Grouping/filtering | `[Trait("Key", "Value")]` | `[Category("Name")]` |
| Assertion style | Single static `Assert` class, purpose-specific methods | Classic (`Assert.AreEqual`) + fluent constraint model (`Assert.That`) |
| Assert no-exception | `Record.Exception(...)` then assert null | `Assert.DoesNotThrow(...)` |
| Console-style output | `ITestOutputHelper` (constructor-injected) | `TestContext.WriteLine` (static) |
| Retry support | Not built-in (community packages) | Built-in `[Retry(n)]` |
| Combinatorial data | Not built-in (manual `MemberData` combos) | Built-in `[Values]`, `[Combinatorial]`, `[Pairwise]` |

**When teams pick xUnit:** they want strict test isolation by default, prefer idiomatic C# (constructors/`IDisposable`) over custom attributes, and often are building ASP.NET Core apps (xUnit is the default template there).

**When teams pick NUnit:** they want a richer built-in feature set (retries, combinatorial testing, a fluent constraint API) without extra packages, or are migrating an existing NUnit codebase.

---

## 17. Best Practices

- Rely on constructor + `IDisposable` for setup/teardown rather than fighting the framework with static workarounds.
- Use `IClassFixture<T>`/`ICollectionFixture<T>` for genuinely expensive shared resources (e.g., a test container, in-memory server) — not for simple object creation, which is cheap per-test.
- Prefer `[Theory]` + `MemberData`/`ClassData` over many near-duplicate `[Fact]`s.
- Use `[Trait]` consistently (e.g., `Category`, `Speed`) so CI pipelines can selectively run fast unit tests vs slow integration tests.
- Inject `ITestOutputHelper` instead of `Console.WriteLine` so diagnostic output stays correctly attributed under parallel execution.
- Keep test classes small and focused; since a new instance is created per test, constructors should stay lightweight.
- Group tests that share mutable external state (files, databases, ports) into the same `[Collection]` to avoid race conditions from xUnit's default parallelism.
- Avoid built-in retry hacks to hide flaky tests — investigate and fix flakiness instead (a deliberate xUnit philosophy).
- Use `Assert.Throws<T>`/`Assert.ThrowsAsync<T>` for exact exception types, and `Assert.ThrowsAny<T>` when subclasses are acceptable.

---

## 18. Quick Reference Tables

### Attributes

| Attribute | Purpose |
|---|---|
| `[Fact]` | Marks a non-parameterized test method |
| `[Theory]` | Marks a parameterized test method |
| `[InlineData]` | Inline parameterized data |
| `[MemberData]` | Data from a static property/method/field |
| `[ClassData]` | Data from a class implementing `IEnumerable<object[]>` |
| `[Trait("Key","Value")]` | Categorize/group tests for filtering |
| `[Fact(Skip = "reason")]` | Skip a test |
| `[Fact(Timeout = ms)]` | Fail if test exceeds time limit |
| `[Collection("name")]` | Group test classes to share a fixture / avoid parallel execution |
| `[CollectionDefinition("name")]` | Define a named collection + its fixture type |

### Assertion Cheat Sheet

| Goal | xUnit |
|---|---|
| Equality | `Assert.Equal(expected, actual)` |
| Boolean | `Assert.True(condition)` |
| Null | `Assert.Null(x)` |
| Exception (exact type) | `Assert.Throws<T>(() => ...)` |
| Exception (base type ok) | `Assert.ThrowsAny<T>(() => ...)` |
| No exception | `Record.Exception(() => ...)` then `Assert.Null(ex)` |
| Collection contains | `Assert.Contains(item, list)` |
| Collection count | `Assert.Equal(n, list.Count)` |
| Collection sequence | `Assert.Equal(expectedArray, actualArray)` |
| Collection unordered | `Assert.Equivalent(expected, actual)` |
| String contains | `Assert.Contains("abc", str)` |
| Type check (exact) | `Assert.IsType<T>(obj)` |
| Type check (assignable) | `Assert.IsAssignableFrom<T>(obj)` |
| Range | `Assert.InRange(x, 1, 10)` |

### Lifecycle Mapping (NUnit → xUnit mental model)

| NUnit | xUnit Equivalent |
|---|---|
| `[SetUp]` | Constructor |
| `[TearDown]` | `Dispose()` (implement `IDisposable`) |
| `[OneTimeSetUp]` | `IClassFixture<T>` constructor |
| `[OneTimeTearDown]` | `IClassFixture<T>.Dispose()` |
| `[Category("X")]` | `[Trait("Category", "X")]` |
| `[Ignore("reason")]` | `[Fact(Skip = "reason")]` |

---

*Practice idea: write a full xUnit test suite for a `ShoppingCart` class — using `[Theory]`/`MemberData` for discount rules, an `IClassFixture` for a shared in-memory catalog, `ITestOutputHelper` for diagnostics, and Moq for an async checkout/payment gateway dependency. Compare the resulting suite structurally against the equivalent NUnit suite to internalize the differences.*
