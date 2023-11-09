# Notes

Notes I'm jotting down for personal purpose. Detailed thought process and etc will be in another file, e.g. README.md.

## Exploration

This is needed since I have to know what I'm looking at. The requirements are a bit open-ended, and the main expectations are to have it in a more "tabular" and "queryable" format.

### First Impressions

-   File is nested JSON all the way down. Definitely have to look up the FHIR format.
-   The file names suggest that it is all the data for a single person.
    -   This may need to be double checked?
    -   The is likely overlapping information about other fields, e.g. same hospital.
-   File names have accented characters ("Maria Jose Adorno" with accented e, "Pariano Patino" with tilde n). Have to make sure it works in production.
-   There are 79 jsons, tallying up to 174 MB. The data is decently sizable.

### Play around

This stage is just playing around with data to see what it looks like. Often this is openning up the data in a text editor / VSCode to see what the columns are, and inspect the data by eye. I migth run some code in the Python REPL using command line.

```
from fhir.resources.bundle import Bundle
from pathlib import Path

path = Path('data/Aaron697_Dickens475_8c95253e-8ee8-9ae8-6d40-021d702dc78e.json')
bundle = Bundle.parse_file(path)
```

This got a bunch of validation errors, with 3 different types:

-   `entry -> 1 -> resource -> class, value is not a valid list (type=type_error.list)`
-   `entry -> 1 -> resource -> participant -> 0 -> individual, extra fields not permitted (type=value_error.extra)`
-   `entry -> 7 -> resource -> contained -> 1 -> __root__ -> kind, field required (type=value_error.missing)`

So this means one or more of:

-   learn more about the FHIR resource type
-   the data needs cleaning

Turns out it's the former! Judging from the data's date (around 2020), and the list of published version (https://hl7.org/fhir/directory.html) it seems like the data conforms to R4 or R4B standard, not the latest R5. Just to have keep that in mind.

Luckily, the `fhir.resources` library has support for R4 standard like so:

```
from fhir.resources.r4b.bundle import Bundle
from pathlib import Path

path = Path('data/Aaron697_Dickens475_8c95253e-8ee8-9ae8-6d40-021d702dc78e.json')
bundle = Bundle.parse_file(path)
```

It worked! Now to actually look into what it has.

The Bundle has type of transaction, which is a list of more resources.

```python
from collections import Counter

entry_types = [
    entry.resource.resource_type
    for entry in bundle.entry
]
entry_counter = Counter(entry_types)
```

It seems like we should do this for all jsons to get a better understanding.

-   entry-level resource_types aren't that diverse? They all start with Patient, then others
-   no. of entries ranges from 118 to 7825
-   some fields are custom / use extensions
-   later entries use references instead of full definitions

## Plan

-   start writing up plan.md
-   finished extract -- great! (just making a library call)

-   spent some time trying to think of sturctured db schema, but not sure about:

    -   which columns to pick (so many!)
    -   most columns have cardinality "0..\*", so are in nested / list format

-   start spending time on mongodb?

    -   still not sure about what transformations to do
    -   try doing no extra pre-processing, just save it in Mongo
        -> Works!

-   naively pass in all jsons through main.py at this state:

```bash
>> time (for fname in $(find data -type f -name "*.json"); do python main.py $fname; done)
(debug messages skipped)
real    11m39.688s
user    1m14.167s
sys     0m8.719s
```

... yeah, that's too slow.

-   changed code to process all files first, then upload all at once:

```bash
time python main.py ./data
(debug messages skipped)
real    2m32.230s
user    1m22.853s
sys     0m1.586s
```

Better! But it's not doing a lot at the moment.
