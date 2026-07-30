# The Complete WPF Guide (Beginner to Advanced)

A detailed, example-driven reference for building desktop applications with **WPF (Windows Presentation Foundation)** — covering every major UI element type, layout system, styling mechanism, and advanced customization technique.

---

## Table of Contents

1. [Introduction to WPF](#1-introduction-to-wpf)
2. [XAML Fundamentals](#2-xaml-fundamentals)
3. [Layout Panels](#3-layout-panels)
4. [Basic Controls: Text & Input](#4-basic-controls-text--input)
5. [Buttons & Selection Controls](#5-buttons--selection-controls)
6. [List & Data Display Controls](#6-list--data-display-controls)
7. [Menus, Toolbars & Navigation Controls](#7-menus-toolbars--navigation-controls)
8. [Containers: Tabs, Group Boxes & Expanders](#8-containers-tabs-group-boxes--expanders)
9. [Dialogs & Windows](#9-dialogs--windows)
10. [Images, Media & Shapes](#10-images-media--shapes)
11. [Data Binding Essentials](#11-data-binding-essentials)
12. [Resources: Styles, Brushes & Reuse](#12-resources-styles-brushes--reuse)
13. [Control Templates & Custom Look-and-Feel](#13-control-templates--custom-look-and-feel)
14. [Data Templates](#14-data-templates)
15. [Triggers & Visual States](#15-triggers--visual-states)
16. [Animations](#16-animations)
17. [Custom Controls & User Controls](#17-custom-controls--user-controls)
18. [Attached Properties & Behaviors](#18-attached-properties--behaviors)
19. [Commands & Input Handling](#19-commands--input-handling)
20. [Performance & Virtualization](#20-performance--virtualization)
21. [Best Practices](#21-best-practices)
22. [Quick Reference](#22-quick-reference)

---

## 1. Introduction to WPF

**WPF (Windows Presentation Foundation)** is Microsoft's UI framework for building rich Windows desktop applications, first released with .NET 3.0 and still actively maintained on modern .NET (via `net8.0-windows`, etc.).

### What Makes WPF Different

- **XAML-based UI** — layout and appearance are described declaratively in XML-like markup, separate from your C# logic.
- **Vector-based rendering** — UI scales cleanly across DPI settings and window sizes, unlike older pixel-based frameworks (WinForms).
- **Powerful data binding** — the foundation that makes the MVVM pattern practical (see the companion MVVM guide for the architectural side of this).
- **Deep styling/templating system** — nearly any control's appearance can be completely replaced without changing its behavior.
- **Composability** — nearly every WPF control can contain other controls (a `Button` can contain an `Image` + `TextBlock`, not just plain text).

### Creating a WPF Project

```bash
dotnet new wpf -n MyWpfApp
cd MyWpfApp
dotnet run
```

This generates:

```
MyWpfApp/
├── App.xaml           <- application-wide resources & startup config
├── App.xaml.cs
├── MainWindow.xaml     <- your first window's UI
├── MainWindow.xaml.cs  <- code-behind (event handlers, initialization)
└── MyWpfApp.csproj
```

---

## 2. XAML Fundamentals

XAML (**E**xtensible **A**pplication **M**arkup **L**anguage) is XML that maps directly to .NET objects and their properties.

### Elements Map to Classes; Attributes Map to Properties

```xml
<Button Content="Click Me" Width="120" Height="30" Background="LightBlue" />
```

is functionally equivalent to writing, in C#:

```csharp
var button = new Button { Content = "Click Me", Width = 120, Height = 30, Background = Brushes.LightBlue };
```

### Nesting = Content

```xml
<Button Width="150" Height="40">
    <StackPanel Orientation="Horizontal">
        <TextBlock Text="Save" />
        <TextBlock Text=" 💾" />
    </StackPanel>
</Button>
```

A `Button`'s `Content` property can hold *any* single object — including an entire layout of nested controls, not just a string.

### Property Element Syntax (for complex property values)

```xml
<Button>
    <Button.Background>
        <LinearGradientBrush StartPoint="0,0" EndPoint="0,1">
            <GradientStop Color="White" Offset="0" />
            <GradientStop Color="LightGray" Offset="1" />
        </LinearGradientBrush>
    </Button.Background>
    <Button.Content>Gradient Button</Button.Content>
</Button>
```

Use attribute syntax (`Background="LightBlue"`) for simple values, and property-element syntax (`<Button.Background>...</Button.Background>`) when the value itself needs to be a nested object (like a gradient).

### Namespaces

```xml
<Window x:Class="MyWpfApp.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:local="clr-namespace:MyWpfApp">
```

| Prefix | Purpose |
|---|---|
| (default, no prefix) | Standard WPF controls (`Button`, `Grid`, etc.) |
| `x:` | XAML language features (`x:Name`, `x:Key`, `x:Class`) |
| `local:` | Your own project's namespace, for referencing custom types/controls |

### x:Name vs Name

```xml
<TextBox x:Name="SearchBox" />
```

`x:Name` (or the equivalent `Name` property on `FrameworkElement`-derived types) lets you reference a XAML element from code-behind:

```csharp
SearchBox.Text = "Hello"; // auto-generated field, thanks to InitializeComponent()
```

### Markup Extensions

```xml
<TextBlock Text="{Binding UserName}" />                  <!-- data binding -->
<Button Background="{StaticResource PrimaryBrush}" />     <!-- resource lookup -->
<TextBlock Foreground="{x:Static Brushes.Red}" />          <!-- reference a static member -->
<ComboBox ItemsSource="{Binding Source={x:Static local:Options.All}}" />
```

Anything in `{CurlyBraces}` is a **markup extension** — a special syntax that resolves to a value at parse/runtime rather than being a literal string.

---

## 3. Layout Panels

Layout panels are containers that arrange their children according to specific rules. Choosing the right panel is one of the most important early WPF skills.

### Grid — Rows & Columns (Most Versatile)

```xml
<Grid>
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto" />   <!-- sized to content -->
        <RowDefinition Height="*" />      <!-- takes remaining space -->
        <RowDefinition Height="2*" />     <!-- takes 2x the space of a plain "*" row -->
    </Grid.RowDefinitions>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="150" />  <!-- fixed width -->
        <ColumnDefinition Width="*" />
    </Grid.ColumnDefinitions>

    <TextBlock Text="Header" Grid.Row="0" Grid.Column="0" Grid.ColumnSpan="2" />
    <ListBox Grid.Row="1" Grid.Column="0" />
    <ContentControl Grid.Row="1" Grid.Column="1" />
    <TextBlock Text="Footer" Grid.Row="2" Grid.Column="0" Grid.ColumnSpan="2" />
</Grid>
```

| Height/Width value | Meaning |
|---|---|
| `Auto` | Sized to fit its content |
| `*` | Proportional share of remaining space |
| `2*` | Proportional share, weighted 2x relative to plain `*` |
| `150` | Fixed size in device-independent pixels |

### StackPanel — Simple Linear Layout

```xml
<StackPanel Orientation="Vertical">
    <TextBlock Text="Username" />
    <TextBox />
    <TextBlock Text="Password" Margin="0,10,0,0" />
    <PasswordBox />
</StackPanel>
```

```xml
<StackPanel Orientation="Horizontal">
    <Button Content="OK" Width="80" />
    <Button Content="Cancel" Width="80" Margin="10,0,0,0" />
</StackPanel>
```

`StackPanel` gives each child as much space as it wants along the stacking axis — great for toolbars, button rows, and simple forms, but it doesn't distribute extra space evenly (use `Grid` with `*` sizing for that).

### DockPanel — Edge-Anchored Layout

```xml
<DockPanel LastChildFill="True">
    <Menu DockPanel.Dock="Top">...</Menu>
    <StatusBar DockPanel.Dock="Bottom">...</StatusBar>
    <TreeView DockPanel.Dock="Left" Width="200" />
    <TextBox /> <!-- fills all remaining space (LastChildFill) -->
</DockPanel>
```

Classic pattern for application shells: menu on top, status bar on bottom, a side panel, and a main content area filling the rest.

### WrapPanel — Flows Content, Wrapping to New Lines

```xml
<WrapPanel>
    <Button Content="Tag 1" Margin="2" />
    <Button Content="Tag 2" Margin="2" />
    <Button Content="Tag 3" Margin="2" />
    <!-- wraps to a new row automatically when space runs out -->
</WrapPanel>
```

Great for tag clouds, toolbars that need to reflow, or thumbnail galleries.

### Canvas — Absolute Positioning

```xml
<Canvas>
    <Ellipse Canvas.Left="50" Canvas.Top="30" Width="40" Height="40" Fill="Red" />
    <Rectangle Canvas.Left="120" Canvas.Top="30" Width="60" Height="40" Fill="Blue" />
</Canvas>
```

Use sparingly — `Canvas` doesn't reflow or resize with the window, so it's mainly appropriate for diagrams, drawing surfaces, or game-like visuals rather than typical application forms.

### UniformGrid — Equal-Sized Cells

```xml
<UniformGrid Rows="3" Columns="3">
    <Button Content="1" /> <Button Content="2" /> <Button Content="3" />
    <Button Content="4" /> <Button Content="5" /> <Button Content="6" />
    <Button Content="7" /> <Button Content="8" /> <Button Content="9" />
</UniformGrid>
```

Perfect for calculator-style layouts or evenly-sized grids of items.

### Nesting Panels

Real layouts almost always nest panels — e.g., a `DockPanel` shell containing a `Grid` form containing `StackPanel` rows:

```xml
<DockPanel>
    <Menu DockPanel.Dock="Top">...</Menu>
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>
        <StackPanel Orientation="Horizontal" Grid.Row="0">
            <TextBox Width="200" />
            <Button Content="Search" Margin="5,0,0,0" />
        </StackPanel>
        <ListBox Grid.Row="1" Margin="0,10,0,0" />
    </Grid>
</DockPanel>
```

---

## 4. Basic Controls: Text & Input

### TextBlock — Read-Only Text Display

```xml
<TextBlock Text="Hello, World!" FontSize="16" FontWeight="Bold" Foreground="DarkSlateGray" />

<!-- Multi-run formatted text -->
<TextBlock>
    <Run Text="Status: " />
    <Run Text="Active" Foreground="Green" FontWeight="Bold" />
</TextBlock>

<!-- Wrapping and trimming -->
<TextBlock Text="A very long sentence that needs to wrap across multiple lines automatically."
           TextWrapping="Wrap" Width="200" />
<TextBlock Text="A very long sentence that gets cut off with an ellipsis."
           TextTrimming="CharacterEllipsis" Width="150" />
```

### TextBox — Single or Multi-Line Editable Text

```xml
<TextBox Width="200" Text="{Binding SearchTerm, UpdateSourceTrigger=PropertyChanged}" />

<!-- Multi-line -->
<TextBox Width="300" Height="100" AcceptsReturn="True" TextWrapping="Wrap"
         VerticalScrollBarVisibility="Auto" />

<!-- With placeholder-like behavior (WPF has no native placeholder; common workaround) -->
<Grid>
    <TextBox x:Name="EmailBox" Width="200" />
    <TextBlock Text="Enter your email..." IsHitTestVisible="False" Margin="5,0,0,0"
               VerticalAlignment="Center" Foreground="Gray">
        <TextBlock.Style>
            <Style TargetType="TextBlock">
                <Setter Property="Visibility" Value="Collapsed" />
                <Style.Triggers>
                    <DataTrigger Binding="{Binding Text.Length, ElementName=EmailBox}" Value="0">
                        <Setter Property="Visibility" Value="Visible" />
                    </DataTrigger>
                </Style.Triggers>
            </Style>
        </TextBlock.Style>
    </TextBlock>
</Grid>
```

### PasswordBox — Masked Input

```xml
<PasswordBox x:Name="PasswordInput" Width="200" PasswordChar="•" />
```

```csharp
// PasswordBox.Password is intentionally NOT bindable directly (security reasons —
// binding would keep the plaintext password in memory/ViewModel longer than necessary)
string password = PasswordInput.Password;
```

### RichTextBox — Formatted Document Editing

```xml
<RichTextBox Width="300" Height="150">
    <FlowDocument>
        <Paragraph>
            <Run Text="This is " />
            <Bold><Run Text="bold" /></Bold>
            <Run Text=" and this is " />
            <Italic><Run Text="italic" /></Italic>
            <Run Text="." />
        </Paragraph>
    </FlowDocument>
</RichTextBox>
```

### Label — Text with Extra Chrome (Mnemonics)

```xml
<Label Content="_Username" Target="{Binding ElementName=UsernameBox}" />
<TextBox x:Name="UsernameBox" />
<!-- Alt+U in the running app moves focus to UsernameBox -->
```

Prefer `TextBlock` for plain display text (lighter weight); use `Label` when you need mnemonic/access-key support or need to host arbitrary content with padding defaults similar to a control.

---

## 5. Buttons & Selection Controls

### Button

```xml
<Button Content="Save" Width="100" Click="SaveButton_Click" />

<!-- MVVM style (preferred — see the MVVM guide for the full pattern) -->
<Button Content="Save" Command="{Binding SaveCommand}" />

<!-- Button with an icon + text -->
<Button Width="120" Height="36">
    <StackPanel Orientation="Horizontal">
        <TextBlock Text="💾" Margin="0,0,5,0" />
        <TextBlock Text="Save" />
    </StackPanel>
</Button>
```

### ToggleButton

```xml
<ToggleButton Content="Bold" IsChecked="{Binding IsBold}" Width="60" />
```

### RepeatButton — Fires Repeatedly While Held

```xml
<RepeatButton Content="+" Click="Increment_Click" Interval="100" Delay="500" />
```

Commonly used inside custom `Slider`/`ScrollBar` templates (see Section 13) for the increment/decrement arrows.

### CheckBox

```xml
<CheckBox Content="Remember me" IsChecked="{Binding RememberMe}" />

<!-- Three-state (indeterminate) -->
<CheckBox Content="Select all" IsThreeState="True" IsChecked="{Binding SelectAllState}" />
```

### RadioButton — Mutually Exclusive Options

```xml
<StackPanel>
    <RadioButton Content="Small" GroupName="Size" IsChecked="{Binding IsSmall}" />
    <RadioButton Content="Medium" GroupName="Size" IsChecked="{Binding IsMedium}" />
    <RadioButton Content="Large" GroupName="Size" IsChecked="{Binding IsLarge}" />
</StackPanel>
```

`GroupName` scopes mutual exclusivity — radio buttons with different `GroupName` values (or in different containers without a shared name) behave independently.

### ComboBox — Dropdown Selection

```xml
<ComboBox Width="150" ItemsSource="{Binding Countries}"
          SelectedItem="{Binding SelectedCountry}"
          DisplayMemberPath="Name" />

<!-- Editable combo box (user can type a custom value) -->
<ComboBox Width="150" IsEditable="True" ItemsSource="{Binding RecentSearches}" />
```

### Slider

```xml
<Slider Minimum="0" Maximum="100" Value="{Binding Volume}"
        TickFrequency="10" TickPlacement="BottomRight" IsSnapToTickEnabled="True" />
```

### Calendar & DatePicker

```xml
<DatePicker SelectedDate="{Binding BirthDate}" />

<Calendar SelectedDate="{Binding AppointmentDate}"
          DisplayDateStart="2020-01-01" DisplayDateEnd="2030-12-31" />
```

---

## 6. List & Data Display Controls

### ListBox — Simple Selectable List

```xml
<ListBox ItemsSource="{Binding Contacts}" SelectedItem="{Binding SelectedContact}"
          DisplayMemberPath="FullName" Height="150" />

<!-- Multi-select -->
<ListBox ItemsSource="{Binding Items}" SelectionMode="Extended" />
```

### ListView — ListBox + Column Support

```xml
<ListView ItemsSource="{Binding Contacts}" SelectedItem="{Binding SelectedContact}">
    <ListView.View>
        <GridView>
            <GridViewColumn Header="Name" DisplayMemberBinding="{Binding FullName}" Width="150" />
            <GridViewColumn Header="Email" DisplayMemberBinding="{Binding Email}" Width="200" />
            <GridViewColumn Header="Status" Width="80">
                <GridViewColumn.CellTemplate>
                    <DataTemplate>
                        <TextBlock Text="{Binding IsActive}" Foreground="Green" />
                    </DataTemplate>
                </GridViewColumn.CellTemplate>
            </GridViewColumn>
        </GridView>
    </ListView.View>
</ListView>
```

### DataGrid — Full Spreadsheet-Style Grid

```xml
<DataGrid ItemsSource="{Binding Contacts}" AutoGenerateColumns="False"
          CanUserAddRows="True" CanUserDeleteRows="True">
    <DataGrid.Columns>
        <DataGridTextColumn Header="First Name" Binding="{Binding FirstName}" Width="120" />
        <DataGridTextColumn Header="Last Name" Binding="{Binding LastName}" Width="120" />
        <DataGridCheckBoxColumn Header="Active" Binding="{Binding IsActive}" Width="60" />
        <DataGridComboBoxColumn Header="Category" Width="100"
                                 SelectedItemBinding="{Binding Category}"
                                 ItemsSource="{Binding DataContext.Categories, RelativeSource={RelativeSource AncestorType=Window}}" />
        <DataGridTemplateColumn Header="Actions" Width="80">
            <DataGridTemplateColumn.CellTemplate>
                <DataTemplate>
                    <Button Content="Delete" Command="{Binding DataContext.DeleteCommand,
                             RelativeSource={RelativeSource AncestorType=DataGrid}}"
                            CommandParameter="{Binding}" />
                </DataTemplate>
            </DataGridTemplateColumn.CellTemplate>
        </DataGridTemplateColumn>
    </DataGrid.Columns>
</DataGrid>
```

### TreeView — Hierarchical Data

```xml
<TreeView ItemsSource="{Binding RootCategories}">
    <TreeView.ItemTemplate>
        <HierarchicalDataTemplate ItemsSource="{Binding Children}">
            <TextBlock Text="{Binding Name}" />
        </HierarchicalDataTemplate>
    </TreeView.ItemTemplate>
</TreeView>
```

```csharp
public class CategoryNode
{
    public string Name { get; set; } = "";
    public ObservableCollection<CategoryNode> Children { get; set; } = new();
}
```

### ItemsControl — The Base for Custom Item Layouts

```xml
<ItemsControl ItemsSource="{Binding Products}">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <WrapPanel /> <!-- lay out items in a flowing grid instead of a vertical list -->
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
    <ItemsControl.ItemTemplate>
        <DataTemplate>
            <Border BorderBrush="Gray" BorderThickness="1" Margin="5" Padding="10" Width="120">
                <StackPanel>
                    <TextBlock Text="{Binding Name}" FontWeight="Bold" />
                    <TextBlock Text="{Binding Price, StringFormat=C}" />
                </StackPanel>
            </Border>
        </DataTemplate>
    </ItemsControl.ItemTemplate>
</ItemsControl>
```

`ItemsControl` is the most flexible list-like control — no built-in selection behavior, just item rendering — and is the base class that `ListBox`, `ListView`, and `TreeView` all build upon.

---

## 7. Menus, Toolbars & Navigation Controls

### Menu

```xml
<Menu>
    <MenuItem Header="_File">
        <MenuItem Header="_New" Command="{Binding NewCommand}" InputGestureText="Ctrl+N" />
        <MenuItem Header="_Open" Command="{Binding OpenCommand}" />
        <Separator />
        <MenuItem Header="_Exit" Command="{Binding ExitCommand}" />
    </MenuItem>
    <MenuItem Header="_Edit">
        <MenuItem Header="_Copy" Command="ApplicationCommands.Copy" />
        <MenuItem Header="_Paste" Command="ApplicationCommands.Paste" />
    </MenuItem>
</Menu>
```

### ContextMenu — Right-Click Menus

```xml
<TextBox>
    <TextBox.ContextMenu>
        <ContextMenu>
            <MenuItem Header="Clear" Command="{Binding ClearCommand}" />
        </ContextMenu>
    </TextBox.ContextMenu>
</TextBox>
```

### ToolBar

```xml
<ToolBar>
    <Button Content="New" />
    <Button Content="Open" />
    <Separator />
    <ToggleButton Content="Bold" />
    <ToggleButton Content="Italic" />
</ToolBar>
```

### StatusBar

```xml
<StatusBar>
    <StatusBarItem Content="{Binding StatusMessage}" />
    <Separator />
    <StatusBarItem HorizontalAlignment="Right" Content="{Binding ItemCount, StringFormat='{}{0} items'}" />
</StatusBar>
```

### TabControl

```xml
<TabControl>
    <TabItem Header="General">
        <StackPanel Margin="10">
            <TextBlock Text="General settings go here" />
        </StackPanel>
    </TabItem>
    <TabItem Header="Advanced">
        <StackPanel Margin="10">
            <TextBlock Text="Advanced settings go here" />
        </StackPanel>
    </TabItem>
</TabControl>
```

---

## 8. Containers: Tabs, Group Boxes & Expanders

### GroupBox

```xml
<GroupBox Header="Personal Information" Margin="10">
    <StackPanel Margin="10">
        <TextBox />
        <TextBox Margin="0,5,0,0" />
    </StackPanel>
</GroupBox>
```

### Expander — Collapsible Section

```xml
<Expander Header="Advanced Options" IsExpanded="False">
    <StackPanel Margin="10">
        <CheckBox Content="Enable verbose logging" />
        <CheckBox Content="Enable telemetry" Margin="0,5,0,0" />
    </StackPanel>
</Expander>
```

### Border — Simple Decoration Wrapper

```xml
<Border BorderBrush="Gray" BorderThickness="1" CornerRadius="6" Padding="10" Background="White">
    <TextBlock Text="Content inside a rounded, bordered box" />
</Border>
```

### ScrollViewer

```xml
<ScrollViewer VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Disabled">
    <StackPanel>
        <!-- long content that needs scrolling -->
    </StackPanel>
</ScrollViewer>
```

### GridSplitter — Resizable Panel Divider

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="200" />
        <ColumnDefinition Width="5" />
        <ColumnDefinition Width="*" />
    </Grid.ColumnDefinitions>

    <TreeView Grid.Column="0" />
    <GridSplitter Grid.Column="1" Width="5" HorizontalAlignment="Stretch" Background="LightGray" />
    <ContentControl Grid.Column="2" />
</Grid>
```

---

## 9. Dialogs & Windows

### Creating and Showing a Second Window

```xml
<!-- SettingsWindow.xaml -->
<Window x:Class="MyWpfApp.SettingsWindow"
        Title="Settings" Height="300" Width="400"
        WindowStartupLocation="CenterOwner">
    <StackPanel Margin="20">
        <CheckBox Content="Enable notifications" />
        <Button Content="Save" HorizontalAlignment="Right" Margin="0,20,0,0" Click="Save_Click" />
    </StackPanel>
</Window>
```

```csharp
// Non-modal (user can still interact with the main window)
var settingsWindow = new SettingsWindow();
settingsWindow.Show();

// Modal (blocks interaction with the owner window until closed)
var settingsWindow = new SettingsWindow { Owner = this };
settingsWindow.ShowDialog();
```

### Returning a Result from a Dialog

```csharp
public partial class ConfirmDialog : Window
{
    public ConfirmDialog()
    {
        InitializeComponent();
    }

    private void Yes_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = true; // automatically closes the window
    }

    private void No_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = false;
    }
}
```

```csharp
var dialog = new ConfirmDialog { Owner = this };
bool? result = dialog.ShowDialog();
if (result == true)
{
    // user confirmed
}
```

### Built-In Dialogs

```csharp
// Message box
MessageBoxResult result = MessageBox.Show(
    "Are you sure you want to delete this item?",
    "Confirm Delete",
    MessageBoxButton.YesNo,
    MessageBoxImage.Warning);

// Open file dialog
var openDialog = new Microsoft.Win32.OpenFileDialog
{
    Filter = "Text files (*.txt)|*.txt|All files (*.*)|*.*",
    Multiselect = false
};
if (openDialog.ShowDialog() == true)
{
    string path = openDialog.FileName;
}

// Save file dialog
var saveDialog = new Microsoft.Win32.SaveFileDialog { Filter = "JSON files (*.json)|*.json" };
if (saveDialog.ShowDialog() == true)
{
    string path = saveDialog.FileName;
}
```

---

## 10. Images, Media & Shapes

### Image

```xml
<Image Source="/Assets/logo.png" Width="100" Height="100" Stretch="Uniform" />

<!-- From an absolute path (loaded at runtime, e.g., from a config setting) -->
<Image Source="{Binding PhotoPath}" Width="150" />
```

| `Stretch` value | Behavior |
|---|---|
| `None` | Original size, may overflow or leave empty space |
| `Fill` | Stretches to fill, ignoring aspect ratio (can distort) |
| `Uniform` | Scales to fit, preserving aspect ratio (default) |
| `UniformToFill` | Scales to fill, preserving aspect ratio (may crop) |

### Shapes

```xml
<Canvas>
    <Rectangle Canvas.Left="10" Canvas.Top="10" Width="100" Height="60"
               Fill="LightBlue" Stroke="Blue" StrokeThickness="2" RadiusX="8" RadiusY="8" />

    <Ellipse Canvas.Left="150" Canvas.Top="10" Width="60" Height="60" Fill="Orange" />

    <Line X1="10" Y1="100" X2="200" Y2="100" Stroke="Black" StrokeThickness="1" />

    <Polygon Points="250,10 300,80 200,80" Fill="Green" />

    <Path Data="M 10,150 C 40,100 80,200 110,150" Stroke="Purple" StrokeThickness="2" />
</Canvas>
```

### MediaElement — Audio/Video Playback

```xml
<MediaElement Source="intro.mp4" LoadedBehavior="Manual" x:Name="Player" Width="400" Height="225" />
```

```csharp
Player.Play();
Player.Pause();
Player.Stop();
```

---

## 11. Data Binding Essentials

*(For the full deep dive on binding modes, converters, validation, and the MVVM pattern that ties this all together, see the companion MVVM guide — this section covers just enough to use the controls above effectively.)*

```xml
<TextBox Text="{Binding Name, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
<TextBlock Text="{Binding Price, StringFormat=C}" />
<TextBlock Text="{Binding CreatedAt, StringFormat='MMM dd, yyyy'}" />
<ProgressBar Value="{Binding PercentComplete}" Maximum="100" />
```

### DataContext — Where Bindings "Come From"

```csharp
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        DataContext = new MainViewModel(); // every {Binding ...} in this Window resolves against this object
    }
}
```

Child elements inherit `DataContext` from their parent unless explicitly overridden — this is why setting it once at the `Window` level makes bindings "just work" throughout the whole visual tree.

---

## 12. Resources: Styles, Brushes & Reuse

### Defining and Using a Style

```xml
<Window.Resources>
    <Style x:Key="PrimaryButtonStyle" TargetType="Button">
        <Setter Property="Background" Value="#2D7DD2" />
        <Setter Property="Foreground" Value="White" />
        <Setter Property="Padding" Value="12,6" />
        <Setter Property="FontWeight" Value="SemiBold" />
        <Setter Property="BorderThickness" Value="0" />
    </Style>
</Window.Resources>

<Button Content="Save" Style="{StaticResource PrimaryButtonStyle}" />
```

### Implicit Styles (Applied to All Controls of a Type)

```xml
<Window.Resources>
    <!-- No x:Key means this style applies automatically to EVERY TextBox in scope -->
    <Style TargetType="TextBox">
        <Setter Property="Padding" Value="6" />
        <Setter Property="BorderBrush" Value="LightGray" />
    </Style>
</Window.Resources>
```

### Style Inheritance (BasedOn)

```xml
<Style x:Key="BaseButtonStyle" TargetType="Button">
    <Setter Property="Padding" Value="10,5" />
    <Setter Property="FontSize" Value="14" />
</Style>

<Style x:Key="DangerButtonStyle" TargetType="Button" BasedOn="{StaticResource BaseButtonStyle}">
    <Setter Property="Background" Value="Crimson" />
    <Setter Property="Foreground" Value="White" />
</Style>
```

### Reusable Brushes & Colors

```xml
<Window.Resources>
    <SolidColorBrush x:Key="PrimaryBrush" Color="#2D7DD2" />
    <SolidColorBrush x:Key="DangerBrush" Color="#D2372D" />
    <sys:Double x:Key="StandardFontSize" xmlns:sys="clr-namespace:System;assembly=mscorlib">14</sys:Double>
</Window.Resources>

<Button Background="{StaticResource PrimaryBrush}" />
```

### App.xaml — Application-Wide Resources

```xml
<Application x:Class="MyWpfApp.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             StartupUri="MainWindow.xaml">
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="Themes/Colors.xaml" />
                <ResourceDictionary Source="Themes/ButtonStyles.xaml" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>
</Application>
```

Resources defined at `Application` scope are available in every Window/UserControl in the app — the standard place for a shared design system (colors, fonts, common styles).

### StaticResource vs DynamicResource

```xml
<Button Background="{StaticResource PrimaryBrush}" />  <!-- resolved once, at load time -->
<Button Background="{DynamicResource PrimaryBrush}" /> <!-- re-resolved if the resource changes at runtime -->
```

Use `DynamicResource` for things like runtime theme switching (light/dark mode toggle); use `StaticResource` everywhere else for better performance.

---

## 13. Control Templates & Custom Look-and-Feel

While **Styles** change property values (colors, fonts, padding), **ControlTemplates** replace a control's entire visual structure while keeping its behavior intact.

### Example: A Fully Custom Button Template

```xml
<Style x:Key="RoundedButtonStyle" TargetType="Button">
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="Button">
                <Border x:Name="border"
                        Background="{TemplateBinding Background}"
                        BorderBrush="{TemplateBinding BorderBrush}"
                        BorderThickness="{TemplateBinding BorderThickness}"
                        CornerRadius="20">
                    <ContentPresenter HorizontalAlignment="Center"
                                      VerticalAlignment="Center"
                                      Margin="{TemplateBinding Padding}" />
                </Border>
                <ControlTemplate.Triggers>
                    <Trigger Property="IsMouseOver" Value="True">
                        <Setter TargetName="border" Property="Background" Value="#1A5FA8" />
                    </Trigger>
                    <Trigger Property="IsPressed" Value="True">
                        <Setter TargetName="border" Property="Background" Value="#134277" />
                    </Trigger>
                    <Trigger Property="IsEnabled" Value="False">
                        <Setter TargetName="border" Property="Background" Value="Gray" />
                    </Trigger>
                </ControlTemplate.Triggers>
            </ControlTemplate>
        </Setter.Value>
    </Setter>
    <Setter Property="Background" Value="#2D7DD2" />
    <Setter Property="Foreground" Value="White" />
    <Setter Property="Padding" Value="16,8" />
    <Setter Property="BorderThickness" Value="0" />
</Style>
```

```xml
<Button Content="Rounded" Style="{StaticResource RoundedButtonStyle}" />
```

**Key concepts:**
- `TemplateBinding` pulls a value from the control's own properties (e.g., whatever `Background` was set to on the `<Button>` itself) into the template.
- `ContentPresenter` is a placeholder marking where the control's `Content` property should render — critical for keeping the control still able to display arbitrary content after re-templating.
- `ControlTemplate.Triggers` handle visual states (hover, pressed, disabled) since replacing the template also replaces the *default* visual feedback for those states.

### Why Re-template Instead of Subclassing?

Re-templating changes *appearance* while WPF's built-in behavior (click handling, keyboard navigation, accessibility) stays intact automatically — you get a custom look without reimplementing any interaction logic.

---

## 14. Data Templates

While `ControlTemplate` changes how a *control* looks, `DataTemplate` defines how a *piece of data* (a plain object with no UI of its own) should be visually rendered.

### Basic DataTemplate

```csharp
public class Product
{
    public string Name { get; set; } = "";
    public decimal Price { get; set; }
    public string ImageUrl { get; set; } = "";
}
```

```xml
<ListBox ItemsSource="{Binding Products}">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <StackPanel Orientation="Horizontal" Margin="5">
                <Image Source="{Binding ImageUrl}" Width="40" Height="40" Margin="0,0,10,0" />
                <StackPanel>
                    <TextBlock Text="{Binding Name}" FontWeight="Bold" />
                    <TextBlock Text="{Binding Price, StringFormat=C}" Foreground="Gray" />
                </StackPanel>
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

### Implicit DataTemplates (By Type, No x:Key)

```xml
<Window.Resources>
    <DataTemplate DataType="{x:Type local:Product}">
        <Border BorderBrush="LightGray" BorderThickness="1" Padding="8" Margin="4">
            <TextBlock Text="{Binding Name}" />
        </Border>
    </DataTemplate>
</Window.Resources>

<!-- Anywhere a Product object is displayed as content, this template is used automatically -->
<ContentControl Content="{Binding SelectedProduct}" />
```

This implicit-by-type mechanism is exactly what powers "ViewModel-first navigation," shown in the MVVM guide — a `ContentControl` bound to a ViewModel object automatically renders the matching View via its `DataTemplate`.

### DataTemplateSelector (Choosing a Template Programmatically)

```csharp
public class StatusTemplateSelector : DataTemplateSelector
{
    public DataTemplate? ActiveTemplate { get; set; }
    public DataTemplate? InactiveTemplate { get; set; }

    public override DataTemplate? SelectTemplate(object item, DependencyObject container)
    {
        if (item is Contact contact)
            return contact.IsActive ? ActiveTemplate : InactiveTemplate;
        return base.SelectTemplate(item, container);
    }
}
```

```xml
<ListBox.ItemTemplateSelector>
    <local:StatusTemplateSelector>
        <local:StatusTemplateSelector.ActiveTemplate>
            <DataTemplate><TextBlock Text="{Binding Name}" Foreground="Green" /></DataTemplate>
        </local:StatusTemplateSelector.ActiveTemplate>
        <local:StatusTemplateSelector.InactiveTemplate>
            <DataTemplate><TextBlock Text="{Binding Name}" Foreground="Gray" /></DataTemplate>
        </local:StatusTemplateSelector.InactiveTemplate>
    </local:StatusTemplateSelector>
</ListBox.ItemTemplateSelector>
```

---

## 15. Triggers & Visual States

### Property Triggers (Style-Level)

```xml
<Style TargetType="Border">
    <Setter Property="Background" Value="White" />
    <Style.Triggers>
        <Trigger Property="IsMouseOver" Value="True">
            <Setter Property="Background" Value="AliceBlue" />
        </Trigger>
    </Style.Triggers>
</Style>
```

### DataTrigger (Bound Value-Driven)

```xml
<Style TargetType="TextBlock">
    <Style.Triggers>
        <DataTrigger Binding="{Binding IsOverdue}" Value="True">
            <Setter Property="Foreground" Value="Red" />
            <Setter Property="FontWeight" Value="Bold" />
        </DataTrigger>
    </Style.Triggers>
</Style>
```

### MultiDataTrigger (Multiple Conditions)

```xml
<Style.Triggers>
    <MultiDataTrigger>
        <MultiDataTrigger.Conditions>
            <Condition Binding="{Binding IsActive}" Value="True" />
            <Condition Binding="{Binding IsPremium}" Value="True" />
        </MultiDataTrigger.Conditions>
        <Setter Property="Background" Value="Gold" />
    </MultiDataTrigger>
</Style.Triggers>
```

### EventTrigger (Reacting to Routed Events, Usually with Animation)

```xml
<Button Content="Click Me">
    <Button.Triggers>
        <EventTrigger RoutedEvent="Button.Click">
            <BeginStoryboard>
                <Storyboard>
                    <DoubleAnimation Storyboard.TargetProperty="Opacity"
                                     From="1" To="0.3" Duration="0:0:0.1" AutoReverse="True" />
                </Storyboard>
            </BeginStoryboard>
        </EventTrigger>
    </Button.Triggers>
</Button>
```

### VisualStateManager (More Structured State Handling — Common in Custom Controls)

```xml
<ControlTemplate TargetType="Button">
    <Border x:Name="border" Background="LightGray">
        <VisualStateManager.VisualStateGroups>
            <VisualStateGroup x:Name="CommonStates">
                <VisualState x:Name="Normal" />
                <VisualState x:Name="MouseOver">
                    <Storyboard>
                        <ColorAnimation Storyboard.TargetName="border"
                                        Storyboard.TargetProperty="Background.Color"
                                        To="LightBlue" Duration="0:0:0.2" />
                    </Storyboard>
                </VisualState>
                <VisualState x:Name="Pressed">
                    <Storyboard>
                        <ColorAnimation Storyboard.TargetName="border"
                                        Storyboard.TargetProperty="Background.Color"
                                        To="SteelBlue" Duration="0:0:0.1" />
                    </Storyboard>
                </VisualState>
            </VisualStateGroup>
        </VisualStateManager.VisualStateGroups>
        <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center" />
    </Border>
</ControlTemplate>
```

`VisualStateManager` is the more modern, more structured alternative to scattering multiple `Trigger` elements — especially valuable in custom controls with many interdependent states.

---

## 16. Animations

### Simple Property Animation

```xml
<Button Content="Animate Me">
    <Button.Triggers>
        <EventTrigger RoutedEvent="Button.Loaded">
            <BeginStoryboard>
                <Storyboard>
                    <DoubleAnimation Storyboard.TargetProperty="Opacity"
                                     From="0" To="1" Duration="0:0:0.5" />
                </Storyboard>
            </BeginStoryboard>
        </EventTrigger>
    </Button.Triggers>
</Button>
```

### Animating a Transform (Move, Scale, Rotate)

```xml
<Rectangle Width="50" Height="50" Fill="CornflowerBlue">
    <Rectangle.RenderTransform>
        <TranslateTransform x:Name="MoveTransform" />
    </Rectangle.RenderTransform>
    <Rectangle.Triggers>
        <EventTrigger RoutedEvent="Rectangle.Loaded">
            <BeginStoryboard>
                <Storyboard>
                    <DoubleAnimation Storyboard.TargetName="MoveTransform"
                                     Storyboard.TargetProperty="X"
                                     From="0" To="200" Duration="0:0:1"
                                     AutoReverse="True" RepeatBehavior="Forever" />
                </Storyboard>
            </BeginStoryboard>
        </EventTrigger>
    </Rectangle.Triggers>
</Rectangle>
```

### Easing Functions (Non-Linear Motion)

```xml
<DoubleAnimation Storyboard.TargetProperty="Opacity" From="0" To="1" Duration="0:0:0.4">
    <DoubleAnimation.EasingFunction>
        <CubicEase EasingMode="EaseOut" />
    </DoubleAnimation.EasingFunction>
</DoubleAnimation>
```

### Starting Animations from Code-Behind

```csharp
var animation = new DoubleAnimation
{
    From = 0,
    To = 1,
    Duration = TimeSpan.FromSeconds(0.5)
};
myElement.BeginAnimation(UIElement.OpacityProperty, animation);
```

---

## 17. Custom Controls & User Controls

### UserControl — Composition of Existing Controls

Best for app-specific, reusable chunks of UI (a "labeled search box," a "contact card") that aren't meant to be broadly re-templated by consumers.

```xml
<!-- LabeledTextBox.xaml -->
<UserControl x:Class="MyWpfApp.Controls.LabeledTextBox"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <StackPanel>
        <TextBlock Text="{Binding LabelText, RelativeSource={RelativeSource AncestorType=UserControl}}" />
        <TextBox Text="{Binding InputText, RelativeSource={RelativeSource AncestorType=UserControl}}" />
    </StackPanel>
</UserControl>
```

```csharp
public partial class LabeledTextBox : UserControl
{
    public static readonly DependencyProperty LabelTextProperty =
        DependencyProperty.Register(nameof(LabelText), typeof(string), typeof(LabeledTextBox));

    public static readonly DependencyProperty InputTextProperty =
        DependencyProperty.Register(nameof(InputText), typeof(string), typeof(LabeledTextBox),
            new FrameworkPropertyMetadata(default(string), FrameworkPropertyMetadataOptions.BindsTwoWayByDefault));

    public string LabelText
    {
        get => (string)GetValue(LabelTextProperty);
        set => SetValue(LabelTextProperty, value);
    }

    public string InputText
    {
        get => (string)GetValue(InputTextProperty);
        set => SetValue(InputTextProperty, value);
    }

    public LabeledTextBox() => InitializeComponent();
}
```

```xml
<local:LabeledTextBox LabelText="Email" InputText="{Binding Email}" />
```

### Custom Control — Full Re-templatable Control

Best for building a reusable, themeable widget others can re-skin entirely (like the framework's own `Button`/`ListBox`). Defined in C# with a default style in `Themes/Generic.xaml`, rather than a fixed XAML layout.

```csharp
// RatingControl.cs
public class RatingControl : Control
{
    static RatingControl()
    {
        DefaultStyleKeyProperty.OverrideMetadata(
            typeof(RatingControl),
            new FrameworkPropertyMetadata(typeof(RatingControl)));
    }

    public static readonly DependencyProperty ValueProperty =
        DependencyProperty.Register(nameof(Value), typeof(int), typeof(RatingControl),
            new FrameworkPropertyMetadata(0, FrameworkPropertyMetadataOptions.BindsTwoWayByDefault));

    public int Value
    {
        get => (int)GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }
}
```

```xml
<!-- Themes/Generic.xaml -->
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                     xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                     xmlns:local="clr-namespace:MyWpfApp">
    <Style TargetType="{x:Type local:RatingControl}">
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="{x:Type local:RatingControl}">
                    <StackPanel Orientation="Horizontal" />
                    <!-- full star-rendering logic would go here -->
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>
</ResourceDictionary>
```

```xml
<local:RatingControl Value="{Binding StarRating}" />
```

### When to Choose Which

| | UserControl | Custom Control |
|---|---|---|
| Definition | XAML + code-behind | C# class + separate default style |
| Re-templatable by consumers | No (fixed internal layout) | Yes (via `Style`/`ControlTemplate`) |
| Best for | App-specific composite views | Reusable, themeable widgets/libraries |
| Typical example | A "customer card" panel | A custom `RatingControl`, `NumericUpDown` |

---

## 18. Attached Properties & Behaviors

### What Is an Attached Property?

A property defined by one type but settable on *any* `DependencyObject` — e.g., `Grid.Row` is defined by `Grid`, but set on children like `Button` or `TextBox`, not on `Grid` itself.

```xml
<Button Grid.Row="1" Grid.Column="2" DockPanel.Dock="Top" Canvas.Left="10" />
```

### Defining Your Own Attached Property

```csharp
public static class WatermarkService
{
    public static readonly DependencyProperty WatermarkTextProperty =
        DependencyProperty.RegisterAttached(
            "WatermarkText", typeof(string), typeof(WatermarkService),
            new PropertyMetadata(string.Empty));

    public static void SetWatermarkText(DependencyObject element, string value) =>
        element.SetValue(WatermarkTextProperty, value);

    public static string GetWatermarkText(DependencyObject element) =>
        (string)element.GetValue(WatermarkTextProperty);
}
```

```xml
<TextBox local:WatermarkService.WatermarkText="Search..." />
```

Attached properties are how WPF lets any random control gain new, contextual capabilities without needing to inherit from a special base class.

### Behaviors (Microsoft.Xaml.Behaviors)

```bash
dotnet add package Microsoft.Xaml.Behaviors.Wpf
```

Behaviors package up reusable interactive logic (e.g., "invoke this command when Enter is pressed") that can be attached declaratively in XAML, without any code-behind.

```xml
<TextBox xmlns:i="http://schemas.microsoft.com/xaml/behaviors">
    <i:Interaction.Triggers>
        <i:EventTrigger EventName="KeyDown">
            <i:InvokeCommandAction Command="{Binding SearchCommand}" />
        </i:EventTrigger>
    </i:Interaction.Triggers>
</TextBox>
```

This is especially useful for wiring up events (which don't natively support `Command` binding, unlike buttons) in an MVVM-friendly, code-behind-free way.

---

## 19. Commands & Input Handling

*(The full `ICommand`/`RelayCommand` implementation is covered in depth in the companion MVVM guide — this section focuses on WPF-specific input mechanisms.)*

### RoutedCommands (Built-In, e.g., Copy/Paste/Undo)

```xml
<Menu>
    <MenuItem Header="Copy" Command="ApplicationCommands.Copy" />
    <MenuItem Header="Paste" Command="ApplicationCommands.Paste" />
</Menu>

<TextBox>
    <TextBox.InputBindings>
        <KeyBinding Command="ApplicationCommands.Save" Key="S" Modifiers="Control" />
    </TextBox.InputBindings>
</TextBox>
```

### KeyBinding — Custom Keyboard Shortcuts

```xml
<Window.InputBindings>
    <KeyBinding Command="{Binding SaveCommand}" Key="S" Modifiers="Control" />
    <KeyBinding Command="{Binding NewCommand}" Key="N" Modifiers="Control" />
</Window.InputBindings>
```

### MouseBinding

```xml
<Border>
    <Border.InputBindings>
        <MouseBinding Command="{Binding OpenCommand}" MouseAction="LeftDoubleClick" />
    </Border.InputBindings>
</Border>
```

### Routed Events — Bubbling & Tunneling

```xml
<StackPanel MouseDown="Panel_MouseDown"> <!-- can catch clicks from any child inside it -->
    <Button Content="Click" />
    <TextBlock Text="Or click here" />
</StackPanel>
```

```csharp
private void Panel_MouseDown(object sender, MouseButtonEventArgs e)
{
    // Fires even if the click originated on the TextBlock, thanks to event bubbling
    Console.WriteLine($"Clicked: {e.OriginalSource}");
}
```

WPF's routed events travel through the visual tree — **bubbling** events (like `Click`) go from the source outward to ancestors; **tunneling** events (prefixed `Preview...`, like `PreviewMouseDown`) go from the root inward to the source first.

---

## 20. Performance & Virtualization

### UI Virtualization (Critical for Large Lists)

```xml
<ListBox ItemsSource="{Binding LargeCollection}"
         VirtualizingPanel.IsVirtualizing="True"
         VirtualizingPanel.VirtualizationMode="Recycling"
         ScrollViewer.CanContentScroll="True" />
```

`ListBox`/`ListView`/`DataGrid` virtualize by default when their `ItemsPanel` is a `VirtualizingStackPanel` (the default) — only visible items are actually realized as UI elements, which is essential for lists with thousands of rows. Wrapping items in an extra `Border` or replacing the panel with a non-virtualizing one (like a plain `WrapPanel`) can silently disable this and tank performance.

### Freezing Freezable Objects (Brushes, Geometries)

```csharp
var brush = new SolidColorBrush(Colors.Blue);
if (brush.CanFreeze) brush.Freeze(); // makes it immutable, improving rendering performance and thread-safety
```

Freezing is especially valuable for brushes/geometries created in code and reused across many elements or threads.

### Avoiding Unnecessary Bindings/Converters in Hot Paths

- Prefer `x:Static` or plain literals over bindings for values that never change.
- Avoid expensive computation inside `IValueConverter.Convert` methods that run for every visible row in a large `DataGrid`.
- Use `IsAsync=True` on bindings whose source computation is slow, so the UI thread isn't blocked while the value is retrieved.

```xml
<TextBlock Text="{Binding ExpensiveComputedProperty, IsAsync=True}" />
```

### Deferred/Background Loading

```csharp
private async Task LoadLargeDatasetAsync()
{
    IsLoading = true;
    var data = await Task.Run(() => _repository.LoadAllSync()); // offload blocking work off the UI thread
    Items = new ObservableCollection<Item>(data);
    IsLoading = false;
}
```

---

## 21. Best Practices

- Choose the simplest layout panel that solves the problem — reach for `Grid` when you need real control, `StackPanel`/`DockPanel` for straightforward cases, and avoid `Canvas` outside of drawing/diagramming scenarios.
- Keep code-behind minimal; wire interaction through bindings/commands (see the MVVM guide) rather than event handlers where practical.
- Centralize shared styles/brushes/templates in merged `ResourceDictionary` files rather than duplicating them per window.
- Use implicit (type-based) styles for consistent baseline appearance, and `x:Key`-based styles for specific variants (primary button, danger button, etc.).
- Prefer re-templating (`ControlTemplate`) over building everything from scratch — you keep the built-in behavior/accessibility for free.
- Always test lists with virtualization enabled and with realistically large datasets — small hard-coded test lists can hide serious performance problems.
- Use `UserControl` for app-specific composite views, and reserve full `CustomControl` authoring for genuinely reusable, widely-restyled components.
- Favor vector content (`Path`, `Shapes`, `Viewbox`-wrapped icons) over raster images where feasible, since WPF renders vectors crisply at any DPI/scale.

---

## 22. Quick Reference

### Layout Panel Cheat Sheet

| Panel | Best for |
|---|---|
| `Grid` | Forms, precise row/column layouts, most general-purpose layouts |
| `StackPanel` | Simple linear stacks (toolbars, form field lists) |
| `DockPanel` | App shells (menu/toolbar/status bar/sidebar layout) |
| `WrapPanel` | Reflowing tag/thumbnail collections |
| `Canvas` | Absolute positioning, diagrams, drawing surfaces |
| `UniformGrid` | Evenly-sized cell grids (calculators, icon grids) |

### Control Cheat Sheet

| Need | Control |
|---|---|
| Read-only text | `TextBlock` |
| Single-line input | `TextBox` |
| Password input | `PasswordBox` |
| Formatted document | `RichTextBox` |
| Click action | `Button` |
| Toggle state | `ToggleButton`, `CheckBox` |
| Mutually exclusive options | `RadioButton` (shared `GroupName`) |
| Dropdown selection | `ComboBox` |
| Simple list | `ListBox` |
| List with columns | `ListView` + `GridView` |
| Spreadsheet-style editable grid | `DataGrid` |
| Hierarchical data | `TreeView` |
| Fully custom item layout | `ItemsControl` |
| Tabs | `TabControl` |
| Collapsible section | `Expander` |
| Grouped fields | `GroupBox` |
| Resizable split layout | `GridSplitter` |
| Image display | `Image` |
| Simple vector graphics | `Rectangle`, `Ellipse`, `Line`, `Polygon`, `Path` |
| Audio/video | `MediaElement` |

### Resource & Styling Cheat Sheet

| Concept | Purpose |
|---|---|
| `Style` | Change property values (colors, sizes, fonts) |
| `ControlTemplate` | Replace a control's entire visual structure |
| `DataTemplate` | Define how a data object (not a control) should render |
| `Trigger` / `DataTrigger` | Change appearance based on a property/bound value |
| `VisualStateManager` | Structured state-based appearance changes (esp. in custom controls) |
| `StaticResource` | Resolved once at load time (faster) |
| `DynamicResource` | Re-resolved if the underlying resource changes (needed for runtime theming) |

---

*Practice idea: build a small "task manager" app using a `DockPanel` shell (menu + status bar), a `Grid`-based main area with a `TreeView` category sidebar and a `DataGrid` task list, custom `Style`s for a consistent color palette, a `ControlTemplate`-based rounded button, and an `Expander` for task details — then add a fade-in `Storyboard` animation when a new task is added.*
