# The Complete NUnit Testing Guide (C#)

An extensive, example-driven reference for **NUnit**, one of the most widely used unit testing frameworks in the .NET ecosystem.

---

## Table of Contents

1. [Introduction & Setup](#1-introduction--setup)
2. [Test Structure Basics](#2-test-structure-basics)
3. [Setup & Teardown Attributes](#3-setup--teardown-attributes)
4. [Assertions](#4-assertions)
5. [The Constraint Model (Assert.That)](#5-the-constraint-model-assertthat)
6. [Parameterized Tests](#6-parameterized-tests)
7. [Test Organization & Categorization](#7-test-organization--categorization)
8. [Exception Testing](#8-exception-testing)
9. [Async Test Support](#9-async-test-support)
10. [Mocking with NUnit (Moq / NSubstitute)](#10-mocking-with-nunit-moq--nsubstitute)
11. [Data-Driven Testing In Depth](#11-data-driven-testing-in-depth)
12. [Test Context & Metadata](#12-test-context--metadata)
13. [Parallel Test Execution](#13-parallel-test-execution)
14. [Custom Constraints & Extensibility](#14-custom-constraints--extensibility)
15. [Ignoring, Explicit & Conditional Tests](#15-ignoring-explicit--conditional-tests)
16. [Running Tests (CLI & CI)](#16-running-tests-cli--ci)
17. [Best Practices](#17-best-practices)
18. [Quick Reference Tables](#18-quick-reference-tables)

---

## 1. Introduction & Setup

**NUnit** is a mature, open-source unit testing framework (originally ported from JUnit) for .NET. It's attribute-based, feature-rich, and integrates with Visual Studio, `dotnet test`, and most CI systems.

### Installing NUnit

```bash
dotnet new classlib -n MyApp.Tests
cd MyApp.Tests
dotnet add package NUnit
dotnet add package NUnit3TestAdapter
dotnet add package Microsoft.NET.Test.Sdk
```

### Minimal .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="NUnit" Version="4.1.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.10.0" />
  </ItemGroup>
</Project>
```

### Your First Test

```csharp
using NUnit.Framework;

namespace MyApp.Tests
{
    [TestFixture]
    public class CalculatorTests
    {
        [Test]
        public void Add_TwoPositiveNumbers_ReturnsSum()
        {
            // Arrange
            var calculator = new Calculator();

            // Act
            int result = calculator.Add(2, 3);

            // Assert
            Assert.That(result, Is.EqualTo(5));
        }
    }
}
```

Run with:

```bash
dotnet test
```

---

## 2. Test Structure Basics

### Core Attributes

| Attribute | Purpose |
|---|---|
| `[TestFixture]` | Marks a class as containing tests |
| `[Test]` | Marks a method as a single test |
| `[TestCase(...)]` | Parameterized test with inline data |
| `[TestCaseSource(...)]` | Parameterized test with external data source |
| `[Theory]` | Data-driven test combined with `[Datapoint]` values |

```csharp
[TestFixture]
public class StringUtilsTests
{
    [Test]
    public void Reverse_SimpleString_ReturnsReversedString()
    {
        string result = StringUtils.Reverse("hello");
        Assert.That(result, Is.EqualTo("olleh"));
    }

    [Test]
    public void Reverse_EmptyString_ReturnsEmptyString()
    {
        Assert.That(StringUtils.Reverse(""), Is.EqualTo(""));
    }
}
```

### Naming Conventions

A common and readable convention: `MethodName_Scenario_ExpectedBehavior`

```csharp
[Test]
public void Withdraw_AmountExceedsBalance_ThrowsInsufficientFundsException() { ... }

[Test]
public void Withdraw_ValidAmount_DecreasesBalance() { ... }
```

---

## 3. Setup & Teardown Attributes

NUnit provides lifecycle hooks that run before/after each test or once per fixture.

```csharp
[TestFixture]
public class DatabaseTests
{
    private SqlConnection _connection;

    [OneTimeSetUp]   // runs ONCE before any test in this fixture
    public void FixtureSetup()
    {
        Console.WriteLine("Opening test database connection pool...");
    }

    [SetUp]          // runs before EACH test
    public void Setup()
    {
        _connection = new SqlConnection("TestConnectionString");
        _connection.Open();
    }

    [Test]
    public void Query_ValidSql_ReturnsResults()
    {
        // uses _connection, freshly created for this test
        Assert.That(_connection.State, Is.EqualTo(ConnectionState.Open));
    }

    [TearDown]       // runs after EACH test
    public void Teardown()
    {
        _connection?.Close();
        _connection?.Dispose();
    }

    [OneTimeTearDown] // runs ONCE after all tests in this fixture
    public void FixtureTeardown()
    {
        Console.WriteLine("Closing test database connection pool.");
    }
}
```

### Execution Order

```
OneTimeSetUp
  SetUp -> Test1 -> TearDown
  SetUp -> Test2 -> TearDown
  SetUp -> Test3 -> TearDown
OneTimeTearDown
```

### Setup/Teardown Inheritance

Base class setup methods run automatically for derived fixtures:

```csharp
public abstract class TestBase
{
    protected Calculator Calculator;

    [SetUp]
    public void BaseSetup()
    {
        Calculator = new Calculator();
    }
}

[TestFixture]
public class CalculatorAdditionTests : TestBase
{
    [Test]
    public void Add_TwoNumbers_ReturnsSum()
    {
        Assert.That(Calculator.Add(2, 2), Is.EqualTo(4));
    }
}
```

---

## 4. Assertions

NUnit supports two assertion styles: the **classic model** (`Assert.AreEqual`, etc.) and the **constraint model** (`Assert.That(...)`). The constraint model is now recommended, but classic-style is still widely seen in existing codebases.

### Classic Assertion Style

```csharp
Assert.AreEqual(5, result);
Assert.AreNotEqual(0, result);
Assert.IsTrue(result > 0);
Assert.IsFalse(result < 0);
Assert.IsNull(errorMessage);
Assert.IsNotNull(user);
Assert.AreSame(referenceA, referenceB); // same object reference
Assert.Greater(result, 0);
Assert.Less(result, 100);
Assert.That(collection, Has.Count.EqualTo(3));
```

### Multiple Assertions in One Test

```csharp
[Test]
public void CreateUser_ValidInput_SetsAllFields()
{
    var user = new User("Alice", 30);

    Assert.Multiple(() =>
    {
        Assert.That(user.Name, Is.EqualTo("Alice"));
        Assert.That(user.Age, Is.EqualTo(30));
        Assert.That(user.IsActive, Is.True);
    });
    // All 3 assertions run and report failures, even if the first one fails
}
```

---

## 5. The Constraint Model (Assert.That)

This is the modern, fluent, and most expressive way to write assertions in NUnit.

### Equality & Comparison

```csharp
Assert.That(actual, Is.EqualTo(expected));
Assert.That(actual, Is.Not.EqualTo(unexpected));
Assert.That(value, Is.GreaterThan(10));
Assert.That(value, Is.LessThanOrEqualTo(100));
Assert.That(value, Is.InRange(1, 10));
Assert.That(1.0001, Is.EqualTo(1.0).Within(0.01)); // floating point tolerance
```

### Strings

```csharp
Assert.That("Hello World", Does.StartWith("Hello"));
Assert.That("Hello World", Does.EndWith("World"));
Assert.That("Hello World", Does.Contain("lo Wo"));
Assert.That("HELLO", Is.EqualTo("hello").IgnoreCase);
Assert.That("12345", Does.Match(@"^\d+$")); // regex
```

### Collections

```csharp
var list = new List<int> { 1, 2, 3, 4, 5 };

Assert.That(list, Has.Count.EqualTo(5));
Assert.That(list, Has.Member(3));
Assert.That(list, Does.Contain(3));
Assert.That(list, Is.Ordered);
Assert.That(list, Is.Ordered.Descending); // fails for ascending data
Assert.That(list, Is.Unique);
Assert.That(list, Is.EquivalentTo(new[] { 5, 4, 3, 2, 1 })); // same items, any order
Assert.That(list, Is.SubsetOf(new[] { 1, 2, 3, 4, 5, 6 }));
Assert.That(list, Is.All.GreaterThan(0));
Assert.That(list, Has.Some.GreaterThan(4));
Assert.That(list, Has.None.LessThan(0));
Assert.That(list, Has.Exactly(1).EqualTo(3));
```

### Types & Null

```csharp
Assert.That(exception, Is.InstanceOf<ArgumentNullException>());
Assert.That(result, Is.TypeOf<int>());
Assert.That(obj, Is.Null);
Assert.That(obj, Is.Not.Null);
Assert.That(list, Is.Empty);
Assert.That(list, Is.Not.Empty);
```

### Combining Constraints

```csharp
Assert.That(value, Is.GreaterThan(0).And.LessThan(100));
Assert.That(name, Is.Not.Null.And.Not.Empty);
Assert.That(status, Is.EqualTo("Active").Or.EqualTo("Pending"));
```

### Custom Failure Messages

```csharp
Assert.That(result, Is.EqualTo(5), $"Expected 5 but got {result} for input (2,3)");
```

---

## 6. Parameterized Tests

### TestCase — Inline Data

```csharp
[TestFixture]
public class MathTests
{
    [TestCase(2, 3, 5)]
    [TestCase(-1, 1, 0)]
    [TestCase(0, 0, 0)]
    [TestCase(100, 200, 300)]
    public void Add_VariousInputs_ReturnsExpectedSum(int a, int b, int expected)
    {
        var calc = new Calculator();
        Assert.That(calc.Add(a, b), Is.EqualTo(expected));
    }

    [TestCase(10, 2, ExpectedResult = 5)]
    [TestCase(9, 3, ExpectedResult = 3)]
    public int Divide_VariousInputs_ReturnsQuotient(int a, int b)
    {
        var calc = new Calculator();
        return calc.Divide(a, b); // NUnit compares the return value to ExpectedResult
    }

    [TestCase(5, TestName = "Square_Of_5_Is_25")]
    [TestCase(-3, TestName = "Square_Of_Negative3_Is_9")]
    public void Square_GivenNumber_ReturnsSquare(int input)
    {
        Assert.That(input * input, Is.EqualTo(Math.Pow(input, 2)));
    }
}
```

### TestCaseSource — External Data

```csharp
[TestFixture]
public class DiscountTests
{
    private static IEnumerable<TestCaseData> DiscountCases()
    {
        yield return new TestCaseData(100m, "REGULAR").Returns(100m);
        yield return new TestCaseData(100m, "VIP").Returns(80m);
        yield return new TestCaseData(100m, "EMPLOYEE").Returns(50m);
    }

    [TestCaseSource(nameof(DiscountCases))]
    public decimal ApplyDiscount_VariousTiers_ReturnsCorrectPrice(decimal price, string tier)
    {
        var pricing = new PricingEngine();
        return pricing.ApplyDiscount(price, tier);
    }
}
```

### TestCaseSource from a Separate Class

```csharp
public class OrderTestData
{
    public static IEnumerable<TestCaseData> ValidOrders
    {
        get
        {
            yield return new TestCaseData(new Order { Total = 50m }).SetName("SmallOrder");
            yield return new TestCaseData(new Order { Total = 500m }).SetName("LargeOrder");
        }
    }
}

[TestFixture]
public class OrderValidationTests
{
    [TestCaseSource(typeof(OrderTestData), nameof(OrderTestData.ValidOrders))]
    public void Validate_ValidOrders_ReturnsTrue(Order order)
    {
        Assert.That(OrderValidator.Validate(order), Is.True);
    }
}
```

### Values & Combinatorial Testing

```csharp
[TestFixture]
public class CombinatorialTests
{
    [Test, Combinatorial]
    public void Multiply_AllCombinations_ProducesCorrectResult(
        [Values(1, 2, 3)] int a,
        [Values(10, 20)] int b)
    {
        // Runs 3 x 2 = 6 combinations
        Assert.That(a * b, Is.EqualTo(a * b)); // placeholder logic
    }

    [Test, Pairwise] // reduces combinations using pairwise algorithm
    public void Configure_PairwiseCombinations_Valid(
        [Values("A", "B", "C")] string mode,
        [Values(1, 2, 3)] int level,
        [Values(true, false)] bool enabled)
    {
        // fewer test executions than full combinatorial, still good coverage
    }
}
```

### Range Values

```csharp
[Test]
public void IsPositive_RangeOfValues_ReturnsExpected(
    [Range(1, 10, 2)] int value) // 1, 3, 5, 7, 9
{
    Assert.That(value > 0, Is.True);
}
```

### Random Values

```csharp
[Test]
public void ProcessAmount_RandomValues_NeverThrows(
    [Random(1, 1000, 5)] int amount) // 5 random ints between 1 and 1000
{
    Assert.DoesNotThrow(() => OrderProcessor.Process(amount));
}
```

---

## 7. Test Organization & Categorization

```csharp
[TestFixture]
[Category("Integration")]
public class PaymentGatewayTests
{
    [Test]
    [Category("Slow")]
    public void ProcessPayment_ValidCard_Succeeds() { }

    [Test]
    [Category("Fast")]
    public void ValidateCardNumber_Luhn_ReturnsTrue() { }
}
```

Run only a category:

```bash
dotnet test --filter "Category=Fast"
dotnet test --filter "Category!=Slow"
```

### Fixture-Level Parameterization

```csharp
[TestFixture(1, 2, 3)]
[TestFixture(10, 20, 30)]
public class CalculatorFixtureTests
{
    private readonly int _a, _b, _expected;

    public CalculatorFixtureTests(int a, int b, int expected)
    {
        _a = a; _b = b; _expected = expected;
    }

    [Test]
    public void Add_ConstructorProvidedValues_MatchesExpected()
    {
        Assert.That(new Calculator().Add(_a, _b), Is.EqualTo(_expected));
    }
}
```

### Generic Test Fixtures

```csharp
[TestFixture(typeof(List<int>))]
[TestFixture(typeof(LinkedList<int>))]
public class CollectionContractTests<TCollection> where TCollection : ICollection<int>, new()
{
    [Test]
    public void Add_SingleItem_IncreasesCount()
    {
        var collection = new TCollection();
        collection.Add(1);
        Assert.That(collection.Count, Is.EqualTo(1));
    }
}
```

---

## 8. Exception Testing

```csharp
[Test]
public void Withdraw_AmountExceedsBalance_ThrowsException()
{
    var account = new BankAccount(100m);

    var ex = Assert.Throws<InvalidOperationException>(() => account.Withdraw(200m));
    Assert.That(ex.Message, Is.EqualTo("Insufficient funds"));
}

[Test]
public async Task FetchDataAsync_InvalidUrl_ThrowsHttpRequestException()
{
    var client = new ApiClient();
    Assert.ThrowsAsync<HttpRequestException>(async () => await client.FetchDataAsync("invalid-url"));
}

[Test]
public void Divide_ByZero_DoesNotThrow()
{
    Assert.DoesNotThrow(() => new Calculator().Divide(10, 1));
}

// Constraint-model equivalent
[Test]
public void Withdraw_NegativeAmount_ThrowsArgumentException()
{
    var account = new BankAccount(100m);
    Assert.That(() => account.Withdraw(-10m), Throws.ArgumentException);
    Assert.That(() => account.Withdraw(-10m),
        Throws.TypeOf<ArgumentException>().With.Message.Contains("negative"));
}
```

---

## 9. Async Test Support

NUnit natively supports `async Task` test methods.

```csharp
[TestFixture]
public class AsyncServiceTests
{
    [Test]
    public async Task GetUserAsync_ValidId_ReturnsUser()
    {
        var service = new UserService();
        User user = await service.GetUserAsync(1);

        Assert.That(user, Is.Not.Null);
        Assert.That(user.Id, Is.EqualTo(1));
    }

    [Test]
    public async Task GetUserAsync_InvalidId_ReturnsNull()
    {
        var service = new UserService();
        User user = await service.GetUserAsync(-1);

        Assert.That(user, Is.Null);
    }

    [Test]
    public void ProcessAsync_Timeout_ThrowsTimeoutException()
    {
        Assert.ThrowsAsync<TimeoutException>(async () =>
        {
            await Task.Delay(100);
            throw new TimeoutException();
        });
    }
}
```

### Test Timeouts

```csharp
[Test, Timeout(1000)] // fails if test takes longer than 1000ms
public async Task FastOperation_CompletesQuickly()
{
    await Task.Delay(200);
}
```

---

## 10. Mocking with NUnit (Moq / NSubstitute)

NUnit doesn't include a mocking library itself — it's typically paired with **Moq** or **NSubstitute**.

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

[TestFixture]
public class NotificationServiceTests
{
    private Mock<IEmailService> _emailServiceMock;
    private NotificationService _sut; // "system under test"

    [SetUp]
    public void Setup()
    {
        _emailServiceMock = new Mock<IEmailService>();
        _sut = new NotificationService(_emailServiceMock.Object);
    }

    [Test]
    public async Task NotifyUser_ValidUser_SendsEmail()
    {
        // Arrange
        _emailServiceMock
            .Setup(s => s.SendAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
            .Returns(Task.CompletedTask);

        // Act
        await _sut.NotifyUser("alice@example.com", "Welcome!");

        // Assert
        _emailServiceMock.Verify(
            s => s.SendAsync("alice@example.com", "Welcome!", It.IsAny<string>()),
            Times.Once);
    }

    [Test]
    public void NotifyUser_EmailServiceThrows_PropagatesException()
    {
        _emailServiceMock
            .Setup(s => s.SendAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
            .ThrowsAsync(new InvalidOperationException("SMTP down"));

        Assert.ThrowsAsync<InvalidOperationException>(
            () => _sut.NotifyUser("bob@example.com", "Hi"));
    }
}
```

### Using NSubstitute (alternative, simpler syntax)

```csharp
dotnet add package NSubstitute
```

```csharp
using NSubstitute;

[Test]
public async Task NotifyUser_ValidUser_SendsEmail_NSubstitute()
{
    var emailService = Substitute.For<IEmailService>();
    var sut = new NotificationService(emailService);

    await sut.NotifyUser("alice@example.com", "Welcome!");

    await emailService.Received(1).SendAsync("alice@example.com", "Welcome!", Arg.Any<string>());
}
```

---

## 11. Data-Driven Testing In Depth

### Theory + Datapoints (property-based-style testing)

```csharp
[TestFixture]
public class MathTheoryTests
{
    [Datapoint] public double D0 = 0.0;
    [Datapoint] public double D1 = 1.0;
    [Datapoint] public double D2 = -1.0;
    [Datapoint] public double D3 = 100.0;

    [Theory]
    public void AbsoluteValue_IsAlwaysNonNegative(double value)
    {
        Assume.That(value != double.NaN); // filter out unwanted data
        Assert.That(Math.Abs(value), Is.GreaterThanOrEqualTo(0));
    }
}
```

### Reading Test Data from a CSV/File (Custom Source)

```csharp
public class CsvTestData
{
    public static IEnumerable<TestCaseData> FromFile()
    {
        foreach (var line in File.ReadLines("testdata.csv").Skip(1))
        {
            var parts = line.Split(',');
            yield return new TestCaseData(int.Parse(parts[0]), int.Parse(parts[1]))
                .Returns(int.Parse(parts[2]));
        }
    }
}

[TestFixture]
public class FileBasedTests
{
    [TestCaseSource(typeof(CsvTestData), nameof(CsvTestData.FromFile))]
    public int Add_FromCsvFile_ReturnsExpected(int a, int b) => new Calculator().Add(a, b);
}
```

---

## 12. Test Context & Metadata

```csharp
[Test]
public void LogTestMetadata_PrintsTestInfo()
{
    Console.WriteLine($"Running test: {TestContext.CurrentContext.Test.Name}");
    Console.WriteLine($"Test ID: {TestContext.CurrentContext.Test.ID}");
    Console.WriteLine($"Work directory: {TestContext.CurrentContext.WorkDirectory}");

    TestContext.WriteLine("This appears in the test output/log.");
    TestContext.Progress.WriteLine("This appears in progress output during execution.");
}

[TearDown]
public void ReportOutcome()
{
    var outcome = TestContext.CurrentContext.Result.Outcome;
    if (outcome == ResultState.Failure)
    {
        Console.WriteLine("Test failed — capturing diagnostic info...");
    }
}
```

### Attaching Files (e.g., screenshots, logs)

```csharp
[Test]
public void GenerateReport_AttachOutputFile()
{
    string path = Path.Combine(TestContext.CurrentContext.WorkDirectory, "report.txt");
    File.WriteAllText(path, "Report contents");
    TestContext.AddTestAttachment(path, "Generated report for debugging");
}
```

---

## 13. Parallel Test Execution

```csharp
// Assembly-level: enable parallel execution across fixtures
[assembly: Parallelizable(ParallelScope.Fixtures)]

[TestFixture]
[Parallelizable(ParallelScope.All)] // enable parallel execution of tests within this fixture
public class ParallelizableTests
{
    [Test]
    public void Test1() { Thread.Sleep(100); Assert.Pass(); }

    [Test]
    public void Test2() { Thread.Sleep(100); Assert.Pass(); }
}
```

| ParallelScope value | Meaning |
|---|---|
| `Self` | This test can run in parallel with others |
| `Children` | Child tests/fixtures may run in parallel |
| `Fixtures` | Fixtures run in parallel with each other |
| `All` | Combination of Self + Children |
| `None` | Disable parallelism (default) |

⚠️ Be cautious with shared mutable state (static fields, shared files, databases) when enabling parallel execution.

---

## 14. Custom Constraints & Extensibility

```csharp
public class IsPrimeConstraint : Constraint
{
    public override ConstraintResult ApplyTo<TActual>(TActual actual)
    {
        bool isPrime = IsPrime(Convert.ToInt32(actual));
        return new ConstraintResult(this, actual, isPrime);
    }

    private bool IsPrime(int n)
    {
        if (n < 2) return false;
        for (int i = 2; i <= Math.Sqrt(n); i++)
            if (n % i == 0) return false;
        return true;
    }
}

public static class CustomConstraints
{
    public static IsPrimeConstraint IsPrime => new IsPrimeConstraint();
}

[Test]
public void SeventeenIsPrime()
{
    Assert.That(17, CustomConstraints.IsPrime);
}
```

### Custom Attributes (e.g., auto-retry)

```csharp
public class RetryAttribute : NUnit.Framework.Interfaces.ITestAction
{
    public int MaxAttempts { get; }
    public RetryAttribute(int maxAttempts) => MaxAttempts = maxAttempts;

    public void BeforeTest(NUnit.Framework.Interfaces.ITest test) { }
    public void AfterTest(NUnit.Framework.Interfaces.ITest test) { }
    public NUnit.Framework.Interfaces.ActionTargets Targets => NUnit.Framework.Interfaces.ActionTargets.Test;
}
```

NUnit also ships a built-in `[Retry(n)]` attribute for flaky-test scenarios:

```csharp
[Test, Retry(3)]
public void FlakyNetworkCall_EventuallySucceeds()
{
    // retried up to 3 times if it fails
}
```

---

## 15. Ignoring, Explicit & Conditional Tests

```csharp
[Test]
[Ignore("Not implemented yet — see JIRA-1234")]
public void FeatureNotYetImplemented_Test() { }

[Test]
[Explicit("Run manually only — hits a real external API")]
public void CallsRealPaymentGateway_Test() { }

[Test]
[Platform("Win")]
public void WindowsOnlyFeature_Test() { }

[Test]
[Culture("en-US")]
public void CultureSpecificFormatting_Test() { }

[Test]
public void ConditionallySkippedAtRuntime()
{
    if (!Environment.GetEnvironmentVariable("RUN_SLOW_TESTS")?.Equals("true") ?? true)
        Assert.Ignore("Skipped: slow tests disabled");

    // test body
}
```

---

## 16. Running Tests (CLI & CI)

```bash
# Run all tests
dotnet test

# Run a specific fixture
dotnet test --filter "FullyQualifiedName~CalculatorTests"

# Run a specific test
dotnet test --filter "Name=Add_TwoPositiveNumbers_ReturnsSum"

# Run by category
dotnet test --filter "Category=Integration"

# Generate a test results file (TRX format for CI)
dotnet test --logger "trx;LogFileName=results.trx"

# Collect code coverage (with coverlet)
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

## 17. Best Practices

- One logical assertion concept per test; use `Assert.Multiple` when checking several related properties of one result.
- Follow **Arrange-Act-Assert (AAA)** structure consistently.
- Prefer the constraint model (`Assert.That`) over classic assertions for readability and better failure messages.
- Use `TestCase`/`TestCaseSource` instead of copy-pasting near-identical tests.
- Keep `[SetUp]` lean — expensive one-time initialization belongs in `[OneTimeSetUp]`.
- Avoid shared mutable state between tests, especially under `[Parallelizable]`.
- Name tests descriptively: `MethodName_Scenario_ExpectedResult`.
- Don't test framework/library code — test your own logic and integration points.
- Mock external dependencies (databases, APIs, file systems) at the boundary of your system under test.
- Keep unit tests fast; mark slow/integration tests with `[Category("Integration")]` or `[Explicit]` and run them separately in CI.

---

## 18. Quick Reference Tables

### Attributes

| Attribute | Purpose |
|---|---|
| `[TestFixture]` | Marks a test class |
| `[Test]` | Marks a test method |
| `[SetUp]` / `[TearDown]` | Per-test lifecycle hooks |
| `[OneTimeSetUp]` / `[OneTimeTearDown]` | Per-fixture lifecycle hooks |
| `[TestCase]` | Inline parameterized data |
| `[TestCaseSource]` | External parameterized data |
| `[Values]` / `[Range]` / `[Random]` | Combinatorial parameter sources |
| `[Category]` | Grouping/filtering tests |
| `[Ignore]` | Skip a test |
| `[Explicit]` | Only run when explicitly selected |
| `[Retry(n)]` | Retry flaky tests |
| `[Timeout(ms)]` | Fail test if it exceeds time limit |
| `[Parallelizable]` | Enable parallel execution |
| `[Order(n)]` | Control execution order within a fixture |

### Assertion Cheat Sheet

| Goal | Constraint Model |
|---|---|
| Equality | `Assert.That(x, Is.EqualTo(y))` |
| Boolean | `Assert.That(x, Is.True)` |
| Null | `Assert.That(x, Is.Null)` |
| Exception | `Assert.Throws<T>(() => ...)` |
| Collection contains | `Assert.That(list, Does.Contain(item))` |
| Collection count | `Assert.That(list, Has.Count.EqualTo(n))` |
| String contains | `Assert.That(str, Does.Contain("abc"))` |
| Type check | `Assert.That(obj, Is.InstanceOf<T>())` |
| Range | `Assert.That(x, Is.InRange(1, 10))` |
| Floating tolerance | `Assert.That(x, Is.EqualTo(y).Within(0.001))` |

---

*Practice idea: write a full NUnit test suite for a `ShoppingCart` class covering add/remove items, discount rules (via `TestCaseSource`), async checkout (mocking a payment gateway with Moq), and negative-path exception tests.*
