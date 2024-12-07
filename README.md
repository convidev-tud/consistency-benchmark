# Merge Consistency Benchmark

## Purpose
> TODO

## Repository Structure

* ``data`` contains the data points. Each data point is a folder containing a base model, evolution models a and b, and evolution operation models a and b.
  * ``data/[IDENTIFIER]/[base|evolution_a|evolution_b].xml``
  * Optionally, each data point may contains a README.md file explaining the purpose of the data point.
* ``gen`` contrains the rendered PUML- and model files and PNGs generated from the data. Subdirectories follow the structure of the data folder.
  * This folder is under gitignore. **Modifications to the generated files are lost during re-generation!**
  * *The up-to-date output of the gen folder will be built by the CI pipeline and is available under the latest CI run (work in progress)*
* ``meta`` contain the used metamodels
  * XSL/
    *  ``/graph.xsd``
    *  ``/operations.xsd``
  * *Equivalent metamodels in other languages (work in progress)*
* ``tools`` contains model transformations and generation scripts
  * **auto_evolv** Is the script to apply an evolution model to a graph model.
  * **graph_to_puml** Is the script to generate a PlantUML file and PNG from a graph model.
  * graph -> other formats  (TODO)
  
### Manual Execution

To (re-)generate the applied evolutions and PNG's execute the ``generate.sh`` command in the root of this directory. The generate script contains extensive error reporting in case requirements are missing on your system. The script expects to find:
* python3
* pip3
* java

These programs must be available in PATH.

## Contributing
> TODO

## Licensing

The dataset and all developed tools shall be available under GLPv3 License

This work uses the third-party application "PlantUML" (plantuml-lgpl-1.2024.8.jar) licensed under the LGPL license. A copy of the PlantUML JAR is located under tools/libs/.
Find more information about PlantUML: https://github.com/plantuml/plantuml

# Walkthrough by Example
> TODO