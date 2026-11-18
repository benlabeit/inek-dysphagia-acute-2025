"""Verify the 128-query adult extension against the public plan and optional private log."""
import csv
from pathlib import Path

from outcomes_analyze_joint import selection_fields
from outcomes_standardization_core import read_info

PLAN = Path(__file__).with_name("adult_manual_exports.csv")
SUPPRESSED = {46, 58}
ALIASES = {"Alter": "Altersgruppe", "Hauptdiagnosen": "Hauptdiagnose",
           "weitere Prozedur": "weitere Prozeduren", "weitereProzedur": "weitere Prozeduren"}
SELECTORS = ("Alter", "Hauptdiagnosen", "Prozeduren", "Nebendiagnosen",
             "weitere Nebendiagnosen", "weitere Prozeduren", "Entlassungsgrund", "DRG")


def entries(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def audit(raw, protocol=None):
    plan = entries(PLAN)
    log = entries(protocol) if protocol else None
    if len(plan) != 128 or [int(r["Nr"]) for r in plan] != list(range(1, 129)):
        raise ValueError("Unexpected export plan")
    if log is not None and len(log) != len(plan):
        raise ValueError("Protocol length differs from plan")
    records = []
    for i, query in enumerate(plan):
        number = int(query["Nr"])
        name = query["Dateiname"]
        record = log[i] if log is not None else None
        if record is not None and any(record[k] != v for k, v in query.items()):
            raise ValueError(f"Query {number}: protocol differs from plan")
        path = raw / name
        if number in SUPPRESSED:
            if path.exists() or (record is not None and
                (record["Fallzahl laut Info"] or record["SHA-256 der Originaldatei"] or
                 "zu wenige Fälle" not in record["Meldung im InEK-DatenBrowser"] or
                 "Unterdrückt" not in record["Status"])):
                raise ValueError(f"Query {number}: suppression record differs")
            records.append(dict(query=number, status="suppressed", workbook=name, sha256=""))
            continue
        info = read_info(path)
        expected = {ALIASES.get(k, k): set(query[k].split(", ")) for k in SELECTORS if query[k]}
        fields = {ALIASES.get(k, k): v for k,v in selection_fields(info["selection"]).items() if v}
        if fields != expected or info["delivery"] != query["Lieferung"]:
            raise ValueError(f"Query {number}: workbook filters or delivery differ")
        if sum(info["distributions"]["age"][k] for k in expected["Altersgruppe"]) != info["n"]:
            raise ValueError(f"Query {number}: observed ages outside selection")
        digest = info["source"]["sha256"]
        if record is not None and (digest != record["SHA-256 der Originaldatei"] or
                                   info["n"] != int(record["Fallzahl laut Info"]) or
                                   record["Status"] != "Excel-Original geprüft"):
            raise ValueError(f"Query {number}: workbook differs from protocol")
        records.append(dict(query=number, status="verified", workbook=name, sha256=digest))
    return records
