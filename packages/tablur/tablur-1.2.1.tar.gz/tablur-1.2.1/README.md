# tablur

<div align="center">
  <img src="./logo.png" width="400" />
</div>

a simple python library for creating beautifully formatted tables with box-drawing characters.

## features

- **simple interface**: use `tablur()` and `simple()` functions
- create tables with box-drawing characters (╭─╮│├┼┤┴╰)
- support for optional headers and footers
- automatic column width calculation
- three input formats: column-based, dictionary, and row-based
- returns formatted strings (no automatic printing)
- lightweight and blazingly fast

## installation

```bash
pip install tablur
```

## usage

### column-based format (default)

```python
from tablur import tablur

# data is defined as a list of tuples where each tuple contains `(column_name, column_data)`
data = [
    ("Name", ["Alice", "Bob", "Charlie"]),
    ("Age", [25, 30, 35]),
    ("City", ["New York", "London", "Tokyo"]),
    ("Salary", [50000, 60000, 70000]),
]

# using the `tablur` function
table = tablur(
    data,
    header="Employee Directory",
    footer="Total: 3 employees",
    chars=["╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼", "─", "│"] # this is the default, make sure you use this format
)
print(table)
```

output:

```
╭───────────────────────────────────╮
│        Employee Directory         │
├─────────┬─────┬──────────┬────────┤
│ Name    │ Age │ City     │ Salary │
├─────────┼─────┼──────────┼────────┤
│ Alice   │ 25  │ New York │ 50000  │
│ Bob     │ 30  │ London   │ 60000  │
│ Charlie │ 35  │ Tokyo    │ 70000  │
├─────────┴─────┴──────────┴────────┤
│        Total: 3 employees         │
╰───────────────────────────────────╯
```

### dictionary format

```python
from tablur import tablur

# data can also be a dictionary where keys are column names and values are lists of data
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Tokyo"],
    "Salary": [50000, 60000, 70000],
}

# using the `tablur` function with dictionary
table = tablur(
    data,
    header="Employee Directory",
    footer="Total: 3 employees"
)
print(table)
```

output:

```
╭───────────────────────────────────╮
│        Employee Directory         │
├─────────┬─────┬──────────┬────────┤
│ Name    │ Age │ City     │ Salary │
├─────────┼─────┼──────────┼────────┤
│ Alice   │ 25  │ New York │ 50000  │
│ Bob     │ 30  │ London   │ 60000  │
│ Charlie │ 35  │ Tokyo    │ 70000  │
├─────────┴─────┴──────────┴────────┤
│        Total: 3 employees         │
╰───────────────────────────────────╯
```

### row-based format

```python
from tablur import simple

# data is just a list of rows, where each row is a list of values
data = [
    ["Alice", 25, "New York"],
    ["Bob", 30, "London"],
    ["Charlie", 35, "Tokyo"]
]

# with simple, you can define the headers explicitly or not (they default to indices)
table = simple(data, headers=["Name", "Age", "City"])
print(table)
```

> [!NOTE]
> The `simple()` function also supports dictionary format, just like `tablur()`.

output:

```
╭─────────┬─────┬──────────╮
│ Name    │ Age │ City     │
├─────────┼─────┼──────────┤
│ Alice   │ 25  │ New York │
│ Bob     │ 30  │ London   │
│ Charlie │ 35  │ Tokyo    │
╰─────────┴─────┴──────────╯
```

## license

mit, you can do whatever you want with the code :D
