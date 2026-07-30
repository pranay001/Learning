# The Complete MVVM Guide (WPF / C#)

A beginner-friendly, deeply detailed walkthrough of the **MVVM (Model-View-ViewModel)** architecture pattern, built around a real, working WPF example — then extended into advanced, production-grade concepts.

---

## Table of Contents

1. [What Is MVVM, and Why Does It Exist?](#1-what-is-mvvm-and-why-does-it-exist)
2. [The Three Pieces, Explained Simply](#2-the-three-pieces-explained-simply)
3. [Setting Up the Project](#3-setting-up-the-project)
4. [Step-by-Step Walkthrough: A Contact List App](#4-step-by-step-walkthrough-a-contact-list-app)
5. [Data Binding Deep Dive](#5-data-binding-deep-dive)
6. [Commands Deep Dive](#6-commands-deep-dive)
7. [INotifyPropertyChanged Deep Dive](#7-inotifypropertychanged-deep-dive)
8. [Value Converters](#8-value-converters)
9. [Validation](#9-validation)
10. [Adding, Editing, and Deleting (CRUD in MVVM)](#10-adding-editing-and-deleting-crud-in-mvvm)
11. [Async Operations in ViewModels](#11-async-operations-in-viewmodels)
12. [Navigation Between Views](#12-navigation-between-views)
13. [Dependency Injection in MVVM](#13-dependency-injection-in-mvvm)
14. [Using the CommunityToolkit.Mvvm Library](#14-using-the-communitytoolkitmvvm-library)
15. [Messaging Between ViewModels](#15-messaging-between-viewmodels)
16. [Design-Time Data & XAML Tooling](#16-design-time-data--xaml-tooling)
17. [Unit Testing ViewModels](#17-unit-testing-viewmodels)
18. [Common Mistakes & Anti-Patterns](#18-common-mistakes--anti-patterns)
19. [MVVM vs Other Patterns (MVC, MVP)](#19-mvvm-vs-other-patterns-mvc-mvp)
20. [Best Practices Checklist](#20-best-practices-checklist)
21. [Quick Reference](#21-quick-reference)

---

## 1. What Is MVVM, and Why Does It Exist?

Imagine you built a WPF app the "quick and dirty" way: your button-click event handler in the code-behind file (`MainWindow.xaml.cs`) directly manipulates UI controls, fetches data, does validation, and saves to a database — all in one big blob of code.

This works for a tiny app. But it causes real problems as the app grows:

- **You can't test your logic without a UI.** To test "does adding a contact work correctly," you'd have to launch the actual window and click buttons.
- **UI code and business logic are tangled together.** A designer wants to change the layout; a developer wants to change the save logic — but they're in the same file, so they collide.
- **Code becomes unreusable.** If you want the same "add contact" logic on a different screen or platform, you have to copy-paste it.

**MVVM (Model-View-ViewModel)** solves this by drawing a firm line between:

- **What the UI looks like** (the View — pure XAML, no logic)
- **What the UI needs to work** (the ViewModel — plain C# classes, no UI dependencies at all)
- **What the data actually is** (the Model — your domain objects/business entities)

The View knows about the ViewModel (it binds to it). The ViewModel does **not** know the View exists at all. This one-way relationship is the entire secret of MVVM, and everything else in this guide flows from it.

### A Simple Mental Model

Think of the ViewModel as a "remote control" for the View:

- The ViewModel exposes properties (like `ContactName`) and commands (like `SaveCommand`).
- The View (XAML) *binds* its controls to those properties/commands.
- When the ViewModel's data changes, the View updates automatically (via a notification mechanism).
- When the user clicks a button in the View, a command on the ViewModel runs — but the ViewModel has no idea a "button" was involved; it just knows "an action was requested."

This indirection is what makes ViewModels testable (you can trigger `SaveCommand.Execute()` in a unit test, with no window ever opening) and reusable (the same ViewModel could back a WPF view today and a MAUI view tomorrow).

---

## 2. The Three Pieces, Explained Simply

### Model

Plain data and business logic — no knowledge of the UI whatsoever.

```csharp
public class Contact
{
    public int Id { get; set; }
    public string FirstName { get; set; } = "";
    public string LastName { get; set; } = "";
    public string Email { get; set; } = "";
    public string FullName => $"{FirstName} {LastName}";
}
```

### View

Pure XAML (plus generated code-behind, which should stay nearly empty). Describes layout and appearance, and binds to a ViewModel.

```xml
<Window x:Class="ContactApp.MainWindow" ...>
    <TextBox Text="{Binding SearchText}" />
    <Button Content="Search" Command="{Binding SearchCommand}" />
</Window>
```

### ViewModel

A plain C# class exposing the data and operations the View needs, using properties and commands, and notifying the View of changes.

```csharp
public class ContactListViewModel : INotifyPropertyChanged
{
    private string _searchText = "";
    public string SearchText
    {
        get => _searchText;
        set { _searchText = value; OnPropertyChanged(); }
    }

    public ICommand SearchCommand { get; }

    // ... constructor, OnPropertyChanged, etc. (shown fully in Section 4)
}
```

### The Golden Rule

> **The ViewModel must never reference anything from `System.Windows` (or any UI framework namespace).** No `Button`, no `MessageBox`, no `Window`. If you find yourself needing one of those in a ViewModel, that's a sign you need an abstraction (we'll cover dialog services later).

---

## 3. Setting Up the Project

```bash
dotnet new wpf -n ContactApp
cd ContactApp
```

This creates:

```
ContactApp/
├── App.xaml
├── App.xaml.cs
├── MainWindow.xaml
├── MainWindow.xaml.cs
└── ContactApp.csproj
```

We'll reorganize into a standard MVVM folder structure as we go:

```
ContactApp/
├── Models/
│   └── Contact.cs
├── ViewModels/
│   └── ContactListViewModel.cs
├── Views/
│   └── MainWindow.xaml
├── Commands/
│   └── RelayCommand.cs
├── Services/
│   └── IContactRepository.cs
├── App.xaml
└── App.xaml.cs
```

---

## 4. Step-by-Step Walkthrough: A Contact List App

We'll build a small but complete app: a list of contacts, a search box, and Add/Delete buttons. Every piece of MVVM plumbing will be shown explicitly (no hidden "magic") before we later show shortcuts (like `CommunityToolkit.Mvvm`) that remove boilerplate.

### Step 1 — The Model

```csharp
// Models/Contact.cs
namespace ContactApp.Models
{
    public class Contact
    {
        public int Id { get; set; }
        public string FirstName { get; set; } = "";
        public string LastName { get; set; } = "";
        public string Email { get; set; } = "";
        public string FullName => $"{FirstName} {LastName}";
    }
}
```

### Step 2 — INotifyPropertyChanged Base Class

Every ViewModel needs a way to tell the View "something changed, please redraw." We centralize this logic once so we don't repeat it everywhere.

```csharp
// ViewModels/ViewModelBase.cs
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace ContactApp.ViewModels
{
    public abstract class ViewModelBase : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler? PropertyChanged;

        // CallerMemberName automatically fills in the property name for us,
        // so callers just write OnPropertyChanged() with no arguments.
        protected void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        // Helper that sets a field, raises the event, and returns whether it actually changed
        protected bool SetField<T>(ref T field, T value, [CallerMemberName] string? propertyName = null)
        {
            if (EqualityComparer<T>.Default.Equals(field, value)) return false;
            field = value;
            OnPropertyChanged(propertyName);
            return true;
        }
    }
}
```

### Step 3 — A Reusable RelayCommand (ICommand Implementation)

WPF's `Command` binding requires an `ICommand` object. We write one reusable implementation instead of a new class for every button.

```csharp
// Commands/RelayCommand.cs
using System.Windows.Input;

namespace ContactApp.Commands
{
    public class RelayCommand : ICommand
    {
        private readonly Action<object?> _execute;
        private readonly Func<object?, bool>? _canExecute;

        public RelayCommand(Action<object?> execute, Func<object?, bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }

        // Simplified constructor for the common case of no parameters
        public RelayCommand(Action execute, Func<bool>? canExecute = null)
            : this(_ => execute(), canExecute is null ? null : _ => canExecute())
        {
        }

        public bool CanExecute(object? parameter) => _canExecute?.Invoke(parameter) ?? true;

        public void Execute(object? parameter) => _execute(parameter);

        // WPF listens to this event to know when to re-check CanExecute
        // (e.g., to grey out a button). CommandManager.RequerySuggested fires
        // automatically on most UI events (clicks, key presses, focus changes).
        public event EventHandler? CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }
    }
}
```

### Step 4 — A Repository (Data Access Abstraction)

The ViewModel shouldn't talk to a database or file directly — it should talk to an interface, so the real implementation can be swapped for a fake one in tests.

```csharp
// Services/IContactRepository.cs
using ContactApp.Models;

namespace ContactApp.Services
{
    public interface IContactRepository
    {
        Task<List<Contact>> GetAllAsync();
        Task AddAsync(Contact contact);
        Task DeleteAsync(int contactId);
    }
}
```

```csharp
// Services/InMemoryContactRepository.cs
using ContactApp.Models;

namespace ContactApp.Services
{
    // A simple in-memory stand-in; swap for an EF Core-backed implementation in a real app.
    public class InMemoryContactRepository : IContactRepository
    {
        private readonly List<Contact> _contacts = new()
        {
            new Contact { Id = 1, FirstName = "Alice", LastName = "Nguyen", Email = "alice@example.com" },
            new Contact { Id = 2, FirstName = "Bob", LastName = "Smith", Email = "bob@example.com" },
        };
        private int _nextId = 3;

        public Task<List<Contact>> GetAllAsync() => Task.FromResult(new List<Contact>(_contacts));

        public Task AddAsync(Contact contact)
        {
            contact.Id = _nextId++;
            _contacts.Add(contact);
            return Task.CompletedTask;
        }

        public Task DeleteAsync(int contactId)
        {
            _contacts.RemoveAll(c => c.Id == contactId);
            return Task.CompletedTask;
        }
    }
}
```

### Step 5 — The ViewModel

This is the heart of MVVM. Notice: no `using System.Windows;`, no reference to any XAML control.

```csharp
// ViewModels/ContactListViewModel.cs
using System.Collections.ObjectModel;
using System.Windows.Input;
using ContactApp.Commands;
using ContactApp.Models;
using ContactApp.Services;

namespace ContactApp.ViewModels
{
    public class ContactListViewModel : ViewModelBase
    {
        private readonly IContactRepository _repository;

        // ObservableCollection automatically notifies the View when items
        // are added/removed (but NOT when a property inside an item changes —
        // more on that distinction in Section 5).
        public ObservableCollection<Contact> Contacts { get; } = new();

        private Contact? _selectedContact;
        public Contact? SelectedContact
        {
            get => _selectedContact;
            set
            {
                if (SetField(ref _selectedContact, value))
                {
                    // Tell WPF to re-check whether DeleteCommand can run now
                    (DeleteCommand as RelayCommand)?.RaiseCanExecuteChanged();
                }
            }
        }

        private string _searchText = "";
        public string SearchText
        {
            get => _searchText;
            set => SetField(ref _searchText, value);
        }

        private string _newContactFirstName = "";
        public string NewContactFirstName
        {
            get => _newContactFirstName;
            set => SetField(ref _newContactFirstName, value);
        }

        private string _newContactLastName = "";
        public string NewContactLastName
        {
            get => _newContactLastName;
            set => SetField(ref _newContactLastName, value);
        }

        private bool _isLoading;
        public bool IsLoading
        {
            get => _isLoading;
            set => SetField(ref _isLoading, value);
        }

        public ICommand LoadCommand { get; }
        public ICommand SearchCommand { get; }
        public ICommand AddCommand { get; }
        public ICommand DeleteCommand { get; }

        public ContactListViewModel(IContactRepository repository)
        {
            _repository = repository;

            LoadCommand = new RelayCommand(async () => await LoadContactsAsync());
            SearchCommand = new RelayCommand(async () => await LoadContactsAsync());
            AddCommand = new RelayCommand(
                async () => await AddContactAsync(),
                () => !string.IsNullOrWhiteSpace(NewContactFirstName));
            DeleteCommand = new RelayCommand(
                async () => await DeleteContactAsync(),
                () => SelectedContact != null);
        }

        private async Task LoadContactsAsync()
        {
            IsLoading = true;
            try
            {
                var all = await _repository.GetAllAsync();
                var filtered = string.IsNullOrWhiteSpace(SearchText)
                    ? all
                    : all.Where(c => c.FullName.Contains(SearchText, StringComparison.OrdinalIgnoreCase)).ToList();

                Contacts.Clear();
                foreach (var contact in filtered)
                    Contacts.Add(contact);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task AddContactAsync()
        {
            var contact = new Contact { FirstName = NewContactFirstName, LastName = NewContactLastName };
            await _repository.AddAsync(contact);

            NewContactFirstName = "";
            NewContactLastName = "";

            await LoadContactsAsync();
        }

        private async Task DeleteContactAsync()
        {
            if (SelectedContact == null) return;
            await _repository.DeleteAsync(SelectedContact.Id);
            await LoadContactsAsync();
        }
    }
}
```

Add a small helper to `RelayCommand` so we can force a re-check of `CanExecute` manually when needed:

```csharp
// Add to RelayCommand.cs
public void RaiseCanExecuteChanged() => CommandManager.InvalidateRequerySuggested();
```

### Step 6 — The View (XAML)

```xml
<!-- Views/MainWindow.xaml -->
<Window x:Class="ContactApp.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Contacts" Height="450" Width="600">
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
            <RowDefinition Height="Auto" />
        </Grid.RowDefinitions>

        <!-- Search bar -->
        <StackPanel Orientation="Horizontal" Grid.Row="0" Margin="0,0,0,10">
            <TextBox Width="200" Text="{Binding SearchText, UpdateSourceTrigger=PropertyChanged}" />
            <Button Content="Search" Command="{Binding SearchCommand}" Margin="5,0,0,0" />
            <TextBlock Text="Loading..." Margin="10,0,0,0"
                       Visibility="{Binding IsLoading, Converter={StaticResource BoolToVisibilityConverter}}" />
        </StackPanel>

        <!-- Contact list -->
        <ListView Grid.Row="1" ItemsSource="{Binding Contacts}"
                  SelectedItem="{Binding SelectedContact}">
            <ListView.View>
                <GridView>
                    <GridViewColumn Header="Name" DisplayMemberBinding="{Binding FullName}" Width="200" />
                    <GridViewColumn Header="Email" DisplayMemberBinding="{Binding Email}" Width="250" />
                </GridView>
            </ListView.View>
        </ListView>

        <!-- Add / Delete controls -->
        <StackPanel Orientation="Horizontal" Grid.Row="2" Margin="0,10,0,0">
            <TextBox Width="120" Text="{Binding NewContactFirstName, UpdateSourceTrigger=PropertyChanged}" />
            <TextBox Width="120" Text="{Binding NewContactLastName, UpdateSourceTrigger=PropertyChanged}" Margin="5,0,0,0" />
            <Button Content="Add" Command="{Binding AddCommand}" Margin="5,0,0,0" />
            <Button Content="Delete Selected" Command="{Binding DeleteCommand}" Margin="5,0,0,0" />
        </StackPanel>
    </Grid>
</Window>
```

### Step 7 — Wiring the ViewModel to the View

The code-behind should be nearly empty — its only job is to create the ViewModel and set it as the `DataContext`.

```csharp
// Views/MainWindow.xaml.cs
using System.Windows;
using ContactApp.ViewModels;

namespace ContactApp.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow(ContactListViewModel viewModel)
        {
            InitializeComponent();
            DataContext = viewModel;
        }
    }
}
```

### Step 8 — App.xaml.cs (Composition Root)

```csharp
// App.xaml.cs
using System.Windows;
using ContactApp.Services;
using ContactApp.ViewModels;
using ContactApp.Views;

namespace ContactApp
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Manual "poor man's DI" for now — Section 13 shows a real DI container
            IContactRepository repository = new InMemoryContactRepository();
            var viewModel = new ContactListViewModel(repository);
            var window = new MainWindow(viewModel);

            window.Show();
        }
    }
}
```

Remove the default `StartupUri="MainWindow.xaml"` from `App.xaml` since we're constructing the window manually now:

```xml
<Application x:Class="ContactApp.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <!-- StartupUri removed; startup logic lives in App.xaml.cs -->
</Application>
```

At this point, you have a fully working MVVM app: search, add, delete — all driven by bindings and commands, with zero business logic in the code-behind. Let's now go deep on each concept used above.

---

## 5. Data Binding Deep Dive

### Binding Modes

```xml
<TextBox Text="{Binding SearchText, Mode=TwoWay}" />   <!-- View <-> ViewModel, both directions -->
<TextBlock Text="{Binding FullName, Mode=OneWay}" />    <!-- ViewModel -> View only -->
<TextBlock Text="{Binding StaticLabel, Mode=OneTime}" /> <!-- read once, never updates -->
```

| Mode | Direction | Typical use |
|---|---|---|
| `TwoWay` | View ↔ ViewModel | Editable input fields |
| `OneWay` | ViewModel → View | Read-only display |
| `OneWayToSource` | View → ViewModel | Rare; e.g., capturing raw control state |
| `OneTime` | ViewModel → View, once | Static/rarely-changing values |

`TextBox.Text` defaults to `TwoWay`; most other properties default to `OneWay`.

### UpdateSourceTrigger

Controls **when** a `TwoWay` binding pushes the View's value back to the ViewModel.

```xml
<TextBox Text="{Binding SearchText, UpdateSourceTrigger=PropertyChanged}" /> <!-- every keystroke -->
<TextBox Text="{Binding SearchText, UpdateSourceTrigger=LostFocus}" />       <!-- default for TextBox -->
```

### Binding to Nested Properties

```xml
<TextBlock Text="{Binding SelectedContact.Email}" />
```

If `SelectedContact` is null, WPF simply shows nothing rather than throwing — bindings fail silently by default (with an entry in the Output window during debugging).

### Binding to Collections: ObservableCollection\<T>

```csharp
public ObservableCollection<Contact> Contacts { get; } = new();
```

`ObservableCollection<T>` raises `CollectionChanged` automatically when items are **added or removed**. This is different from noticing when a **property inside an item** changes — for that, the item itself must implement `INotifyPropertyChanged` (see Section 7).

### RelativeSource & ElementName Bindings

```xml
<!-- Bind to another control's property -->
<TextBlock Text="{Binding ElementName=SearchBox, Path=Text.Length}" />

<!-- Bind to a property on an ancestor in the visual tree -->
<Button Content="Close"
        Command="{Binding DataContext.CloseCommand, RelativeSource={RelativeSource AncestorType=Window}}" />
```

### Binding to Static Resources / Enums

```xml
<ComboBox ItemsSource="{Binding Source={StaticResource ContactCategories}}" />
```

### Debugging Bindings

Set `PresentationTraceSources.TraceLevel=High` on a binding temporarily to get detailed diagnostic output in the Visual Studio Output window:

```xml
<TextBlock Text="{Binding FullName, diag:PresentationTraceSources.TraceLevel=High}"
           xmlns:diag="clr-namespace:System.Diagnostics;assembly=WindowsBase" />
```

---

## 6. Commands Deep Dive

### Why Not Just Use Click Events?

```xml
<!-- Avoid this in MVVM -->
<Button Content="Save" Click="SaveButton_Click" />
```

```csharp
// code-behind — logic trapped here, untestable without a live UI
private void SaveButton_Click(object sender, RoutedEventArgs e) { ... }
```

Using `Command` binding instead keeps the logic in the ViewModel, callable from a unit test with no window involved:

```xml
<Button Content="Save" Command="{Binding SaveCommand}" />
```

### CanExecute and Automatic Button Disabling

```csharp
AddCommand = new RelayCommand(
    execute: async () => await AddContactAsync(),
    canExecute: () => !string.IsNullOrWhiteSpace(NewContactFirstName));
```

WPF automatically disables (greys out) any button bound to a command whose `CanExecute` returns `false`, and re-enables it once the condition becomes true — no manual `IsEnabled` binding needed.

### Command Parameters

```xml
<Button Content="Delete" Command="{Binding DeleteCommand}" CommandParameter="{Binding Id}" />
```

```csharp
DeleteCommand = new RelayCommand(param =>
{
    int id = (int)param!;
    // delete logic using id
});
```

### AsyncRelayCommand (Handling async Properly)

The simple `RelayCommand` above uses `async void` internally (via the lambda), which loses exception handling. A more robust `AsyncRelayCommand` tracks execution state and surfaces errors:

```csharp
public class AsyncRelayCommand : ICommand
{
    private readonly Func<Task> _execute;
    private readonly Func<bool>? _canExecute;
    private bool _isExecuting;

    public AsyncRelayCommand(Func<Task> execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public bool CanExecute(object? parameter) => !_isExecuting && (_canExecute?.Invoke() ?? true);

    public async void Execute(object? parameter)
    {
        _isExecuting = true;
        RaiseCanExecuteChanged();
        try
        {
            await _execute();
        }
        finally
        {
            _isExecuting = false;
            RaiseCanExecuteChanged();
        }
    }

    public event EventHandler? CanExecuteChanged;
    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

This version also naturally disables the button while the command is running, preventing double-submission (e.g., double-clicking "Save").

---

## 7. INotifyPropertyChanged Deep Dive

### Why Simple Fields Don't Work

```csharp
public string SearchText; // NOT bindable correctly — WPF has no way to know when this changes
```

Bindings work by subscribing to the `PropertyChanged` event. If a property never raises it, the View shows stale data until something else forces a refresh.

### The Full Pattern, Explained Line by Line

```csharp
private string _searchText = "";

public string SearchText
{
    get => _searchText;
    set
    {
        if (_searchText == value) return;  // avoid redundant notifications
        _searchText = value;
        OnPropertyChanged();               // tell any bound Views to refresh
    }
}
```

Using the `SetField` helper from Section 4 collapses this to one line while keeping the same behavior:

```csharp
public string SearchText
{
    get => _searchText;
    set => SetField(ref _searchText, value);
}
```

### Notifying Dependent (Computed) Properties

```csharp
public string FirstName
{
    get => _firstName;
    set
    {
        if (SetField(ref _firstName, value))
        {
            OnPropertyChanged(nameof(FullName)); // FullName depends on FirstName
        }
    }
}

public string FullName => $"{FirstName} {LastName}";
```

### Making Model Objects Bindable Too

If list items themselves need live-updating fields (e.g., editing a contact's name directly in a grid), the **Model** (or a wrapper around it) needs `INotifyPropertyChanged` as well:

```csharp
public class Contact : ViewModelBase // reusing our base class
{
    private string _firstName = "";
    public string FirstName
    {
        get => _firstName;
        set => SetField(ref _firstName, value);
    }
    // ... etc.
}
```

---

## 8. Value Converters

Converters translate between what the ViewModel exposes (e.g., a `bool`) and what the View needs (e.g., a `Visibility` enum), keeping that translation logic out of both the ViewModel and code-behind.

### BoolToVisibilityConverter

```csharp
using System.Globalization;
using System.Windows;
using System.Windows.Data;

public class BoolToVisibilityConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => (value is bool b && b) ? Visibility.Visible : Visibility.Collapsed;

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is Visibility v && v == Visibility.Visible;
}
```

Register it as a resource (commonly in `App.xaml` for app-wide use):

```xml
<Application.Resources>
    <local:BoolToVisibilityConverter x:Key="BoolToVisibilityConverter" />
</Application.Resources>
```

Use it:

```xml
<TextBlock Text="Loading..."
           Visibility="{Binding IsLoading, Converter={StaticResource BoolToVisibilityConverter}}" />
```

### A Converter with a Parameter

```csharp
public class InverseBoolConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => !(value is bool b && b);

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => !(value is bool b && b);
}
```

```xml
<Button IsEnabled="{Binding IsLoading, Converter={StaticResource InverseBoolConverter}}" />
```

### MultiValueConverter (Combining Several Bindings)

```csharp
public class FullNameConverter : IMultiValueConverter
{
    public object Convert(object[] values, Type targetType, object? parameter, CultureInfo culture)
        => $"{values[0]} {values[1]}";

    public object[] ConvertBack(object value, Type[] targetTypes, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

```xml
<TextBlock>
    <TextBlock.Text>
        <MultiBinding Converter="{StaticResource FullNameConverter}">
            <Binding Path="FirstName" />
            <Binding Path="LastName" />
        </MultiBinding>
    </TextBlock.Text>
</TextBlock>
```

---

## 9. Validation

### IDataErrorInfo (Classic Approach)

```csharp
public class NewContactViewModel : ViewModelBase, IDataErrorInfo
{
    public string FirstName { get; set; } = "";

    public string Error => string.Empty; // rarely used; per-property is more common

    public string this[string columnName]
    {
        get
        {
            return columnName switch
            {
                nameof(FirstName) when string.IsNullOrWhiteSpace(FirstName) => "First name is required.",
                _ => string.Empty
            };
        }
    }
}
```

```xml
<TextBox Text="{Binding FirstName, ValidatesOnDataErrors=True, UpdateSourceTrigger=PropertyChanged}" />
```

### INotifyDataErrorInfo (Modern, Supports Async & Multiple Errors Per Property)

```csharp
using System.Collections;
using System.ComponentModel;

public class ValidatableViewModelBase : ViewModelBase, INotifyDataErrorInfo
{
    private readonly Dictionary<string, List<string>> _errors = new();

    public bool HasErrors => _errors.Any();

    public event EventHandler<DataErrorsChangedEventArgs>? ErrorsChanged;

    public IEnumerable GetErrors(string? propertyName)
        => propertyName != null && _errors.TryGetValue(propertyName, out var errors) ? errors : Array.Empty<string>();

    protected void AddError(string propertyName, string error)
    {
        if (!_errors.ContainsKey(propertyName)) _errors[propertyName] = new List<string>();
        if (!_errors[propertyName].Contains(error))
        {
            _errors[propertyName].Add(error);
            ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
        }
    }

    protected void ClearErrors(string propertyName)
    {
        if (_errors.Remove(propertyName))
            ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
    }
}
```

```csharp
public class NewContactViewModel : ValidatableViewModelBase
{
    private string _firstName = "";
    public string FirstName
    {
        get => _firstName;
        set
        {
            SetField(ref _firstName, value);
            ClearErrors(nameof(FirstName));
            if (string.IsNullOrWhiteSpace(value))
                AddError(nameof(FirstName), "First name is required.");
        }
    }
}
```

```xml
<TextBox Text="{Binding FirstName, UpdateSourceTrigger=PropertyChanged}"
         Validation.ErrorTemplate="{StaticResource ErrorTemplate}" />
```

### DataAnnotations Validation

```csharp
public class NewContactViewModel : ValidatableViewModelBase
{
    [Required(ErrorMessage = "Email is required")]
    [EmailAddress(ErrorMessage = "Invalid email format")]
    public string Email { get; set; } = "";

    public void ValidateAll()
    {
        var context = new ValidationContext(this);
        var results = new List<ValidationResult>();
        Validator.TryValidateObject(this, context, results, validateAllProperties: true);
        // map results into AddError(...) calls per property
    }
}
```

---

## 10. Adding, Editing, and Deleting (CRUD in MVVM)

### Pattern: Separate ViewModel Per Concern

Rather than cramming "add new contact" fields directly into `ContactListViewModel` (as our walkthrough did for simplicity), production apps typically use a dedicated ViewModel for editing, often shown in a dialog:

```csharp
public class ContactEditViewModel : ValidatableViewModelBase
{
    public Contact Contact { get; }

    public ICommand SaveCommand { get; }
    public ICommand CancelCommand { get; }

    public event Action<bool>? RequestClose; // true = saved, false = cancelled

    public ContactEditViewModel(Contact contact)
    {
        Contact = contact;
        SaveCommand = new RelayCommand(() => RequestClose?.Invoke(true), () => !HasErrors);
        CancelCommand = new RelayCommand(() => RequestClose?.Invoke(false));
    }
}
```

The View subscribes to `RequestClose` in code-behind (this is one of the few legitimate uses of code-behind — closing a dialog window is inherently a "View" concern):

```csharp
public partial class ContactEditWindow : Window
{
    public ContactEditWindow(ContactEditViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        viewModel.RequestClose += saved =>
        {
            DialogResult = saved;
            Close();
        };
    }
}
```

### Dialog Services (Avoiding MessageBox in ViewModels)

Calling `MessageBox.Show(...)` directly inside a ViewModel breaks the "no UI references" rule and makes testing painful. Instead, define an abstraction:

```csharp
public interface IDialogService
{
    void ShowMessage(string message);
    bool ShowConfirmation(string message);
}

public class WpfDialogService : IDialogService
{
    public void ShowMessage(string message) => MessageBox.Show(message);
    public bool ShowConfirmation(string message) =>
        MessageBox.Show(message, "Confirm", MessageBoxButton.YesNo) == MessageBoxResult.Yes;
}
```

```csharp
public class ContactListViewModel : ViewModelBase
{
    private readonly IDialogService _dialogService;

    public ContactListViewModel(IContactRepository repository, IDialogService dialogService)
    {
        _dialogService = dialogService;
        // ...
    }

    private async Task DeleteContactAsync()
    {
        if (SelectedContact == null) return;
        if (!_dialogService.ShowConfirmation($"Delete {SelectedContact.FullName}?")) return;

        await _repository.DeleteAsync(SelectedContact.Id);
        await LoadContactsAsync();
    }
}
```

Now, in unit tests, you inject a fake `IDialogService` that always returns `true`/`false` without ever showing a real dialog.

---

## 11. Async Operations in ViewModels

### Why async Matters in MVVM

Blocking the UI thread (e.g., calling `.Result` on a `Task`) freezes the entire application — no button clicks, no window redraws — until the operation finishes. ViewModels should use `async`/`await` for any I/O (database, file, network).

### IsLoading / IsBusy Pattern

```csharp
private async Task LoadContactsAsync()
{
    IsLoading = true;
    try
    {
        var all = await _repository.GetAllAsync();
        Contacts.Clear();
        foreach (var c in all) Contacts.Add(c);
    }
    catch (Exception ex)
    {
        _dialogService.ShowMessage($"Failed to load contacts: {ex.Message}");
    }
    finally
    {
        IsLoading = false;
    }
}
```

```xml
<ProgressBar IsIndeterminate="True"
             Visibility="{Binding IsLoading, Converter={StaticResource BoolToVisibilityConverter}}" />
```

### Cancellation Support

```csharp
private CancellationTokenSource? _searchCts;

private async Task SearchAsync()
{
    _searchCts?.Cancel();
    _searchCts = new CancellationTokenSource();
    var token = _searchCts.Token;

    try
    {
        await Task.Delay(300, token); // debounce rapid typing
        var results = await _repository.SearchAsync(SearchText, token);

        Contacts.Clear();
        foreach (var c in results) Contacts.Add(c);
    }
    catch (OperationCanceledException)
    {
        // a newer search superseded this one — safe to ignore
    }
}
```

---

## 12. Navigation Between Views

### Simple Approach: ViewModel-First Navigation with a Content Presenter

```csharp
public class ShellViewModel : ViewModelBase
{
    private object? _currentView;
    public object? CurrentView
    {
        get => _currentView;
        set => SetField(ref _currentView, value);
    }

    public ICommand GoToContactListCommand { get; }
    public ICommand GoToSettingsCommand { get; }

    public ShellViewModel(ContactListViewModel contactListVm, SettingsViewModel settingsVm)
    {
        GoToContactListCommand = new RelayCommand(() => CurrentView = contactListVm);
        GoToSettingsCommand = new RelayCommand(() => CurrentView = settingsVm);

        CurrentView = contactListVm; // default screen
    }
}
```

```xml
<Window.Resources>
    <DataTemplate DataType="{x:Type vm:ContactListViewModel}">
        <views:ContactListView />
    </DataTemplate>
    <DataTemplate DataType="{x:Type vm:SettingsViewModel}">
        <views:SettingsView />
    </DataTemplate>
</Window.Resources>

<DockPanel>
    <StackPanel DockPanel.Dock="Left">
        <Button Content="Contacts" Command="{Binding GoToContactListCommand}" />
        <Button Content="Settings" Command="{Binding GoToSettingsCommand}" />
    </StackPanel>
    <ContentControl Content="{Binding CurrentView}" />
</DockPanel>
```

WPF automatically picks the right `DataTemplate` based on the **type** of the object in `CurrentView` — this is called **implicit DataTemplate selection** and is central to "ViewModel-first" navigation.

### Frame/Page-Based Navigation (Alternative)

For wizard-style or page-stack navigation, WPF's `Frame` + `Page` model with a `NavigationService` abstraction is common in larger apps, but the ViewModel-first `ContentControl` swap above is simpler and sufficient for most business apps.

---

## 13. Dependency Injection in MVVM

Manually `new`-ing up ViewModels and their dependencies (as in Step 8) doesn't scale. `Microsoft.Extensions.DependencyInjection` (the same container used in ASP.NET Core) works great in WPF too.

```bash
dotnet add package Microsoft.Extensions.DependencyInjection
dotnet add package Microsoft.Extensions.Hosting
```

```csharp
// App.xaml.cs
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

public partial class App : Application
{
    private IHost _host = null!;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                services.AddSingleton<IContactRepository, InMemoryContactRepository>();
                services.AddSingleton<IDialogService, WpfDialogService>();

                services.AddTransient<ContactListViewModel>();
                services.AddTransient<SettingsViewModel>();
                services.AddTransient<ShellViewModel>();

                services.AddTransient<MainWindow>();
            })
            .Build();

        _host.Start();

        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _host.Dispose();
        base.OnExit(e);
    }
}
```

```csharp
public partial class MainWindow : Window
{
    // The DI container automatically supplies ShellViewModel and its own dependencies
    public MainWindow(ShellViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
```

### Service Lifetimes

| Lifetime | Behavior | Typical use in WPF |
|---|---|---|
| `Singleton` | One instance for the app's lifetime | Repositories, configuration, shared caches |
| `Transient` | New instance every time it's requested | ViewModels (usually), lightweight services |
| `Scoped` | One instance per "scope" | Less common in WPF (more relevant to web request scopes) |

---

## 14. Using the CommunityToolkit.Mvvm Library

Writing `INotifyPropertyChanged` boilerplate and `RelayCommand` by hand (as we did above, deliberately, for learning) is exactly what **CommunityToolkit.Mvvm** (Microsoft's official MVVM helper library) eliminates via source generators.

```bash
dotnet add package CommunityToolkit.Mvvm
```

### Before (manual) vs After (toolkit)

**Manual version (what we wrote above):**

```csharp
private string _searchText = "";
public string SearchText
{
    get => _searchText;
    set => SetField(ref _searchText, value);
}
```

**Toolkit version:**

```csharp
public partial class ContactListViewModel : ObservableObject
{
    [ObservableProperty]
    private string searchText = "";
}
```

The `[ObservableProperty]` attribute is a **source generator** — at compile time, it generates a full public `SearchText` property (with proper `PropertyChanged` notifications) from the private field. You write far less code, with identical runtime behavior.

### Commands via [RelayCommand]

```csharp
public partial class ContactListViewModel : ObservableObject
{
    private readonly IContactRepository _repository;

    [ObservableProperty]
    private ObservableCollection<Contact> contacts = new();

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(DeleteCommand))]
    private Contact? selectedContact;

    public ContactListViewModel(IContactRepository repository)
    {
        _repository = repository;
    }

    [RelayCommand]
    private async Task LoadAsync()
    {
        var all = await _repository.GetAllAsync();
        Contacts = new ObservableCollection<Contact>(all);
    }

    [RelayCommand(CanExecute = nameof(CanDelete))]
    private async Task DeleteAsync()
    {
        if (SelectedContact == null) return;
        await _repository.DeleteAsync(SelectedContact.Id);
        await LoadAsync();
    }

    private bool CanDelete() => SelectedContact != null;
}
```

This generates `LoadCommand` and `DeleteCommand` properties of type `IAsyncRelayCommand` automatically, wired to `LoadAsync`/`DeleteAsync`, complete with `CanExecute` support and automatic re-evaluation when `SelectedContact` changes (via `[NotifyCanExecuteChangedFor]`).

```xml
<Button Content="Delete" Command="{Binding DeleteCommand}" />
```

### Validation with the Toolkit

```csharp
public partial class NewContactViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "First name is required")]
    private string firstName = "";
}
```

---

## 15. Messaging Between ViewModels

Sometimes two unrelated ViewModels need to communicate (e.g., adding a contact in a dialog should refresh the list in another screen) without holding a direct reference to each other. The **Messenger** (mediator/pub-sub) pattern from `CommunityToolkit.Mvvm` handles this.

```csharp
// Define a message type
public class ContactAddedMessage
{
    public Contact Contact { get; }
    public ContactAddedMessage(Contact contact) => Contact = contact;
}
```

```csharp
// Sender (e.g., the Add dialog's ViewModel)
public partial class ContactEditViewModel : ObservableObject
{
    [RelayCommand]
    private void Save()
    {
        var contact = new Contact { FirstName = FirstName, LastName = LastName };
        WeakReferenceMessenger.Default.Send(new ContactAddedMessage(contact));
    }
}
```

```csharp
// Receiver (e.g., the list ViewModel)
public partial class ContactListViewModel : ObservableObject, IRecipient<ContactAddedMessage>
{
    public ContactListViewModel()
    {
        WeakReferenceMessenger.Default.RegisterAll(this);
    }

    public void Receive(ContactAddedMessage message)
    {
        Contacts.Add(message.Contact);
    }
}
```

The "Weak" in `WeakReferenceMessenger` means it holds weak references to recipients, so registering doesn't prevent garbage collection if a ViewModel is otherwise no longer referenced — avoiding a common memory-leak trap with naive event-based pub-sub.

---

## 16. Design-Time Data & XAML Tooling

One of MVVM's underrated benefits: you can see realistic data in the Visual Studio/Rider XAML designer **without running the app**, by binding to a design-time-only ViewModel.

```xml
<Window ...
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:vm="clr-namespace:ContactApp.ViewModels"
        mc:Ignorable="d"
        d:DataContext="{d:DesignInstance Type=vm:ContactListDesignViewModel, IsDesignTimeCreatable=True}">
```

```csharp
public class ContactListDesignViewModel : ContactListViewModel
{
    public ContactListDesignViewModel() : base(new FakeDesignTimeRepository())
    {
        // Pre-populate with fixed sample data so the designer shows something realistic
    }
}
```

This lets designers/developers tweak layout and styling while looking at representative data, entirely separate from the real, DI-driven runtime ViewModel.

---

## 17. Unit Testing ViewModels

This is the payoff for following MVVM discipline: ViewModels can be fully tested with no WPF window, no STA thread, no UI automation.

```bash
dotnet new xunit -n ContactApp.Tests
dotnet add package Moq
```

```csharp
using Xunit;
using Moq;
using ContactApp.ViewModels;
using ContactApp.Services;
using ContactApp.Models;

public class ContactListViewModelTests
{
    [Fact]
    public async Task LoadCommand_PopulatesContacts()
    {
        // Arrange
        var mockRepo = new Mock<IContactRepository>();
        mockRepo.Setup(r => r.GetAllAsync()).ReturnsAsync(new List<Contact>
        {
            new Contact { Id = 1, FirstName = "Alice", LastName = "Nguyen" }
        });
        var mockDialog = new Mock<IDialogService>();
        var viewModel = new ContactListViewModel(mockRepo.Object, mockDialog.Object);

        // Act
        viewModel.LoadCommand.Execute(null);
        await Task.Delay(50); // allow the async void command to complete in this simple example

        // Assert
        Assert.Single(viewModel.Contacts);
        Assert.Equal("Alice Nguyen", viewModel.Contacts[0].FullName);
    }

    [Fact]
    public void AddCommand_CanExecute_FalseWhenFirstNameEmpty()
    {
        var viewModel = new ContactListViewModel(Mock.Of<IContactRepository>(), Mock.Of<IDialogService>());
        viewModel.NewContactFirstName = "";

        Assert.False(viewModel.AddCommand.CanExecute(null));

        viewModel.NewContactFirstName = "Carol";
        Assert.True(viewModel.AddCommand.CanExecute(null));
    }

    [Fact]
    public async Task DeleteCommand_UserCancelsConfirmation_DoesNotCallRepository()
    {
        var mockRepo = new Mock<IContactRepository>();
        var mockDialog = new Mock<IDialogService>();
        mockDialog.Setup(d => d.ShowConfirmation(It.IsAny<string>())).Returns(false); // user clicks "No"

        var viewModel = new ContactListViewModel(mockRepo.Object, mockDialog.Object)
        {
            SelectedContact = new Contact { Id = 1, FirstName = "Alice" }
        };

        viewModel.DeleteCommand.Execute(null);
        await Task.Delay(50);

        mockRepo.Verify(r => r.DeleteAsync(It.IsAny<int>()), Times.Never);
    }
}
```

For the `AsyncRelayCommand` version from Section 6 (or the CommunityToolkit's `IAsyncRelayCommand`), you can `await` the command's `ExecuteAsync` directly instead of using `Task.Delay` as a workaround, making tests fully deterministic:

```csharp
[Fact]
public async Task LoadCommand_PopulatesContacts_Deterministic()
{
    var mockRepo = new Mock<IContactRepository>();
    mockRepo.Setup(r => r.GetAllAsync()).ReturnsAsync(new List<Contact> { new() { FirstName = "Alice" } });
    var viewModel = new ContactListViewModel(mockRepo.Object, Mock.Of<IDialogService>());

    await ((IAsyncRelayCommand)viewModel.LoadCommand).ExecuteAsync(null);

    Assert.Single(viewModel.Contacts);
}
```

---

## 18. Common Mistakes & Anti-Patterns

| Anti-pattern | Why it's a problem | Fix |
|---|---|---|
| Putting business logic in code-behind (`Button_Click`) | Untestable, tightly couples UI to logic | Move logic into ViewModel commands |
| ViewModel referencing `System.Windows.Controls` types | Breaks testability, couples ViewModel to WPF specifically | Use abstractions (`IDialogService`, `INavigationService`) |
| Using plain fields instead of properties with `OnPropertyChanged` | View silently shows stale data | Always raise `PropertyChanged` on every bindable property |
| One giant "God ViewModel" for the whole app | Hard to test, hard to reason about, everything is coupled | Split into focused ViewModels (list, detail, edit) composed via navigation |
| Calling `.Result`/`.Wait()` on async calls in a ViewModel | Can deadlock the UI thread | Always `await`; use `async Task` command implementations |
| Forgetting `UpdateSourceTrigger=PropertyChanged` on live-search text boxes | Search only triggers after losing focus | Set explicitly when instant feedback is needed |
| Not disposing/unsubscribing from Messenger registrations | Memory leaks, ghost handlers firing after a ViewModel should be gone | Use `WeakReferenceMessenger`, or explicitly `Unregister` in cleanup |
| Two-way binding on a property that should be read-only | User can silently "edit" something that should be static | Use `Mode=OneWay` explicitly for computed/read-only properties |

---

## 19. MVVM vs Other Patterns (MVC, MVP)

| Pattern | Who talks to whom | Where display logic lives | Typical platform |
|---|---|---|---|
| **MVC** (Model-View-Controller) | Controller updates Model and selects View; View often reads Model directly | Split between Controller and View | Web frameworks (ASP.NET MVC, Rails) |
| **MVP** (Model-View-Presenter) | View has a reference to Presenter; Presenter has a reference back to View (via an interface) and manipulates it directly | Presenter | WinForms, older Android |
| **MVVM** | View binds to ViewModel; ViewModel has **no reference to the View at all** | ViewModel, surfaced via bindable properties | WPF, MAUI, Avalonia, Xamarin.Forms |

The defining difference: MVVM's data-binding engine is what allows the View to stay updated *without* the ViewModel needing to hold any reference back to it — this is only practical because frameworks like WPF have a first-class binding system. MVP predates rich binding engines and needed the Presenter to manually push updates to the View through an interface.

---

## 20. Best Practices Checklist

- [ ] ViewModels contain **zero** references to `System.Windows.*` UI types.
- [ ] Every bindable property raises `PropertyChanged` (directly, or via a toolkit-generated property).
- [ ] Commands are used instead of Click event handlers for all user-triggered actions.
- [ ] `CanExecute` is used to control interactivity, not manual `IsEnabled` bindings duplicating the same logic.
- [ ] Long-running work is `async`, with an `IsLoading`/`IsBusy` flag bound to a progress indicator.
- [ ] Dialogs/MessageBoxes are accessed through an injected service interface, not called directly.
- [ ] Dependencies (repositories, services) are injected via constructor, not `new`-ed inside the ViewModel.
- [ ] ViewModels are unit tested without ever creating a `Window` or requiring an STA thread.
- [ ] Cross-ViewModel communication uses a messenger/mediator rather than direct references between unrelated ViewModels.
- [ ] Code-behind is minimal — ideally just `InitializeComponent()` and DataContext assignment (plus legitimate View-only concerns like closing a dialog window).

---

## 21. Quick Reference

### Core Building Blocks

| Concept | Purpose |
|---|---|
| `INotifyPropertyChanged` | Lets the View know a property's value changed |
| `ObservableCollection<T>` | Lets the View know items were added/removed from a collection |
| `ICommand` | Represents an action the View can trigger, decoupled from any specific control |
| `IValueConverter` | Translates a ViewModel value into a View-friendly representation (and back) |
| `IDataErrorInfo` / `INotifyDataErrorInfo` | Surfaces validation errors to the View |
| `DataTemplate` | Maps a ViewModel type to the View that should render it |

### Binding Syntax Cheat Sheet

```xml
{Binding PropertyName}
{Binding PropertyName, Mode=TwoWay}
{Binding PropertyName, UpdateSourceTrigger=PropertyChanged}
{Binding PropertyName, Converter={StaticResource MyConverter}}
{Binding PropertyName, ElementName=OtherControl}
{Binding PropertyName, RelativeSource={RelativeSource AncestorType=Window}}
{Binding Path=Nested.Property}
```

### CommunityToolkit.Mvvm Cheat Sheet

| Manual approach | Toolkit approach |
|---|---|
| Private field + property + `OnPropertyChanged()` | `[ObservableProperty] private string myField;` |
| Custom `RelayCommand` class | `[RelayCommand] private void DoThing() { }` |
| Manual `IDataErrorInfo` | `ObservableValidator` + `[NotifyDataErrorInfo]` + DataAnnotations |
| Custom pub-sub / events | `WeakReferenceMessenger.Default.Send(...)` / `IRecipient<T>` |

---

*Practice idea: extend the Contact app with an Edit dialog (Section 10), swap the manual plumbing for `CommunityToolkit.Mvvm` (Section 14), add validation on the email field (Section 9), and write a full test suite for the list, add, and delete flows (Section 17) — without ever launching the actual window.*
