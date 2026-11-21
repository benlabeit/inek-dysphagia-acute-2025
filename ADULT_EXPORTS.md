# Manuelle InEK-Exporte für die Erwachsenenanalysen

[Filter und Dateinamen für jede Abfrage](adult_manual_exports.csv) · [InEK-Datenlieferung 2025](https://datenbrowser.inek.org/DRG202601)

## Abgeschlossene Lieferung

Alle 128 geplanten Abfragen haben einen dokumentierten Endstatus. Die 126 verfügbaren Originale sind anhand der Filter im Info-Blatt, der Erwachsenen-Altersgruppen, der Fallzahlen und der Prüfsummen verifiziert. Für Nr. 46 (E44.0) und Nr. 58 (E44.1), jeweils Alter 18–74 Jahre, I61 und Dysphagie, unterdrückte InEK die Ausgabe. Beide Fallzahlen bleiben leer. Alle acht B70D-Abfragen konnten für den Mortalitätsvergleich ausgewertet werden. Das [Prüfprotokoll ohne Fallzahlen](adult_export_audit.csv) enthält den Status je Abfrage.

## Ablage für die Reproduktion

Die 126 XLSX-Dateien unter ihren unveränderten Namen zusammen mit den früheren Originalexporten in demselben privaten lokalen Ordner ablegen. Diesen Ordner bei `adult_analysis.py --raw` angeben. Die private `Exportprotokoll.csv` kann im selben Ordner oder separat liegen. Mit `--protocol /pfad/Exportprotokoll.csv` werden Fallzahlen und Originalprüfsummen zusätzlich gegen das Lieferprotokoll geprüft.

## Beispiel für die ersten zwei Abfragen

Die CSV enthält die konkreten Selektionswerte. Für die ersten zwei Zeilen die Lieferung **Unterjährige Datenlieferung DRG Januar bis Dezember 2025** wählen, im Feld **Prozeduren** die angegebenen 16 Schlaganfall-OPS gemeinsam auswählen, unter **Altersgruppe** alle sieben Kategorien von 18–29 bis 65–74 Jahre auswählen und unter **weitere Nebendiagnosen** J96.00 setzen. Hauptdiagnose und Entlassungsgrund bleiben frei.

1. Im Feld **Nebendiagnosen** die Auswahl leer lassen. Daten anzeigen, Excel herunterladen und unter dem in Zeile 1 angegebenen Namen speichern.
2. Für die zweite Abfrage im Feld **Nebendiagnosen** R13.0, R13.1 und R13.9 gemeinsam auswählen. Alle anderen Einstellungen bleiben gleich. Den zweiten Export unter dem Namen aus Zeile 2 speichern.

Jeder Export muss im Blatt *Info* die richtige Lieferung, Altersauswahl und Filterkombination ausweisen. Bei nicht angezeigten Ergebnissen den Status „unterdrückt“ bzw. die genaue Bildschirmmeldung festhalten. Eine fehlende Angabe ist kein beobachteter Nullwert. Die Quelle enthält aggregierte Krankenhausfälle. Originaldateien verbleiben im privaten Projektbereich.

## Zusammensetzung des abgeschlossenen Abfrageplans

| Abfragenummer | Zweck | Umfang |
| --- | --- | --- |
| 1–108 | Ergänzte Ereignistabellen für Modelle 2 und 3 bei neun Endpunkten | Zwei Altersgruppen × drei Hauptdiagnose-Auswahlen × zwei Quellgruppen je Endpunkt. Die personenbezogenen Merkmale Geschlecht und PCCL werden getrennt aus den Info-Verteilungen ausgewertet. |
| 109–120 | E43-Originaldateien für die zusätzlichen DRG-Analysen wiederbeschaffen | Alle zwölf Originale wurden in dieser Lieferung geprüft. Die ersten vier Dateien dieser Gruppe reichen für die einfachere Alters-DRG-Auswertung, die weiteren acht ergänzen die Hauptdiagnose. |
| 121–128 | Sensitivitätsanalyse für Mortalität innerhalb der DRG B70D nach Alter und Geschlecht | Vier Nenner- und vier Todesfallabfragen. Jede Altersgruppe und Quellgruppe ist einzeln ausgewählt. Die Geschlechtsverteilung des Info-Blatts ist für den jeweiligen Nenner bzw. Endpunkt eindeutig zuordenbar. |

Modell 4 im Manuskript standardisiert für Altersgruppe und DRG und ist für alle 20 binären Endpunkte verfügbar (Ergebnisschlüssel `age_drg`). Die zusätzliche B70D-Sensitivitätsanalyse nach Alter und Geschlecht ergab für die Mortalität ein RR von 8,04 (95%-KI 7,27–8,89). Die Entlassungsabfragen unten ermöglichen diese Sensitivitätsanalyse für die vier Entlassziele. Eine zusätzliche Geschlechtsadjustierung über mehrere DRGs hinweg würde geschlechtsspezifische Nenner und Ereigniszahlen in den jeweiligen Alters-DRG-Strata voraussetzen. Die 108 Abfragen allein liefern keine gemeinsame Verteilung von DRG und Geschlecht. Bei einer Bereitstellung durch InEK wäre eine aggregierte Tabelle nach Altersgruppe, Geschlecht, DRG, Dysphagiegruppe und Endpunkt der direkte Weg. Für die Verweildauer werden je Zelle zusätzlich die Summe der Aufenthaltstage und der quadrierten Aufenthaltstage oder äquivalente Mittelwerte und Standardabweichungen benötigt. Für die anderen Verweildauermodelle werden analoge Zellen nach Alter, Hauptdiagnose und Geschlecht bzw. PCCL benötigt. Ein reiner Häufigkeitsexport nach Geschlecht oder PCCL liefert diese Aufenthaltsdauern nicht.

## Ergänzung für die Entlassungsziele im Akutmanuskript

Der separate Plan umfasst 64 Abfragen. Alle 40 Kernabfragen, sechs der acht zusätzlichen Hauptdiagnose-Abfragen und alle 16 B70D-Abfragen ergaben prüfbare Originaldateien. Die Abfragen 45 und 46 im Entlassungsplan wurden bei Hospizentlassung, Alter 18–74 Jahre und Hauptdiagnose I61 unterdrückt. Die Fallzahlen bleiben unbekannt. Betroffen ist die feinere Sensitivitätsanalyse für Hospiz mit sechs Alters-Hauptdiagnose-Gruppen. Die fünf gemeinsamen Gruppen tragen alle vier Endpunkte. [Entlassungsplan](InEK_Akut_Entlassungsziele_Exportplan.xlsx) · [Prüfprotokoll](adult_discharge_export_audit.csv)

Die 62 nativen Excel-Dateien unter den Namen aus dem Entlassungsplan in denselben privaten Ordner wie die Nenner- und Mortalitätsdateien legen. Das private XLSX-Exportprotokoll kann getrennt gespeichert werden. Den Pfad mit `adult_discharge.py --protocol` übergeben. Nenner für die Zielortanalysen sind die jeweils lebend entlassenen Erwachsenenfälle. Die gemeinsam abgefragten Schlüssel 06, 08 und 13 bezeichnen externe Krankenhausverlegungen. [Reproduktion und Ergebnisse](README.md#discharge-status-and-destination)
