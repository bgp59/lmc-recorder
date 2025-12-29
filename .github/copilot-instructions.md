# Repository Scope Instructions

When creating test cases:

* use short, descriptive `Name` (.go) or `name` (.py), without spaces, in `CamelCase`

* elaborate the scenario in `Description` (.go) or `description` (.py)

* format JSON data indented on multiple lines as follows:

    ```go
    {
        JsonData: `
            [
                {
                    "Instance": "parent1",
                    "Class": "ParentClass1",
                    "Variables": [
                        {
                            "Name": "var1", 
                            "Type": "String", 
                            "Value": "val1"
                        },
                        {
                            "Name": "var2", 
                            "Type": "Numeric", 
                            "Value": 100
                        }
                    ],
                    "Children": [
                        {
                            "Instance": "child1-1",
                            "Class": "ChildClass1-1",
                            "Variables": [
                                {
                                    "Name": "var11", 
                                    "Type": "String", 
                                    "Value": "val11"
                                },
                                {
                                    "Name": "var12", 
                                    "Type": "Numeric", 
                                    "Value": 100
                                }
                            ],
                            Children": []
                        }
                    ]
                }
            ]
        `,
    }
    ```

    or

  ```go
  {
      JsonVars: `
          [
              {
                "Name": "var1", 
                "Type": "String", 
                "Value": "val1"
              },
              {
                "Name": "var2", 
                "Type": "Numeric", 
                "Value": 100
              }
          ]
      `,
  }
  ```

* format YAML data indented on multiple lines as follows:

    ```go
    func f() {
        yamlConfig := `
            default:
            scan_interval: 10s
            flush_interval: 10m
            checkpoint_interval: 2h
            rollover_interval: 12h
            parse_error_threshold: 10
            url: "http://example.com:9090/data"
            security_key: "test-key"
            request_timeout: 5s
            ignore_tls_verify: false
            tcp_conn_timeout: 3s
            recorders:
            - inst: "test-recorder"
        `
    }
    ```


* if a file is altered or generated add the following 2 comment lines at the top, **after** the `#!` (shebang) line, if the file ends in `.py`, `.sh` etc.

  * Prompt: path of the prompt file, relative to the root of the project
  * Model: model from the prompt file
