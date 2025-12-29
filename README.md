# LMC (née RMC) Data Recorder And Playback Toolset

- [Motivation](#motivation)
- [Principles Of Operations](#principles-of-operations)
- [Further Reading](#further-reading)
  - [Installation Guide](docs/InstallationGuide.md)
  - [Playback Tools User Guide](docs/PlaybackToolsUserGuide.md)
  - [Using Recorded Data In Python](docs/API.md)
  - [Recording Tools Catalogue](docs/RecordingToolsCatalogue.md)
  - [Playback Tools Catalogue](docs/PlaybackToolsCatalogue.md)
  - [Data Model](docs/DataModel.md)
  - [Developer Guide](docs/DeveloperGuide.md)
- [License](LICENSE)

## Motivation

LSEG Real-Time Platform components (adh, ads) provide access to a rich set of
internal stats via
[LMC](https://developers.lseg.com/en/api-catalog/real-time-legacy/refinitiv-management-classes-rmc).

Recording this information at regular intervals would be beneficial for
troubleshooting, event investigation, capacity planning, etc. and this project
provides a solution for that.

Conceptually each component of a LSEG process exposes some information in the
form of a class. A class is a template grouping data together as a list of
variables. A specific component is identified by an instance (name).

This is based on the object oriented approach, whereby a component is
implemented by a class providing its state and functionality; the component
exposes information through a management class. At runtime, instances of the
component and its associated management classes are created/destroyed as needed.

The instances are grouped in a tree structure, starting from an empty root.

In addition to the C++ library, realtime components support a REST API providing access in
[JSON](https://www.json.org/json-en.html) format:

```json
[
  {
    "Instance": "lseg1.bgp59.com.1.adh",
    "Class": "ManagedProcess.SrcDist",
    "Variables": [
      {
        "Name": "processID",
        "Type": "Numeric",
        "Value": 45
      },
      {
        "Name": "groupID",
        "Type": "Numeric",
        "Value": 500
      },
      {
        "Name": "userID",
        "Type": "Numeric",
        "Value": 500
      }
    ],
    "Children": [
      {
        "Instance": "lseg1.bgp59.com.1.adh.admin.MemoryStats",
        "Class": "ShmemMOServerStats",
        "Variables": [
          {
            "Name": "pid",
            "Type": "Numeric",
            "Value": 45
          }
        ],
        "Children": []
      }
    ]
  }
]
```

Potential recording solutions:

1. Snap the compressed JSON response and append it, together with the timestamp,
   to a file.

   This is a very simple solution but it has an inefficient storage format: text
   (albeit compressed) and content: all info in each snap, regardless of whether
   it has changed from the previous snap or not.

1. Snap the (compressed) JSON and store only the changes in a custom binary
   format in a compressed file.

   This is the approach taken by this project and it yields a 20:1 .. 50:1
   (in compressed:out compressed) shrinking ratio over #1.

1. Store the parsed information into a relational database.

   This would map classes into tables and variables into columns, probably it
   would be less efficient than #2 (a guess on my part). However there might
   some merit in having the relevant data (a certain time window for a few
   components) into a RDB, so this project provides an export capability to
   create BCP like files for import.

1. Store the parsed information into a timeseries database like
   [VictoriaMetrics](https://victoriametrics.com/)

   This might be as efficient as #2 and it will the subject of a future project.

## Principles Of Operations

The recorder maintains an internal cache with the previous scan and, except for
checkpoints, it will generate records only for variables whose values have
changed. The recorder uses a [custom structure, binary
format](docs/DataModel.md) which replaces string names with numeric ID's. The
information about name <-> ID mapping is recorded first time when a new mapping
is encountered and at checkpoints, when all info is recorded regardless of it
being old and/or unchanged.

```text
              +------------+
              |   adh/ads  |
              +------------+
                     | REST API 
        +------------|-------------------------------+
        |   .........v.........      ...........     |
        |   .   current scan --------->        .     |
        |   .        v        .      . compare .     |
        |   .     prev scan ---------->        .     |
        |   ...................      ...........     |
        |                                 | changes  |
        |                            .....V.....     |
        |                            . encoder .     |
        |   lmcrec                   ...........     |
        +---------------------------------|----------+
                                          v records
                                    record file           
                                          | records
        +---------------------------------|----------+
        |                            .....v.....     |
        |                            . decoder .     |
        |                            .....|.....     |
        |                                 | updates  |
        |                        .........v......... |
        |                        . LMC state cache . |
        |  lmcrec playback       .........|......... |
        +---------------------------------|----------+
                                          v
                                user / playback tool
```

The recorded data can be used:

- [programmatically](docs/API.md) in Python
- [queried](docs/QueryDescription.md) via a
  [command tool](docs/PlaybackToolsUserGuide.md#running-queries)
- for limited subsets of data, imported into a SQL database, using the the files
  generated by the [export](docs/) command

## Further Reading

- [Installation Guide](docs/InstallationGuide.md)
- [Playback Tools User Guide](docs/PlaybackToolsUserGuide.md)
- [Using Recorded Data In Python](docs/API.md)
- [Recording Tools Catalague](docs/RecordingToolsCatalogue.md)
- [Playback Tools Catalogue](docs/PlaybackToolsCatalogue.md)
- [Data Model](docs/DataModel.md)
- [Developer Guide](docs/DeveloperGuide.md)
