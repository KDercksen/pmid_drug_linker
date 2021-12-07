#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import pandas as pd
from tqdm import tqdm


def preprocess(text: str) -> str:
    return text.lower()


def drugs_to_pmids_mapping(
    literature: pd.DataFrame, drugs: pd.DataFrame
) -> Dict[str, List[str]]:
    drugs_to_pmids = defaultdict(list)
    for article in tqdm(literature.itertuples(), total=len(literature)):
        title = preprocess(article.title)
        abstract = preprocess(article.abstract)
        for drug_row in drugs.itertuples():
            drug = preprocess(drug_row.drug)
            if drug in title or drug in abstract:
                drugs_to_pmids[drug].append(article.pmid)
    return drugs_to_pmids


if __name__ == "__main__":
    pmids_help_str = """Excel file with PubMed IDs, titles and abstracts.
    The expected format is: column A = PMID, column B = year, column C = title,
    column D = abstract.
    """
    relevant_drugs_help_str = """Excel file with drugs and optional synonyms.
    The expected format is: column A = ID, column B = drug name. Optional:
    column C and onwards = synonyms for drug in column B
    """

    p = argparse.ArgumentParser("Link PMIDs to drugs")
    p.add_argument("--pmids", type=Path, required=True, help=pmids_help_str)
    p.add_argument(
        "--relevant-drugs", type=Path, required=True, help=relevant_drugs_help_str
    )
    p.add_argument("--output", type=Path, required=True, help="File to write results")
    args = p.parse_args()

    # Load literature sheet
    with open(args.pmids, "rb") as f:
        literature = pd.read_excel(
            f, usecols="A:D", names=["pmid", "year", "title", "abstract"], dtype=str
        ).fillna("")

    # Load drugs sheet
    with open(args.relevant_drugs, "rb") as f:
        drugs = pd.read_excel(f, names=["id", "drug"], dtype=str)

    # Map PMIDs to drugs
    drugs_to_pmids = drugs_to_pmids_mapping(literature, drugs)

    # Save to CSV file
    result = pd.DataFrame.from_records(
        [(k, ",".join(v)) for k, v in drugs_to_pmids.items() if len(v) > 0]
    )
    result.to_csv(args.output)
