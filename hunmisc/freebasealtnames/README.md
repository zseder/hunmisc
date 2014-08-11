These scripts are to generate alternative names to entities based on this data:
http://googleresearch.blogspot.com/2013/07/11-billion-clues-in-800-million.html

## Usage

1. download data
See `clueweb12facc_to_mention.py` header for details
1. extract dictionaries
Use `clueweb12facc_to_mention.py`. See help with `-h` for instructions.
    1. Sample run is
    ~~~~
    python clueweb12facc_to_mention.py /path/to/Clueweb12FACC/ dmentions.pickle --output-reverse dmentions_rev.pickle
    ~~~~
1. extract alternative names based on extracted dictionaries in the previous
steps.
For every mention, at most one entity is kept.
Parameters:
    1. `min-str-entity`: a mention for an entity is filtered when less than
        this
    1. `min-str-ratio`: for a given mention, if an entity is mentioned with
        less ratio than this, filtered
    1. `min-str-sum`: mentions with less total number are filtered
    1. `min-entity-sum`: all entities with less total mention are filtered
    1. `min-fraction`: for a given entity, if a mention covers less than this
        ratio, filtered
    1. `best-entity-ratio`: for a given mention, if the best two entities are
        not two far from each other (ratio 5.0 as default), mention is
        skipped because it looks like it is disambigous
    1. `lower`: lowercasing mentions, if it wasn't done while building
        dictionaries
    1. `o`: output. If not given: stdout
    1. `parallel`: runs parallel. Uses as much cpu as there is. default=True
Running time was 14 hrs using 1 core and zipped tsvs. With bunch(=n) of cores
it shouldn't be n-times faster because of I/O throttling.

Running:
    1.
    ~~~~
    python altnames.py dmentions.pickle dmentions_rev.pickle > out
    ~~~~
