#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pathlib import Path

from pmid_drug_linker import (
    DiffableMapping,
    csv_to_mapping,
    drugs_to_pmids_mapping,
    load_drugs_xlsx,
    load_literature_xlsx,
    preprocess,
    process_drugs_sheet,
)


class TestDiffableMapping:
    def base_mapping(self):
        base = defaultdict(list)  # type: ignore
        base.update({"drug1": ["id1", "id2", "id3"], "drug2": ["id1", "id2"]})
        return DiffableMapping(base)

    def test_self_diff(self):
        base = self.base_mapping()
        self_diff = base.difference(base)
        assert self_diff["drug1"] == [] and self_diff["drug2"] == []

    def test_addition_diff(self):
        base = self.base_mapping()
        new = DiffableMapping(defaultdict(list))
        new.mapping.update(
            {"drug1": ["id1", "id2", "id3"], "drug2": ["id1", "id2", "id3"]}
        )
        added_diff = new.difference(base)
        not_added_diff = base.difference(new)
        assert added_diff["drug1"] == [] and added_diff["drug2"] == ["id3"]
        assert not_added_diff["drug1"] == [] and not_added_diff["drug2"] == []


class TestIOFunctions:
    def setup_method(self):
        self.literature_sheet_path = Path("resources/test_literature_sheet.xlsx")
        self.drugs_sheet_path = Path("resources/test_drug_sheet.xlsx")
        self.mapping_csv_path = Path("resources/test_mapping.csv")

    def test_csv_to_mapping(self):
        a = "31587145"
        b = "32840724"
        expected = DiffableMapping(
            {
                "alfentanil": [a],
                "caffeine": [a, b],
                "gentamicin": [a],
                "ibuprofen": [a],
                "midazolam": [a, b],
                "vancomycin": [a],
                "metoprolol": [b],
                "nifedipine": [b],
                "propranolol": [b],
                "rilpivirine": [b],
                "theophylline": [b],
            }
        )
        test_map = DiffableMapping(csv_to_mapping(self.mapping_csv_path))
        assert all(x == [] for x in test_map.difference(expected).values())
        assert all(x == [] for x in expected.difference(test_map).values())

    def test_load_literature_xlsx(self):
        sheet = load_literature_xlsx(self.literature_sheet_path)
        assert sheet.shape == (5, 4)

    def test_load_drugs_xlsx(self):
        sheet = load_drugs_xlsx(self.drugs_sheet_path, 1)
        assert sheet.shape == (11, 3)
        sheet = load_drugs_xlsx(self.drugs_sheet_path, 4)
        assert sheet.shape == (11, 6)

    def test_process_drug_sheet(self):
        sheet = load_drugs_xlsx(self.drugs_sheet_path, 0)
        processed = process_drugs_sheet(sheet, 0)
        assert all(x == [] for x in processed.values())

    def test_drugs_to_pmids_mapping(self):
        expected = DiffableMapping(csv_to_mapping(self.mapping_csv_path))
        pmids = load_literature_xlsx(self.literature_sheet_path)
        drugs = load_drugs_xlsx(self.drugs_sheet_path, 0)
        processed_drugs = process_drugs_sheet(drugs, 0)
        test_map = DiffableMapping(drugs_to_pmids_mapping(pmids, processed_drugs))
        assert all(x == [] for x in test_map.difference(expected).values())
        assert all(x == [] for x in expected.difference(test_map).values())

    def test_preprocess(self):
        assert preprocess("Gentamicin ") == "gentamicin"
        assert preprocess("Gentamicin") == "gentamicin"
