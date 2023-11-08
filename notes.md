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
