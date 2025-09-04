# Typhe

[![PyPI version](https://img.shields.io/pypi/v/typhe.svg)](https://pypi.org/project/typhe/)
[![Python Version](https://img.shields.io/pypi/pyversions/typhe.svg)](https://pypi.org/project/typhe/)
[![License](https://img.shields.io/pypi/l/typhe.svg)](https://pypi.org/project/typhe/)

Typhe is a lightweight Python library that extends Python's type system with **additional integer and string types**, as well as structures (`struct`) to make your code safer and more explicit.

---

## 🔹 Supported Types

- **char**  
- **sint8**  
- **uint8**  
- **sint16**  
- **uint16**  
- **uint32**  
- **sint32**  
- **uint64**  
- **sint64**  
- **struct**

### ⚡ Additional Types

- **mint** – Limited integer type  
- **mstr** – Limited string type  

---

## 📦 Requirements

- Python >= 3.8  
- setuptools >= 42  
- wheel  

---

## ⚙️ Installation

Install Typhe via pip:

```bash
pip install typhe
```

---

## 💡 Usage Example

```python
from typhe import uint8, struct

class Calculator(struct):
    def __init__(self):
        super().__init__({
            "operator": str,
            "number1": uint8,
            "number2": uint8
        })

calculator = Calculator()
calculator(
    operator="+",
    number1=uint8(5),
    number2=uint8(10)
)

print(calculator.number1)  # Output: 5
```

---

## 🤝 Contributing

Contributions are welcome!
Please fork the repository, make your changes, and submit a pull request.

---

## 📝 License

Typhe is licensed under the GPL3 License.
See the [LICENSE](LICENSE) file for details.