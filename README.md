Drugs to PMIDs linker
=====================

## Installation
Install [Python](https://www.python.org) and the required libraries:
```python
pip install pandas tqdm [pytest]
```
(or use Anaconda to do this).

## Usage
The tool has two main options, `create` and `update`.

### `create`
This command is used to create a new dataset with pmid -> drug links. Open a
command prompt and run the following command:
```python
python pmid_drug_linker.py create
    --pmids literature.xlsx
    --relevant-drugs drugs.xlsx
    --output pmid_drug_mapping.csv
```

### `update`
This command is used to generate a new dataset as well as a changelog given a
previous dataset.  Mainly useful to e.g. update a dataset with some new
literature or drugs, and having the difference in a separate file.

```python
python pmid_drug_linker.py update
    --pmids literature.xlsx
    --relevant-drugs drugs.xlsx
    --old-dataset pmid_drug_mapping.csv  # output from a previous "create" run
    --changelog-path pmid_drug_mapping_changelog.csv  # where to write difference between pmid_drug_mapping.csv and pmid_drug_mapping_new.csv
    --output pmid_drug_mapping_new.csv  # new dataset (what you would get from "create" run)
```

For more info on the arguments, run `python find_drugs.py --help`.

---

## Sheet format
Example sheets are included in the `resources` folder, these are also used for
running tests.

### `literature.xlsx`
| A | B | C | D |
| - | - | - | - |
| pmid | year | title | abstract |

Examples of fields:

| field | content |
| ----- | ------- |
| pmid | 24936338 |
| year | 2014 |
| title | Modeling the time dependent biodistribution of Samarium-153 ethylenediamine tetramethylene phosphonate using compartmental analysis |
| abstract | AIM: The main purpose of this work was to develop a pharmacokinetic model for the bone pain palliation agent Samarium-153 ethylenediamine tetramethylene phosphonate ([(153)Sm]-EDTMP) in normal rats to analyze the behavior of the complex. BACKGROUND: The use of compartmental analysis allows a mathematical separation of tissues and organs to determine the concentration of activity in each fraction of interest. Biodistribution studies are expensive and difficult to carry out in humans, but such data can be obtained easily in rodents. MATERIALS AND METHODS: We have developed a physiologically based pharmacokinetic model for scaling up activity concentration in each organ versus time. The mathematical model uses physiological parameters including organ volumes, blood flow rates, and vascular permabilities; the compartments (organs) are connected anatomically. This allows the use of scale-up techniques to predict new complex distribution in humans in each organ. RESULTS: The concentration of the radiopharmaceutical in various organs was measured at different times. The temporal behavior of biodistribution of (153)Sm-EDTMP was modeled and drawn as a function of time. CONCLUSIONS: The variation of pharmaceutical concentration in all organs is described with summation of 6-10 exponential terms and it approximates our experimental data with precision better than 2%. |

The first row in this sheet should contain column headers (e.g. "PMID", "Title"
...) and will be skipped during loading.

### `drugs.xlsx`
| A | B | C | D | E |
| - | - | - | - | - |
| id | drug | synonym 0 | synonym ... | synonym N |

Examples of fields:

| field | content |
| ----- | ------- |
| id | 0 |
| drug | midazolam |
| synonym 0 | Dormicum |
| synonym 1 | Versed |
| ... | ... |

Synonyms should be alternate names for `drug`, one per column. **The default
for maximum number of synonyms is 4, you can use `--num-synonyms N` to use less
or more**. Again, the first row in the sheet should contain column headers and
will be skipped during loading.


## Testing
Use `pytest` command to run the tests (as far as there are any :-)).
