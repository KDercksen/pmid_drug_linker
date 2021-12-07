Drugs to PMIDs linker
=====================

## Installation
Install [Python](https://www.python.org) and the required libraries:
```python
pip install pandas tqdm
```
(or use Anaconda to do this).

## Usage
Open a command prompt and run the following command:
```python
python find_drugs.py
    --pmids literature.xlsx
    --relevant-drugs drugs.xlsx
    --output pmid_drug_mapping.csv
```

For more info on the arguments, run `python find_drugs.py --help`.

## Sheet format
### `literature.xlsx`
| A | B | C | D |
| - | - | - | - |
| pmid | year | title | abstract |

### `drugs.xlsx`
| A | B |
| - | - |
| id | drug |

Synonyms will also be included in this file, still determining what the
formatting should be.
