# Python Object-Oriented Programming (OOP) Guide

## 1. What is Object-Oriented Programming (OOP)?
Object-Oriented Programming is a programming paradigm where you organize code using objects, which combine **data** (attributes) and **behavior** (methods).

### Key Concepts in OOP:
- **Class**: A blueprint for creating objects. Defines attributes (data) and methods (behavior).
- **Object**: An instance of a class. It represents a specific realization of the class.
- **Encapsulation**: Combining data and methods into a single unit (class).
- **Inheritance**: Allowing a class to inherit attributes and methods from another class.
- **Polymorphism**: Using a common interface for different types of data.
- **Abstraction**: Hiding implementation details and showing only the essential features.

---

## 2. Creating Classes and Objects
### Example:
```python
# Define a class
class Car:
    # Constructor: initializes an object
    def __init__(self, brand, color):
        self.brand = brand  # Attribute
        self.color = color  # Attribute

    # Method: defines behavior
    def drive(self):
        print(f"The {self.color} {self.brand} is driving!")

# Create objects (instances of the class)
car1 = Car("Toyota", "red")
car2 = Car("Honda", "blue")

# Access attributes and call methods
print(car1.brand)  # Output: Toyota
car1.drive()       # Output: The red Toyota is driving!
car2.drive()       # Output: The blue Honda is driving!
```

---

## 3. Understanding the Parts of a Class

### **Attributes**:
- Variables that hold data about the object.
- Defined inside the `__init__` method or class.

### **Methods**:
- Functions defined in a class that describe its behavior.
- Take `self` as the first parameter to refer to the object itself.

### **Constructor (`__init__` method)**:
- A special method called when creating an object.
- Used to initialize attributes.

---

## 4. Encapsulation
Encapsulation restricts direct access to attributes and allows controlled access via methods.

### Example:
```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance  # Private attribute

    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount > self.__balance:
            print("Insufficient funds!")
        else:
            self.__balance -= amount

    def get_balance(self):
        return self.__balance

# Usage
account = BankAccount("Alice", 1000)
account.deposit(500)
account.withdraw(200)
print(account.get_balance())  # Output: 1300
```

Here, `__balance` is private and cannot be accessed directly outside the class. Use `get_balance` for controlled access.

---

## 5. Inheritance
Inheritance allows one class (child) to inherit attributes and methods from another (parent).

### Example:
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass  # Placeholder for child classes

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

# Create objects
dog = Dog("Buddy")
cat = Cat("Kitty")
print(dog.speak())  # Output: Buddy says Woof!
print(cat.speak())  # Output: Kitty says Meow!
```

---

## 6. Polymorphism
Different classes can define methods with the same name, and Python will determine the correct method to call based on the object type.

### Example:
```python
animals = [Dog("Buddy"), Cat("Kitty")]

for animal in animals:
    print(animal.speak())
```

Output:
```
Buddy says Woof!
Kitty says Meow!
```

---

## 7. Abstraction
Abstraction hides unnecessary details and provides a simple interface using abstract classes.

### Example with `abc` module:
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

# dog = Animal()  # Error: Can't instantiate abstract class
dog = Dog()
print(dog.speak())  # Output: Woof!
```

---

## 8. Putting It All Together
Here’s a complete example demonstrating multiple concepts:
```python
class Vehicle:
    def __init__(self, brand, color):
        self.brand = brand
        self.color = color

    def describe(self):
        return f"This is a {self.color} {self.brand}."

class Car(Vehicle):
    def __init__(self, brand, color, doors):
        super().__init__(brand, color)
        self.doors = doors

    def describe(self):
        return f"This is a {self.color} {self.brand} with {self.doors} doors."

class Motorcycle(Vehicle):
    def describe(self):
        return f"This is a {self.color} {self.brand} motorcycle."

# Create objects
car = Car("Toyota", "red", 4)
motorcycle = Motorcycle("Harley", "black")

# Polymorphism
vehicles = [car, motorcycle]
for vehicle in vehicles:
    print(vehicle.describe())
```

Output:
```
This is a red Toyota with 4 doors.
This is a black Harley motorcycle.
```

---

## 9. Advanced OOP Concepts

### a. Multiple Inheritance
A class can inherit from more than one parent class.

```python
class Flyer:
    def fly(self):
        print("I can fly!")

class Swimmer:
    def swim(self):
        print("I can swim!")

class Duck(Flyer, Swimmer):
    pass

duck = Duck()
duck.fly()   # Output: I can fly!
duck.swim()  # Output: I can swim!
```

---

### b. Operator Overloading
You can define how operators (e.g., `+`, `-`, `*`) behave for your custom classes by overriding special methods (dunder methods).

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(2, 3)
p2 = Point(4, 5)
p3 = p1 + p2  # Uses __add__()
print(p3)     # Output: Point(6, 8)
```

---

### c. Property Decorators
Control access to attributes using `@property`.

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

    @property
    def perimeter(self):
        return 2 * (self.width + self.height)

rect = Rectangle(4, 5)
print(rect.area)       # Output: 20
print(rect.perimeter)  # Output: 18
```

---

## 10. Design Patterns

### a. Singleton Pattern
Ensure only one instance of a class exists.

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # Output: True
```

---

### b. Factory Pattern
A method or class responsible for creating objects without exposing the instantiation logic.

```python
class Shape:
    def draw(self):
        pass

class Circle(Shape):
    def draw(self):
        print("Drawing a Circle")

class Square(Shape):
    def draw(self):
        print("Drawing a Square")

class ShapeFactory:
    @staticmethod
    def get_shape(shape_type):
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
        else:
            return None

shape = ShapeFactory.get_shape("circle")
shape.draw()  # Output: Drawing a Circle
```

---

## 11. Best Practices in OOP

1. **Follow the DRY Principle**:
   - Don't Repeat Yourself. Use inheritance or composition to avoid redundant code.
   
2. **Use Composition Over Inheritance**:
   - Instead of always inheriting, consider using objects as attributes.

   ```python
   class Engine:
       def start(self):
           print("Engine started.")

   class Car:
       def __init__(self):
           self.engine = Engine()

       def drive(self):
           self.engine.start()
           print("Car is driving.")

   car = Car()
   car.drive()
   ```

3. **Encapsulate Attributes**:
   - Use private attributes (`__attribute`) and provide getters/setters.

4. **Use Meaningful Names**:
   - Name classes, methods, and attributes clearly.

5. **Avoid Overcomplicating**:
   - Design simple and reusable classes.

---

## 12. Practical Exercise

### Goal: Build a Library Management System

#### Requirements:
1. A `Book` class with attributes: `title`, `author`, `year`, `is_checked_out`.
2. A `Library` class that can:
   - Add books.
   - List all books.
   - Check out a book.
   - Return a book.

### Try implementing it or let me know if you'd like guidance!