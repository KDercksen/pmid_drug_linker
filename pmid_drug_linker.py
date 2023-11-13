#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import pandas as pd
from tqdm import tqdm


class DiffableMapping:
    def __init__(self, mapping: Dict[str, List[str]]):
        # logic in the difference function only works with a defaultdict
        assert type(mapping is defaultdict)
        self.mapping = mapping

    def difference(self, other_mapping: "DiffableMapping") -> Dict[str, List[str]]:
        diff_map = defaultdict(list)
        for key, vals in self.mapping.items():
            self_vals = set(vals)
            other_vals = set(other_mapping.mapping[key])
            diff_vals = self_vals.difference(other_vals)
            diff_map[key].extend(list(diff_vals))
        return diff_map


def csv_to_mapping(path: Path) -> Dict[str, List[str]]:
    mapping = defaultdict(list)
    with open(path) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            drug, pmids = row
            pmids_list = pmids.split(",")
            mapping[drug].extend(pmids_list)
    return mapping


def mapping_to_csv(mapping: Dict[str, List[str]], output: Path):
    # Save to CSV file, skip drugs without any PMIDs
    result = pd.DataFrame.from_records(
        [(k, ",".join(v)) for k, v in mapping.items() if len(v) > 0]
    )
    result.to_csv(output, index=False, header=False)


def preprocess(text: str) -> str:
    return text.lower().strip()


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


def add_base_args(parser: argparse.ArgumentParser):
    pmids_help_str = """Excel file with PubMed IDs, titles and abstracts.
    The expected format is: column A = PMID, column B = year, column C = title,
    column D = abstract.
    """
    relevant_drugs_help_str = """Excel file with drugs and optional synonyms.
    The expected format is: column A = ID, column B = drug name. Optional:
    column C and onwards = synonyms for drug in column B
    """

    # all this stuff is needed for both create and update actions
    parser.add_argument("--pmids", type=Path, required=True, help=pmids_help_str)
    parser.add_argument(
        "--relevant-drugs", type=Path, required=True, help=relevant_drugs_help_str
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="File to write results"
    )
    parser.add_argument(
        "--num-synonyms",
        type=int,
        default=4,
        help="Number of drug synonym columns to load from drugs sheet",
    )


def make_args() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("Link PMIDs to drugs")

    # subcommands creation below
    subparsers = p.add_subparsers(title="commands", dest="command", required=True)
    # arguments for the 'create' command
    create_parser = subparsers.add_parser(  # noqa
        "create",
        description="create mapping",
    )
    add_base_args(create_parser)

    # arguments for the update command
    update_parser = subparsers.add_parser(
        "update",
        description="update existing mapping",
    )
    add_base_args(update_parser)
    update_parser.add_argument("--old-dataset", type=Path, required=True)
    update_parser.add_argument("--changelog-path", type=Path, required=True)

    return p


def load_literature_xlsx(path: Path) -> pd.DataFrame:
    return pd.read_excel(
        path,
        usecols=range(4),
        skiprows=[0],
        names=["pmid", "year", "title", "abstract"],
        header=None,
        dtype=str,
    ).fillna("")


def load_drugs_xlsx(path: Path, num_synonyms: int) -> pd.DataFrame:
    return pd.read_excel(
        path,
        usecols=range(2 + num_synonyms),
        skiprows=[0],
        names=["id", "drug"] + [f"synonym{i}" for i in range(num_synonyms)],
        header=None,
        dtype=str,
    ).fillna("")


if __name__ == "__main__":
    parser = make_args()
    args = parser.parse_args()

    # Load literature sheet
    literature = load_literature_xlsx(args.pmids)

    # Load drugs sheet and process it to a mapping
    drugs = process_drugs_sheet(
        load_drugs_xlsx(args.relevant_drugs, args.num_synonyms), args.num_synonyms
    )

    # Map PMIDs to drugs
    drugs_to_pmids = drugs_to_pmids_mapping(literature, drugs)

    # Write "create" result to csv
    mapping_to_csv(drugs_to_pmids, args.output)

    if args.command == "update":
        old_dataset = DiffableMapping(csv_to_mapping(args.old_dataset))
        diff_map = DiffableMapping(drugs_to_pmids).difference(old_dataset)
        # Write diff to changelog path
        mapping_to_csv(diff_map, args.changelog_path)
