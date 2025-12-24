# Class Introduction
---

**Below code gives an overview of methods, properties, getter, setter, deleter, attributes and instance**

```python
class SMU:
    class_type = 'alpha'  # class attribute

    def __init__(self, resource_name):
        self._resource_name = resource_name

    @property
    def resource_name(self):
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value):
        if not isinstance(value, str):
            raise ValueError("resource name must be of string type")
        self._resource_name = value

    @resource_name.getter
    def resource_name(self):
        return self._resource_name

    @resource_name.deleter
    def resource_name(self):
        print('deleting resource name from the object instance')
        del self._resource_name

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    @classmethod
    def get_class_type(cls):
        return cls.class_type

    @staticmethod
    def get_all_supply_resources():
        return ["dev1", "dev2"]

    def initialize(self):
        print(f'initializing {self.resource_name}')

    def set_voltage(self, volt):
        """
        Sets the voltage.

        Parameters:
        volt (float): The voltage value to set.

        Returns:
        None
        """
        print(f'setting {volt}V to {self.resource_name}')

    def close(self):
        print(f'closing session for {self.resource_name}')


my_smu = SMU('Dev1')
print(my_smu.get_all_supply_resources())  # ["dev1", "dev2"]
print(SMU.get_all_supply_resources())  # ["dev1", "dev2"]
print(SMU.get_class_name())  # SMU
my_smu.initialize()  # initializing Dev1
my_smu.set_voltage(5)  # setting 5V to Dev1
print(my_smu.resource_name)  # Dev1
del my_smu.resource_name  # deleting resource name from the object instance
print(my_smu.resource_name) # reports error since the object instance attribute is deleted in the previous step
my_smu.close()

```

# Inheritance example
---
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