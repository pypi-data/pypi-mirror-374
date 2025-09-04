# UTILITIES de Muerte

A small suite of Python utilities by **MuerteSeguraZ**, including:

* **Base Conversion**
* **Magnet Sorting**
* **Data Analyzer**

This project includes a simple **batch menu** for running demos of each utility.

---

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Utilities](#utilities)

  * [Base Conversion](#base-conversion)
  * [Magnet Sorting](#magnet-sorting)
  * [Data Analyzer](#data-analyzer)
* [Examples](#examples)
* [Credits](#credits)

---

## Installation

1. Make sure Python is installed (tested on Python 3.10+).
2. Clone or download the repository.
3. Keep all files in the same folder (`schooltools` folder recommended).
4. Run the menu:

```bat
menu.bat
```

---

## Usage

When you run `menu.bat`, you will see:

```
###################
#    UTILITIES    #
#    de Muerte    #
###################

What do you wanna test?
(1 = base conversion, 2 = magnet sorting, 3 = exit / type exit, 4 = data analyzer, crd = creador)
Type here:
```

Type the number corresponding to the tool you want to test.

---

## Utilities

### **1. Base Conversion**

Convert numbers or strings to various formats:

* Binary (`bin`)
* Hexadecimal (`hex`)
* Octal (`oct`)
* ASCII codes (`ascii`)
* Base64 (`base64`)
* Reversed binary (`revbin`)
* Unicode code point (`ord`) / character (`chr`)

#### Example

```python
from schooltools import base_converter_

def convert():
    print("bin:", base_converter_("bin")([5, "hi", 255]))
    # ['101', '1101000', '1101001', '11111111']

    print("hex:", base_converter_("hex")([10, "AB", 255]))
    # ['a', '41', '42', 'ff']
```

---

### **2. Magnet Sorting**

A custom sorting algorithm that simultaneously moves the **minimum** to the left and **maximum** to the right.

#### Example

```python
from schooltools import magnet_sort

a = 1 + 1
b = 2 + 2
c = 3 + 3
d = 5 + 3

print(magnet_sort([a, d, b, c]))
```

---

### **3. Data Analyzer**

Analyze a list of numbers with full statistics and a histogram:

* Count, sum, min, max, range
* Mean, median, mode
* Variance and standard deviation
* 25th, 50th, 75th percentiles
* Horizontal histogram

#### Example

```python
from schooltools import data_analyzer

data = [5, 3, 8, 3, 9, 5, 1, 3]
print(data_analyzer(data))
```

**Sample Output:**

```
numbers: [1, 3, 3, 3, 5, 5, 8, 9]

count: 8
sum: 37
min: 1
max: 9
range: 8
mean: 4.625
median: 4.0
mode: 3
variance: 6.484375
std_dev: 2.54644359843292
25th percentile: 3.0
50th percentile: 4.0
75th percentile: 5.75
histogram:
  1 | █████████████ (1)
  3 | ████████████████████████████████████████ (3)
  5 | ██████████████████████████ (2)
  8 | █████████████ (1)
  9 | █████████████ (1)
```

---

## Batch Menu Example

```
###################
#    UTILITIES    #
#    de Muerte    #
###################

What do you wanna test?
(1 = base conversion, 2 = magnet sorting, 3 = exit / type exit, 4 = data analyzer, crd = creador)
Type here: 4
Running Data Analyzer demo...
(numbers and stats printed)
Press any key to continue . . .
```

* Options `1`-`4` run the corresponding demo.
* Type `exit` or `3` to quit.
* Type `crd` to see the creator info.

---

## Credits

**Created by:** MuerteSeguraZ
For educational and personal projects.

---
