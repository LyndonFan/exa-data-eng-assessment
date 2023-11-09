# Plan

WIP: how to perform ETL on the data.

## Code Logic

### Extract

-   ...

### Transform

-   ...

### Load

-   ...

## Storage

### Raw files

-   lossless!
    -   great for raw storage (if needed)
-   hard to query by default

### Traditional databases (e.g. MySQL, PostgreSQL)

-   not rely on them too much
    -   too many fields, many possibly empty
    -   can have more than in specification due to extensions (e.g. us-core-race)
-   still want a handful?
    -   requirements mentioned "preferably in a tabular format"
-   what tables to pick?
    -   makes sense to have majority of tables keep track of resources -> which resources?
        -   normalized ones (e.g. Patient)
        -   commonly used ones (Observation, Claim, DiagnosticReport, ExplanationOfBenefit, DocumentReference, Encounter)
    -   some for delivery times?
    -   what fields?
        -   depends on resource

### NoSQL

-   document
    -   looks most apprioriate as it's in form of json and many nested
    -   e.g. Firestore / Mongo
    -   most familiar
-   key value pair
    -   fast, do-able with the <100 files?
    -   like redis. Used a handful of times,
-   graph db
    -   maintain relationships -- if any!
    -   unfamiliar
