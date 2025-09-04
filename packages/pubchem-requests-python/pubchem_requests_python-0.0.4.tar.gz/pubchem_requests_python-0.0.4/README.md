# Pub Chem Requests

This package wraps the PubChem PUG REST and PUG View APIs, simplifying the retrieval of basic information about chemical compounds, including:

- Name
- Synonyms
- CAS Number
- CID Number (This is specific to PubChem)
- molecular formula
- molecular weight
- molar mass
- A list of descriptions
- A list of hazard statements (safety information)

## Installation

```bash
pip install pubchem-requests-python
```

## The Compound Class

A class containing information about a given chemical compound.

### Fetching a compound
Compounds can be initialized from a name, CAS Number, or directly from a CID:

```python
from pubchem_requests_python import (
    compound_from_name,
    compound_from_CAS,
    compound_from_CID,
)

# 3 ways to retrieve information about water
from_name = compound_from_name('water')
from_CAS = compound_from_CAS('7732-18-5')
from_CID = compound_from_CID('962')
```

If a compound is not found, the ```compound_from_X``` function will return ```None```.

Notes: 
- ```compound_from_CID``` is the most reliable, closely followed by ```compound_from_CAS```. ```compound_from_name``` does not search synonyms and uses the name directly in the api call, meaning typos and spacing can directly affect the success of the function.

### Getters

Each compound property has an associated getter function:

```python
    def get_synonyms(self) -> list[str] | None
    def get_name(self) -> str | None
    def get_cas(self) -> str | None
    def get_descriptions(self) -> list[str] | None
    def get_molecular_formula(self) -> str | None
    def get_molecular_weight(self) -> float | None
    def get_molar_mass(self) -> float | None
    def get_safety_data(self) -> list[str] | None
```

Alternatively, the ```.dict()``` function will return a dictionary representing the compound with keys:
- ```"name": str | None```
- ```"cas": str | None```
- ```"cid": str | None```
- ```"synonyms": list[str] | None```
- ```"descriptions": list[str] | None```
- ```"molecular_formula": str | None```
- ```"molecular_weight": float | None```
- ```"molar_mass": float | None```
- ```"safety_data": list[str] | None```

Note: It is possible for a compound to be found, but for some of its information to be missing/empty. In this case, the get fucntion for that property will return ```None```, and the key for that property will map to ```None```.

### Future work
- The PUG View response contains 'Experimental Properties' which vary from compound to compound, but generally contain information about the physical form/appearance of a compound at room temperature, information about boiling point, odor, taste, etc. This could be incorporated into the compound class.
- Lower level logging.

## Individual Requests

For convenience, the package also provides a set of functions to retrieve individual chemical properties:

```python
def cas_to_cid(cas_number: str) -> str | None
def name_to_cid(compound_name: str) -> str | None
def cid_to_cas(cid: str) -> str | None
def cid_to_name(cid: str) -> str | None
def cid_to_names(cid: str) -> list[str] | None
def name_to_cas(compound_name: str) -> str | None
def cas_to_name(cas_number: str) -> str | None
def cas_to_names(cas_number: str) -> list[str] | None
def cid_to_molecular_weight(cid: str) -> float | None
def name_to_molecular_weight(compound_name: str) -> float | None
def cas_to_molecular_weight(cas_number: str) -> float | None
def cid_to_safety_data(cid: str) -> list[str] | None
def name_to_safety_data(name: str) -> list[str] | None
def cas_to_safety_data(cas_number: str) -> list[str] | None
def cid_to_molecular_formula(cid: str) -> str | None
def name_to_molecular_formula(name: str) -> str | None
def cas_to_molecular_formula(cas_number: str) -> str | None
```

Note: Initializing a compound takes ~the same amount of time as any one of these functions, and is therefore generally more efficient.