# LMC (née RMC) Data Recorder And Playback Toolset

- [Motivation](#motivation)
- [Principles Of Operations](#principles-of-operations)
- [Further Reading](#further-reading)
  - [Installation Guide](docs/InstallationGuide.md)
  - [Playback Tools User Guide](docs/PlaybackToolsUserGuide.md)
  - [Using Recorded Data In Python](docs/API.md)
  - [Recording Tools Catalog](docs/RecordingToolsCatalog.md)
  - [Playback Tools Catalog](docs/PlaybackToolsCatalog.md)
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

This is based on an object-oriented approach, where a component is implemented
by a class that provides its state and functionality. The component exposes
information through a management class. At runtime, instances of the component
and its associated management classes are created and destroyed as needed.

The instances are grouped in a tree structure, starting from an empty root.

In addition to the C++ library, real-time components support a REST API
providing access in [JSON](https://www.json.org/json-en.html) format:

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
   (albeit compressed) and repetitive content: all information in each snapshot,
   regardless of whether it has changed from the previous snapshot or not.

1. Snap the (compressed) JSON and store only the changes in a custom binary
   format in a compressed file.

   This is the approach taken by this project and it yields a 20:1 to 50:1
   compression ratio improvement over approach #1.

1. Store the parsed information into a relational database.

   This would map classes to tables and variables to columns, and would probably
   be less efficient than #2 (though this is speculative). However, there might
   be some merit in having the relevant data (a certain time window for a few
   components) in a relational database, so this project provides an export
   capability to create BCP-like files for import.

1. Store the parsed information in a time-series database like
   [VictoriaMetrics](https://victoriametrics.com/)

   This might be as efficient as #2 and will be the subject of a future project.

## Principles Of Operations

The recorder maintains an internal cache of the previous scan and, except for
checkpoints, generates records only for variables whose values have changed. The
recorder uses a [custom-structured binary format](docs/DataModel.md) that
replaces string names with numeric IDs. The mapping between names and IDs is
recorded the first time a new mapping is encountered and at checkpoints, when
all information is recorded regardless of whether it is old or unchanged.

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
        |   . cache           .      ...........     |
        |   ...................           | changes  |
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
  [command-line tool](docs/PlaybackToolsUserGuide.md#running-queries)
- for limited subsets of data, imported into a SQL database using the files
  generated by the [export](docs/) command

## Further Reading

- [Installation Guide](docs/InstallationGuide.md)
- [Playback Tools User Guide](docs/PlaybackToolsUserGuide.md)
- [Using Recorded Data In Python](docs/API.md)
- [Recording Tools Catalog](docs/RecordingToolsCatalog.md)
- [Playback Tools Catalog](docs/PlaybackToolsCatalog.md)
- [Data Model](docs/DataModel.md)
- [Developer Guide](docs/DeveloperGuide.md)
