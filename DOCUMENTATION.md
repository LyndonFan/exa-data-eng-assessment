# Documentation

This page is for explaining what the code does and any associated decisions. For running the code, see [README.md].

## Overall Code Logic & Storage

### Overall Logic

1. Make a copy of the raw files for record keeping.
2. Extract the inner resources, and save them in Mongo. Also generate a lookup of id to resource type.
3. For specific resource types (Patient, Encounter, Observation), process them to get useful fields and save them in a SQL database.

### JSON files

This is to make a copy of the raw, unedited file for record-keeping purposes. For example, if the supplier sends a correction of the bundle, we can know any differences.

It is noted that in the current situation it merely copies the data, so isn't that useful.

### MongoDB

This combines all the data and stores them in a queriable form, while making minimal edits.

For each resource type, the data is stored in its own collection. We remove the "resourceType" field, and rename the "id" field to "\_id" to use as indexing in Mongo.

We also create a new "IDReference" collection, with documents like

```javascript
{
    "_id": string,
    "resourceType": string
}
```

This is used for looking up ids from references (e.g. `Encounter.subject`)

### SQL database

Here we perform specific modelling for 3 resources, namely:

-   Patient, the first resources that appears in each transaction. This is picked as it's likely the most often used "object"
-   Observation, the most frequent resource
-   Encounter, the most frequently referenced resource. We say resource A references resource B if A has a (nested) field which is like

    ```javascript
    {"reference": "urn:uuid:" + B.id}
    ```

Note the schemas are written in `src/db/schema.py`, which are also used to create the tables for convenience. Below we explain their relationship and meaning.

You can also see the [ER Diagram](ERDiagram.md) for a quick look of the relationships between tables.

### Patient

| Column name       | Datatype | Required | Corresponding FHIR Field                      |
| ----------------- | -------- | -------- | --------------------------------------------- |
| id                | string   | Y        | id                                            |
| active            | boolean  | Y        | active                                        |
| name              | string   | N        | "last inferred official name"<sup>1</sup>     |
| maiden_name       | string   | N        | "last inferred maiden name"<sup>1</sup>       |
| deceased          | boolean  | Y        | deceasedBoolean, deceasedDateTime<sup>2</sup> |
| deceased_datetime | datetime | N        | deceasedDateTime                              |
| marital_status    | string   | N        | maritalStatus.text                            |

<sup>1</sup>: The names come from the "name" field, and whether they are official or maiden depends on the "use" field. Inferring the name is by picking the earliest value from below:

-   `name.text`
-   `name.given[0] + " " +name.family`
-   `name.given[0]`

<sup>2</sup>: If the deceasedDateTime is not null, we infer deceasedBoolean to be true. If both fields are empty, we infer the patient to be alive, i.e. not deceased.

### Encounter

| Column name  | Datatype | Required | Corresponding FHIR Field        |
| ------------ | -------- | -------- | ------------------------------- |
| id           | string   | Y        | id                              |
| status       | string   | Y        | status                          |
| patient_id   | string   | Y        | subject.reference<sup>3</sup>   |
| class_code   | string   | N        | class.code                      |
| period_start | datetime | Y        | period.start                    |
| period_end   | datetime | Y        | period.end                      |
| reason       | string   | N        | reasonCode[0].coding[0].display |
| location     | string   | N        | location[0].location.display    |

<sup>3</sup>: This has a foreign key constraint, where the patient id (removing the "urn:uuid:" prefix) should be in the patient table.

### Observation

| Column name        | Datatype | Required | Corresponding FHIR Field                                          |
| ------------------ | -------- | -------- | ----------------------------------------------------------------- |
| id                 | string   | Y        | id                                                                |
| observation_type   | string   | Y        | code.coding[0].display                                            |
| status             | string   | Y        | status                                                            |
| patient_id         | string   | Y        | subject.reference<sup>4</sup>                                     |
| encounter_id       | string   | Y        | encounter.reference<sup>5</sup>                                   |
| category           | string   | N        | category[0].coding[0].display                                     |
| effective_datetime | datetime | N        | effectiveDateTime                                                 |
| issued             | datetime | N        | issued                                                            |
| values             | JSON     | N        | code, valueQuantity, valueCodeableConcept, components<sup>6</sup> |

<sup>4</sup>: Foreign key constraint from patient table.
<sup>5</sup>: Foreign key constraint from encounter table.
<sup>6</sup>: This is generated by combining the fields as such:

```python
[
    # if valueQuantity exists
    {"code": code, "valueQuantity": valueQuantity},
    # if valueCodeableConcept exists
    {"code": code, "valueCodeableConcept": valueCodeableConcept},
    *components
]
```

## Next Steps

### Better error handling

A lot of the code only works on the "happy path" where the at least one of the resources has that field. The `EncounterProcessor` has been rewritten several times to deal with missing columns, but the same could be done for other processors.

### More specific resource type modelling

Some of the fields could be modelled with more specificity (e.g. the JSON column in Observations)

### Modelling more resource types

It is noted that the next most frequent resource is Claim, which is also closely related to multiple other resources present (e.g. ExplanationOfBenefit). We can add more SQL tables and
