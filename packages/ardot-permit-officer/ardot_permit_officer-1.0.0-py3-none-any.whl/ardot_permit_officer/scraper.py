from dataclasses import dataclass


@dataclass
class Officer:
    district: str
    name: str
    email: str
    phone: str
    counties: list


def get_permit_officer_by_district(district: int) -> dict:
    """
    Get permit officer info for a single district (1-10).
    By default returns a dict. To get an Officer object, use get_permit_officer_by_district_obj.
    """
    return get_permit_officer_info(district)


def get_permit_officer_by_district_obj(district: int) -> Officer:
    """
    Get permit officer info for a single district (1-10) as an Officer object.
    """
    info = get_permit_officer_info(district)
    return Officer(
        district=info["district"],
        name=info["name"],
        email=info["email"],
        phone=info["phone"],
        counties=info["counties"],
    )


def get_all_permit_officers_obj() -> list:
    """
    Get permit officer info for all 10 districts as Officer objects.
    """
    return [get_permit_officer_by_district_obj(i) for i in range(1, 11)]


import requests
from bs4 import BeautifulSoup
from typing import List, Dict

BASE_URL = "https://ardot.gov/districts/district-{}"  # 1-10

from typing import Any


def get_permit_officer_info(district: int) -> Dict[str, Any]:
    import re

    officer_info = {
        "district": str(district),
        "name": "",
        "email": "",
        "phone": "",
        "counties": [],
    }
    url = BASE_URL.format(district)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Scrape counties
    counties = []
    # Search all <p> and <li> tags for 'Counties:'
    for tag in soup.find_all(["p", "li"]):
        text = tag.get_text(separator=" ", strip=True)
        if "counties:" in text.lower():
            counties_text = text.split(":", 1)[-1]
            counties_text = counties_text.replace(".", "").replace(";", "").strip()
            counties = [c.strip() for c in counties_text.split(",") if c.strip()]
            break
    officer_info["counties"] = counties

    # Find the 'Contacts' section
    contacts_header = None
    for h in soup.find_all(["h2", "h3", "h4"]):
        if "contact" in h.get_text(strip=True).lower():
            contacts_header = h
            break
    if contacts_header:
        # Collect all text and <a> tags after the contacts header, up to the next header
        sib = contacts_header.next_sibling
        lines = []
        mailtos = []
        while sib:
            if hasattr(sib, "name") and sib.name and sib.name.startswith("h"):
                break
            # Collect mailto links
            if hasattr(sib, "find_all"):
                for a in sib.find_all("a", href=True):
                    href = a["href"]
                    if href and href.startswith("mailto:"):
                        mailtos.append(
                            (
                                a.get_text(strip=True),
                                href.replace("mailto:", "").strip(),
                            )
                        )
            text = (
                sib.get_text(" ", strip=True) if hasattr(sib, "get_text") else str(sib)
            )
            for line in text.splitlines():
                line = line.strip()
                if line:
                    lines.append(line)
            sib = sib.next_sibling
        # Scan for 'Permit Officer' and extract info from the same or nearby lines
        for i, line in enumerate(lines):
            if "permit officer" in line.lower():
                # Try to extract name (before 'Permit Officer')
                name_match = re.search(r"([A-Za-z .\'-]+)\s*Permit Officer", line)
                if name_match:
                    officer_info["name"] = name_match.group(1).strip()
                # Try to extract phone from this and next 2 lines
                for j in range(i, min(i + 3, len(lines))):
                    phone_match = re.search(r"(\(\d{3}\) ?\d{3}-?\d{4})", lines[j])
                    if phone_match and not officer_info["phone"]:
                        officer_info["phone"] = phone_match.group(1).strip()
                # Try to find the closest mailto link (by name match)
                for name, email in mailtos:
                    if (
                        officer_info["name"]
                        and isinstance(officer_info["name"], str)
                        and officer_info["name"].split()[0].lower() in name.lower()
                    ):
                        officer_info["email"] = email
                        break
                break
    # Fallback: check og:description meta tag for contact info if nothing found
    if (
        not officer_info["name"]
        or not officer_info["email"]
        or not officer_info["phone"]
    ):
        desc_match = re.search(
            r'<meta[^>]+property=["\"]og:description["\"][^>]+content=["\"]([^"\"]+)["\"]',
            resp.text,
        )
        if desc_match:
            desc = desc_match.group(1)
            po_match = re.search(
                r"([A-Za-z .\'-]+)Permit Officer([A-Za-z0-9@.\-() ]+)", desc
            )
            if po_match:
                officer_info["name"] = po_match.group(1).strip()
                rest = po_match.group(2)
                email_match = re.search(r"([\w.\-]+@[\w.\-]+)", rest)
                phone_match = re.search(r"(\(\d{3}\) ?\d{3}-?\d{4})", rest)
                if email_match:
                    officer_info["email"] = email_match.group(1).strip()
                if phone_match:
                    officer_info["phone"] = phone_match.group(1).strip()
    return officer_info


def get_all_permit_officers() -> List[Dict[str, Any]]:
    """
    Get permit officer info for all 10 districts.
    """
    return [get_permit_officer_info(i) for i in range(1, 11)]
