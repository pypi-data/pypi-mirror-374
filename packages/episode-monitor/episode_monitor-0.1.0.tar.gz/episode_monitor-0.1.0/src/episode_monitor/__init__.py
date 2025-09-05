import requests
import time
import re
import json
import yaml
import os
import argparse
import notify2
from datetime import datetime
from pathlib import Path


def get_xdg_path(env_var, default_subdir, filename):
    """Resolve an XDG path (creates directory if needed)."""
    base = Path(os.environ.get(env_var, str(Path.home() / default_subdir)))
    path = base / "episode_monitor"
    path.mkdir(parents=True, exist_ok=True)
    return path / filename


# Paths following XDG spec
STATE_FILE = get_xdg_path("XDG_STATE_HOME", ".local/state", "episode_counts.json")
CONFIG_FILE = get_xdg_path("XDG_CONFIG_HOME", ".config", "config.yaml")
LOG_FILE = get_xdg_path("XDG_CACHE_HOME", ".cache", "episode_log.txt")


def load_state():
    """Load last known episode counts from file (JSON)."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # empty if no file


def save_state(state):
    """Save episode counts to file (JSON)."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_config():
    """Load configuration (shows + interval) from YAML file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            shows = data.get("shows", [])
            interval = data.get("interval", 300)  # default 5 minutes
            return shows, interval
    else:
        default_data = {
            "interval": 300,
            "shows": ["The Simpsons", "Family Guy", "South Park"]
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(default_data, f)
        return default_data["shows"], default_data["interval"]


def log_message(message):
    """Log message to console and file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def send_notification(title, message):
    """Send a desktop notification."""
    notify2.init("Episode Monitor")
    n = notify2.Notification(title, message, "dialog-information")
    n.set_urgency(notify2.URGENCY_NORMAL)
    n.show()


def get_num_episodes_api(title):
    """
    Get the number of episodes of a TV show from Wikipedia using the MediaWiki API.
    `title` should be the page title, e.g., "The Simpsons".
    """
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    }

    response = requests.get(URL, params=PARAMS, headers={
        "User-Agent": "Mozilla/5.0 (compatible; EpisodeMonitor/1.0; +https://example.com)"
    })
    response.raise_for_status()
    data = response.json()

    # Extract wikitext
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    wikitext = page["revisions"][0]["slots"]["main"]["*"]

    # Look for num_episodes field inside the infobox
    match_line = re.search(r"\|\s*num_episodes\s*=(.*)", wikitext) # locate the line containing num_episodes = ...
    match_num = re.search(r"(\d+)", match_line.group(1)) if match_line else None # match for a number in the line containing num_episodes = ...
    return int(match_num.group(1)) if match_num else None


def check_shows(last_counts):
    """Perform a single check of all shows, update state, log changes."""
    shows, interval = load_config()

    for title in shows:
        count = get_num_episodes_api(title)
        if count is not None:
            if title not in last_counts:
                msg=f"Initial number of episodes: {count}"
                log_message(f"[{title}] {msg}")
                send_notification(f"{title}", msg)
            elif count > last_counts[title]:
                msg=f"New episode detected! Count increased from {last_counts[title]} to {count}"
                log_message(f"[{title}] {msg}")
                send_notification(f"{title}", msg)
            elif count < last_counts[title]:
                msg = f"Episode count decreased from {last_counts[title]} to {count} (possible Wikipedia edit)."
                log_message(f"[{title}] {msg}")
                send_notification(f"{title}", msg)

            last_counts[title] = count
        else:
            log_message(f"[{title}] Could not find episode count in infobox.")

    save_state(last_counts)
    return interval


def monitor_tv_shows(run_once=False):
    """Main monitoring loop or single run based on flag."""
    last_counts = load_state()
    shows, interval = load_config()

    log_message(f"Monitoring {len(shows)} shows (interval {interval}s, once={run_once})...")

    if run_once:
        check_shows(last_counts)
    else:
        while True:
            try:
                interval = check_shows(last_counts)
            except Exception as e:
                log_message(f"Error: {e}")
            time.sleep(interval)


def main():
    print(
        f"Config file: {CONFIG_FILE}\n"
        f"State file: {STATE_FILE}\n"
        f"Log file: {LOG_FILE}\n"
    )
    parser = argparse.ArgumentParser(description="Wikipedia TV Show Episode Monitor")
    parser.add_argument("--once", action="store_true", help="Run one check and exit")
    args = parser.parse_args()
    monitor_tv_shows(run_once=args.once)
