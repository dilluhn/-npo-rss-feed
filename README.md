# NPO Nieuwe Programma's RSS Feed

Deze tool genereert een RSS feed van nieuwe en recente programma's op NPO die je kunt gebruiken in Feedly of andere RSS readers.

## Installatie

1. Zorg ervoor dat Python 3.6+ is geïnstalleerd
2. Installeer de benodigde packages:
   ```
   pip install requests feedgen beautifulsoup4
   ```
3. Download alle bestanden in deze map

## Gebruik

### Eenmalig genereren van de RSS feed

```
python3 npo_new_programs_feed.py
```

Dit genereert een bestand `npo_new_programs.xml` dat je kunt importeren in je RSS reader.

### Starten van de RSS feed server

```
python3 serve_rss_feed.py [poort]
```

Dit start een webserver op poort 8000 (of een andere poort als je die specificeert) die de RSS feed serveert.
Je kunt deze feed toevoegen aan je RSS reader met de URL: `http://jouw-server-ip:8000/`

### Automatisch updaten van de RSS feed

```
python3 update_feed.py
```

Dit script draait continu en update de RSS feed elk uur.

## Toevoegen aan Feedly

1. Log in op je Feedly account
2. Klik op 'Add Content' of het '+' icoon
3. Kies 'Add a source by URL'
4. Voer de URL van je RSS feed in:
   - Als je de server draait: `http://jouw-server-ip:8000/`
   - Als je het XML bestand hebt geüpload naar een webserver: de URL van dat bestand
5. Klik op 'Add' om de feed toe te voegen

## Kenmerken

- Nieuwe programma's worden gemarkeerd met "NIEUW:" in de titel
- De feed wordt automatisch bijgewerkt als je de update_feed.py script gebruikt
- Als er geen programma's gevonden kunnen worden, worden er voorbeeldprogramma's getoond
