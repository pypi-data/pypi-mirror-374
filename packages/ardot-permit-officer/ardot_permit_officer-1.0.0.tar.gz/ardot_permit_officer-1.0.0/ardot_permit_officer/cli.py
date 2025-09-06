import json
from .scraper import get_all_permit_officers

def main():
    officers = get_all_permit_officers()
    print(json.dumps(officers, indent=2))
