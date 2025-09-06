# ardot_permit_officer

A Python package to fetch ARDOT permit officer contact information from all 10 district pages.

## Features
- Scrapes name, email, and phone number for each district's permit officer
- CLI tool to print or export the data


## Usage

### Command Line

Install the package (from PyPI or locally):

```bash
pip install ardot_permit_officer
```

Run the CLI to print all permit officer info as JSON:

```bash
ardot-permit-officer
```

### Python API

You can also use the package in your own Python code. You can choose between dict (default) or object-oriented (Officer class) results:

#### Get all permit officers (dicts)
```python
from ardot_permit_officer.scraper import get_all_permit_officers
officers = get_all_permit_officers()
for officer in officers:
	print(officer['email'])
```

#### Get all permit officers (objects)
```python
from ardot_permit_officer.scraper import get_all_permit_officers_obj
officers = get_all_permit_officers_obj()
for officer in officers:
	print(officer.email)
```

#### Get a single district's permit officer (dict)
```python
from ardot_permit_officer.scraper import get_permit_officer_by_district
officer = get_permit_officer_by_district(7)  # For district 7
print(officer['email'])
```

#### Get a single district's permit officer (object)
```python
from ardot_permit_officer.scraper import get_permit_officer_by_district_obj
officer = get_permit_officer_by_district_obj(7)
print(officer.email)
```

## Publishing
Publishing to PyPI is automated via GitHub Actions. See `.github/workflows/publish.yml`.
