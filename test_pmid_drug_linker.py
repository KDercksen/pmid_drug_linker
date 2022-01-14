#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from pmid_drug_linker import DiffableMapping


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
        assert added_diff["drug1"] == [] and added_diff["drug2"] == ["id3"]
