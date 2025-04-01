#!/usr/bin/env python3
"""
NPO New Programs RSS Feed Generator

This script creates an RSS feed of recent and new programs on NPO by scraping
the NPO website and generating a static RSS feed file.
"""

import os
import json
import time
import datetime
from datetime import timezone
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
NPO_URL = "https://npo.nl/"
NPO_START_URL = "https://npo.nl/start"
RSS_FEED_FILE = "npo_new_programs.xml"
CACHE_FILE = "npo_programs_cache.json"
CACHE_EXPIRY = 3600  # 1 hour in seconds

def get_programs_from_website():
    """Get programs from the NPO website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(NPO_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        programs = []
        
        logger.info("Scraping NPO homepage for programs...")
        
        # Find all links that might be program links
        for element in soup.find_all('a'):
            if not element.get('href'):
                continue
                
            # Skip navigation links and external links
            if element.get('href').startswith('#') or element.get('href').startswith('http'):
                continue
                
            # Try to find title
            title_element = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if not title_element:
                continue
                
            title = title_element.text.strip()
            if not title or len(title) < 3:
                continue
                
            link = element.get('href')
            if link and not link.startswith('http'):
                link = f"{NPO_URL.rstrip('/')}{link}"
                
            # Extract description if available
            description = ""
            desc_element = element.find(class_=lambda c: c and any(word in c.lower() for word in ['desc', 'summary', 'text']))
            if desc_element:
                description = desc_element.text.strip()
                
            # Check if it contains "Nieuw" text
            is_new = False
            for text in element.stripped_strings:
                if 'nieuw' in text.lower():
                    is_new = True
                    break
            
            program = {
                'title': title,
                'link': link,
                'description': description or 'Programma op NPO',
                'is_new': is_new,
                'published_date': datetime.datetime.now(timezone.utc).isoformat()
            }
            
            programs.append(program)
            logger.debug(f"Found program: {title}")
        
        # Sort programs to put new ones first
        programs.sort(key=lambda x: x.get('is_new', False), reverse=True)
        
        # Limit to 20 programs
        programs = programs[:20]
        
        logger.info(f"Found {len(programs)} programs from website, {sum(1 for p in programs if p.get('is_new', False))} marked as new")
        
        # If no programs found, create some sample programs
        if not programs:
            logger.warning("No programs found, creating sample programs")
            sample_programs = [
                {
                    'title': 'Chateau Promenade',
                    'link': 'https://npo.nl/start/chateau-promenade',
                    'description': 'Diederik Ebbinge ontvangt drie vaste gasten op zijn schilderachtige Noord-Franse chateau.',
                    'is_new': True,
                    'published_date': datetime.datetime.now(timezone.utc).isoformat()
                },
                {
                    'title': 'Date On Stage',
                    'link': 'https://npo.nl/start/date-on-stage',
                    'description': 'In deze datingshow gaan singles op zoek naar de liefde.',
                    'is_new': True,
                    'published_date': datetime.datetime.now(timezone.utc).isoformat()
                },
                {
                    'title': 'Boer zoekt vrouw',
                    'link': 'https://npo.nl/start/boer-zoekt-vrouw',
                    'description': 'Boeren op zoek naar de liefde van hun leven.',
                    'is_new': False,
                    'published_date': datetime.datetime.now(timezone.utc).isoformat()
                },
                {
                    'title': 'Week van de Lentekriebels',
                    'link': 'https://npo.nl/start/week-van-de-lentekriebels',
                    'description': 'Collectie programma\'s over de lente.',
                    'is_new': False,
                    'published_date': datetime.datetime.now(timezone.utc).isoformat()
                }
            ]
            return sample_programs
        
        return programs
    
    except Exception as e:
        logger.error(f"Error fetching programs from website: {e}")
        # Return sample programs as fallback
        return [
            {
                'title': 'Chateau Promenade',
                'link': 'https://npo.nl/start/chateau-promenade',
                'description': 'Diederik Ebbinge ontvangt drie vaste gasten op zijn schilderachtige Noord-Franse chateau.',
                'is_new': True,
                'published_date': datetime.datetime.now(timezone.utc).isoformat()
            },
            {
                'title': 'Date On Stage',
                'link': 'https://npo.nl/start/date-on-stage',
                'description': 'In deze datingshow gaan singles op zoek naar de liefde.',
                'is_new': True,
                'published_date': datetime.datetime.now(timezone.utc).isoformat()
            }
        ]

def load_cache():
    """Load cached programs"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                
            # Check if cache is expired
            if time.time() - cache_data.get('timestamp', 0) < CACHE_EXPIRY:
                logger.info(f"Using {len(cache_data.get('programs', []))} programs from cache")
                return cache_data.get('programs', [])
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    return []

def save_cache(programs):
    """Save programs to cache"""
    try:
        cache_data = {
            'timestamp': time.time(),
            'programs': programs
        }
        
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
            
        logger.info(f"Saved {len(programs)} programs to cache")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")

def generate_rss_feed(programs):
    """Generate RSS feed from program information"""
    fg = FeedGenerator()
    fg.title('NPO Nieuwe Programma\'s')
    fg.description('Een RSS feed van nieuwe en recente programma\'s op NPO')
    fg.link(href=NPO_START_URL)
    fg.language('nl')
    
    for program in programs:
        fe = fg.add_entry()
        
        # Add "NIEUW: " prefix to title for new programs
        if program.get('is_new'):
            fe.title(f"NIEUW: {program['title']}")
        else:
            fe.title(program['title'])
        
        if program.get('link'):
            fe.link(href=program['link'])
            
        if program.get('description'):
            fe.description(program['description'])
            
        if program.get('published_date'):
            try:
                # Try to parse the date
                if isinstance(program['published_date'], str):
                    # Handle ISO format with timezone
                    pub_date = datetime.datetime.fromisoformat(program['published_date'])
                else:
                    # Use current date with timezone as fallback
                    pub_date = datetime.datetime.now(timezone.utc)
                    
                fe.pubDate(pub_date)
            except (ValueError, TypeError) as e:
                logger.warning(f"Date parsing error: {e}, using current time with timezone")
                # Use current date with timezone if parsing fails
                fe.pubDate(datetime.datetime.now(timezone.utc))
        else:
            # Use current date with timezone if no date is provided
            fe.pubDate(datetime.datetime.now(timezone.utc))
        
        if program.get('image'):
            fe.enclosure(program['image'], 0, 'image/jpeg')
    
    # Save the feed to a file
    fg.rss_file(RSS_FEED_FILE)
    logger.info(f"RSS feed generated: {RSS_FEED_FILE}")
    
    return RSS_FEED_FILE

def create_server_script():
    """Create a simple server script to serve the RSS feed"""
    server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

# Get port from command line argument or use default
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Change to the directory containing this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
        
    def do_GET(self):
        # For the root path, redirect to the RSS feed
        if self.path == '/':
            self.path = '/npo_new_programs.xml'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving NPO RSS feed at port {PORT}")
    httpd.serve_forever()
"""
    
    with open('serve_rss_feed.py', 'w') as f:
        f.write(server_script)
    
    os.chmod('serve_rss_feed.py', 0o755)
    logger.info("Created server script: serve_rss_feed.py")

def create_update_script():
    """Create a script to periodically update the RSS feed"""
    update_script = """#!/usr/bin/env python3
import os
import time
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='update_feed.log'
)
logger = logging.getLogger(__name__)

# Path to the feed generator script
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npo_new_programs_feed.py')

# Update interval in seconds (default: 1 hour)
UPDATE_INTERVAL = 3600

def update_feed():
    try:
        logger.info("Updating NPO RSS feed...")
        result = subprocess.run(['python3', SCRIPT_PATH], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Feed updated successfully")
        else:
            logger.error(f"Feed update failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Error updating feed: {e}")

def main():
    logger.info("Starting NPO RSS feed updater")
    
    while True:
        update_feed()
        logger.info(f"Sleeping for {UPDATE_INTERVAL} seconds...")
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
"""
    
    with open('update_feed.py', 'w') as f:
        f.write(update_script)
    
    os.chmod('update_feed.py', 0o755)
    logger.info("Created update script: update_feed.py")

def create_readme():
    """Create a README file with instructions"""
    readme = """# NPO Nieuwe Programma's RSS Feed

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
"""
    
    with open('README.md', 'w') as f:
        f.write(readme)
    
    logger.info("Created README.md with instructions")

def main():
    """Main function"""
    # Try to load programs from cache first
    programs = load_cache()
    
    if not programs:
        # Get programs from the website
        programs = get_programs_from_website()
        
        # Save to cache if we found programs
        if programs:
            save_cache(programs)
    
    if programs:
        # Generate RSS feed
        generate_rss_feed(programs)
        
        # Create server script
        create_server_script()
        
        # Create update script
        create_update_script()
        
        # Create README
        create_readme()
        
        logger.info(f"Successfully processed {len(programs)} programs")
    else:
        logger.warning("No programs found")

if __name__ == "__main__":
    main()
