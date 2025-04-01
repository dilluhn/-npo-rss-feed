#!/usr/bin/env python3
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
