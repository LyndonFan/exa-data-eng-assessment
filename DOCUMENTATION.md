# Documentation

## Overall Code Logic

## Storage Architecture

The data is stored in 3 locations and formats, each with their own purposes.

### JSON files

This is to make a copy of the raw, unedited file for record-keeping purposes. For example, if the supplier sends a correction of the bundle, we can know any differences.

It is noted that in the current situation it merely copies the data, so isn't that useful.

### MongoDB

This combines all the data and stores them in a queriable form, while making minimal edits.

### SQL database

## Next Steps
