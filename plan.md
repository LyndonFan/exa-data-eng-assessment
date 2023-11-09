# Plan

WIP: how to perform ETL on the data.

## Code Logic

-   Extract
    -   use `fhir.resource.r4b` to load them as objects
-   Transform/Load
    -   traverse through nested structure
        -   keep track of references
        -   create uuid if it doesn't have id
    -   "common" resource (see [below](#Storage))
        -   tabular format
    -   extension
        -   maybe just keep the main value/text?
    -   other resources
        -   keep id
        -   preserver all non-meta fields

## Storage

Criteria:

-   make it easy for **analytics team to create dashboards and visualizations** (in requirements)
-   stack I'm familiar with, hence can work and/or change quickly (e.g. no .NET for this task)
-   low financial cost and fast (if possible)

### Raw files

-   lossless!
    -   great for raw storage (if needed)
    -   good idea to save in raw form for:
        -   debugging
        -   sending request
-   hard to query by default

### Traditional databases (e.g. MySQL, PostgreSQL)

-   not rely on them too much
    -   too many fields, many possibly empty
    -   can have more than in specification due to extensions (e.g. us-core-race)
-   still want a handful?
    -   requirements mentioned "preferably in a tabular format"
    -   much easier and more straightforward for analytics team to use, esp. dashboards
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
