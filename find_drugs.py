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


def process_drugs_sheet(drugs: pd.DataFrame, num_synonyms: int) -> Dict[str, List[str]]:
    # Extract drug + synonyms from the supplied sheet.
    drug_synonym_mapping = {}
    for drug_row in drugs.itertuples():
        main_name = preprocess(drug_row.drug)
        synonyms = [preprocess(drug_row[2 + i]) for i in range(num_synonyms)]
        drug_synonym_mapping[main_name] = [s for s in synonyms if s]
    return drug_synonym_mapping


def drugs_to_pmids_mapping(
    literature: pd.DataFrame, drugs: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    # Map drug names to relevant PMIDs; this takes a processed drug sheet as argument
    drugs_to_pmids = defaultdict(list)
    for article in tqdm(literature.itertuples(), total=len(literature)):
        title = preprocess(article.title)
        abstract = preprocess(article.abstract)
        for drug_name, synonyms in drugs.items():
            all_drug_names = [drug_name] + synonyms
            if any(drug in title or drug in abstract for drug in all_drug_names):
                drugs_to_pmids[drug_name].append(article.pmid)
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
    p.add_argument(
        "--num-synonyms",
        type=int,
        default=4,
        help="Number of drug synonym columns to load from drugs sheet",
    )
    args = p.parse_args()

    # Load literature sheet
    with open(args.pmids, "rb") as f:
        literature = pd.read_excel(
            f,
            usecols=range(4),
            skiprows=[0],
            names=["pmid", "year", "title", "abstract"],
            header=None,
            dtype=str,
        ).fillna("")

    # Load drugs sheet
    with open(args.relevant_drugs, "rb") as f:
        drugs = pd.read_excel(
            f,
            usecols=range(2 + args.num_synonyms),
            skiprows=[0],
            names=["id", "drug"] + [f"synonym{i}" for i in range(args.num_synonyms)],
            header=None,
            dtype=str,
        ).fillna("")

    # Process drugs sheet
    processed_drugs = process_drugs_sheet(drugs, args.num_synonyms)

    # Map PMIDs to drugs
    drugs_to_pmids = drugs_to_pmids_mapping(literature, processed_drugs)

    # Save to CSV file, skip drugs without any PMIDs
    result = pd.DataFrame.from_records(
        [(k, ",".join(v)) for k, v in drugs_to_pmids.items() if len(v) > 0]
    )
    result.to_csv(args.output)
