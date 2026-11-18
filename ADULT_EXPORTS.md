# Manuelle InEK-Exporte für die Erwachsenenanalysen

[Filter und Dateinamen für jede Abfrage](adult_manual_exports.csv) · [InEK-Datenlieferung 2025](https://datenbrowser.inek.org/DRG202601)

## Erste zwei Exporte

Die CSV enthält die konkreten Selektionswerte. Für die ersten zwei Zeilen die Lieferung **Unterjährige Datenlieferung DRG Januar bis Dezember 2025** wählen, im Feld **Prozeduren** die angegebenen 16 Schlaganfall-OPS gemeinsam auswählen, unter **Altersgruppe** alle sieben Kategorien von 18–29 bis 65–74 Jahre auswählen und unter **weitere Nebendiagnosen** J96.00 setzen. Hauptdiagnose und Entlassungsgrund bleiben frei.

1. Im Feld **Nebendiagnosen** die Auswahl leer lassen. Daten anzeigen, Excel herunterladen und unter dem in Zeile 1 angegebenen Namen speichern.
2. Für die zweite Abfrage im Feld **Nebendiagnosen** R13.0, R13.1 und R13.9 gemeinsam auswählen. Alle anderen Einstellungen bleiben gleich. Den zweiten Export unter dem Namen aus Zeile 2 speichern.

Jeder Export muss im Blatt *Info* die richtige Lieferung, Altersauswahl und Filterkombination ausweisen. Bei nicht angezeigten Ergebnissen den Status „unterdrückt“ bzw. die genaue Bildschirmmeldung festhalten. Eine fehlende Angabe ist kein beobachteter Nullwert. Die Quelle enthält aggregierte Krankenhausfälle. Originaldateien verbleiben im privaten Projektbereich.

## Welche Abfragen fehlen

| Abfragenummer | Zweck | Umfang |
| --- | --- | --- |
| 1–108 | Fehlende Ereignistabellen für Modelle 2 und 3 bei neun Endpunkten | Zwei Altersgruppen × drei Hauptdiagnose-Auswahlen × zwei Quellgruppen je Endpunkt. Die personenbezogenen Merkmale Geschlecht und PCCL werden getrennt aus den Info-Verteilungen ausgewertet. |
| 109–120 | E43-Originaldateien für die zusätzlichen DRG-Analysen wiederbeschaffen | Zuerst das vorhandene Projektarchiv oder frühere Downloads prüfen. Die überprüften Erwachsenen-Schätzer für Modell 2 und 3 liegen bereits vor. Die ersten vier Dateien dieser Gruppe reichen für die einfachere Alters-DRG-Auswertung, die weiteren acht ergänzen die Hauptdiagnose. |
| 121–128 | Machbarkeit von Modell 4 für Mortalität innerhalb der häufigen DRG B70D prüfen | Vier Nenner- und vier Todesfallabfragen. Jede Altersgruppe und Quellgruppe ist einzeln ausgewählt. Die Geschlechtsverteilung des Info-Blatts muss für den jeweiligen Nenner bzw. Endpunkt eindeutig zuordenbar sein. |

Der B70D-Pilot ist eine Machbarkeitsprüfung für eine einzelne DRG. Eine populationsübergreifende Schätzung für Modell 4 setzt entsprechend gekreuzte Nenner und Ereigniszahlen in weiteren beobachtbaren Alters-DRG-Strata voraus. Die 108 Abfragen allein liefern keine gemeinsame Verteilung von DRG und Geschlecht. Bei einer Bereitstellung durch InEK wäre eine aggregierte Tabelle nach Altersgruppe, Geschlecht, DRG, Dysphagiegruppe und Endpunkt der direkte Weg. Für die Verweildauer werden je Zelle zusätzlich die Summe der Aufenthaltstage und der quadrierten Aufenthaltstage oder äquivalente Mittelwerte und Standardabweichungen benötigt. Für die anderen Verweildauermodelle werden analoge Zellen nach Alter, Hauptdiagnose und Geschlecht bzw. PCCL benötigt. Ein reiner Häufigkeitsexport nach Geschlecht oder PCCL liefert diese Aufenthaltsdauern nicht.
