
# Column Type Detector

A simple Python utility to detect the data types of columns in a delimited file using DuckDB and Pandas.

##  Overview

This tool loads a delimited file into an in-memory DuckDB database treating all columns as VARCHAR.  
It analyzes each column to detect data types: int, float, double, str, or null, and outputs a summary table.

##  Requirements

- Python >=3.12.3+
- duckdb >=1.3.2
- pandas >=2.1.4


##  Installation

```bash
pip install duckdb>=1.3.2 pandas>=2.1.4
```


###  Example CLI Wrapper

```
from columnTypeDetector import load_data_as_varchar, get_column_names, detect_column_types

con = load_data_as_varchar('/content/sample_data/All_Customers.csv',',')

get_column_names(con,"raw_data")

detect_column_types(con,"raw_data")

```

##  Sample Output

Here is an example output of the type detection:

| col             | float | int  | null | str  | double | total |
|-----------------|-------|------|------|------|--------|-------|
| Address1        | 0     | 3    | 0    | 2496 | 0      | 2499  |
| Address2        | 0     | 0    | 2499 | 0    | 0      | 2499  |
| Address3        | 0     | 0    | 2499 | 0    | 0      | 2499  |
| City           | 0     | 0    | 7    | 2492 | 0      | 2499  |
| City2          | 0     | 0    | 2495 | 4    | 0      | 2499  |
| Company       | 1     | 0    | 0    | 2498 | 0      | 2499  |
| Country       | 0     | 0    | 58   | 2441 | 0      | 2499  |
| CreateDate    | 0     | 0    | 0    | 2499 | 0      | 2499  |
| Currency      | 0     | 81   | 0    | 2418 | 0      | 2499  |
| CustomerID    | 0     | 2495 | 0    | 4    | 0      | 2499  |
| CustomerTier  | 0     | 457  | 171  | 1871 | 0      | 2499  |
| Firstname     | 0     | 0    | 0    | 2499 | 0      | 2499  |
| Lastname      | 0     | 0    | 0    | 2499 | 0      | 2499  |
| MiscDate      | 0     | 0    | 0    | 2499 | 0      | 2499  |
| OrderAmount   | 0     | 2498 | 0    | 1    | 0      | 2499  |
| PrefDelivMethod | 0   | 0    | 0    | 2499 | 0      | 2499  |
| State         | 0     | 107  | 0    | 2392 | 0      | 2499  |
| Status       | 0     | 0    | 0    | 2499 | 0      | 2499  |
| Zip          | 0     | 2410 | 0    | 89   | 0      | 2499  |



##  License

Copyright 2025 Vikas Bhaskar Vooradi

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

