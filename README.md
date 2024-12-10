# Merge Consistency Benchmark

## Purpose
This repository contains the data and tools of the *Merge Consistency Benchmark*.
The benchmark aims to provide a dataset usable for researching and evaluation different inconsistency scenarios.
The dataset aims to adhere to the following quality statements:

* **Openness** The dataset and its related artifacts are available under the GNU GPL-v3 license.
* **Reusability** The dataset is largely technology agnostic. The used base-technochnology is XML/XSD for models and metamodels. Exemplary model transformations into other common modeling languages are provided or can be easily created.
* **Comprehendability** The developed artifacts and data points aim to be easy to understand. The used metamodels are abstract and simple. Only rudimentary knowledge of software modeling must be required to understand the data points. We provide documentation for our tooling.
* **Extensibility** The dataset is not be conceptually limited to a specific number of data points. The tooling supports the creation of new data points by the community.
* **Relevance** Each data point aims to represent a relevant consistency problem. The used metamodels are simplifications but have strong similarities with practical modeling languages

## Usage & Contributions

We motivate the usage of this dataset for any purposes - may it be research or industry - as long as the dataset and tooling is used according to the openness requirement of the GNU GPL-v3 license. If desired, this repository can be forked, extended or modified according to the license terms and requirements. In particular, it is allowed to create and archive a copy of this repository in an openly-available reproduction package for research purposes.

We are happy to receive contributions to let the dataset grow over time. We aim to provide regular releases. Find the contribution guide in the remainder of this document.

## Repository Structure

* ``data`` contains the data points. Each data point is a folder containing a base model, evolution models a and b, and evolution operation models a and b.
  * ``data/[IDENTIFIER]/[base|evolution_a|evolution_b].xml``
  * Optionally, each data point may contains a meta.md file explaining the purpose of the data point.
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
  * graph -> other formats (TODO)
  
### Manual Execution (Dataset Processing)

To (re-)generate the applied evolutions and PNG's execute the ``generate.sh`` command in the root of this directory. The generate script contains extensive error reporting in case requirements are missing on your system. The script expects to find the following terminal commands:
* python3
* pip3
* java

## Contributing

> Contributions by core-contributors can be made directly in the main branch while the initial build-up of the dataset is in progress. Please refrain from breaking changes in the tooling without filing a pull request. **The main branch will be protected after the first release of the benchmark. Then, contributions are only possible via pull requests.** 

### Adding / Updating Data Points

A data point consists of a uniquely named directory within ``data/`` containing:
* a base model ``base.xml``
* two evolutions ``evolution_a.xml`` and ``evolution_b.xml``
* a short metadata description ``meta.md``

**To add a new data point...** 
1. create a copy of the *TEMPLATE* data point.
2. rename it with a unique but identifying name. Please use snake case (for example rename_property_conflict_01)
3. add your content to the already provided base model and evolution files. Note: you just write the base model and the evolution scripts. The final models will be generated automatically by a script after validating the correctness of the models. If opened in a XML/XSD capable editor (vscode with XML plugin) the editor will find the metamodel schema and already highlight invalid XML expressions.
4. Add desired data to the meta file. Please refrain from using any complex formatting to support machine-readability.
5. execute ``generate.sh`` as stated in *Manual Execution* to confirm the compilation of your data point
6. commit the data point with an explainatory commit message.

### Adding Metamodels / Model Transformations

**We currently do not consider changing the core XSD metamodels for graphs and operations as this would lead to major changes in the stable tooling.**

Contributions consisting of "congurent" metamodels and transformations are welcome.

You find the list of supported metamodels in the ``meta/`` directory. We currently support:
* XSD/XML (core)
* Ecore/XMI full support (work in progress)

Supporting a metamodel/language means the provision of an automated transformation script from the XML core data points into models of the target language.
* A language support can either include both support for the graph and operations (full) or just for the graph (basic).
* The language metamodels must be placed in a directory in ``meta/``
* The transformation script(s) must be placed in ``tools`` (e.g. ``tools/xml_to_ecore``)
* The transformation must be executable standalone via the commandline. All required libraries must be part of this repository. The script and dependencies must conform to the GNU GPL-v3 license.
* The transformation tool must provide an entry script ``transform.sh`` which reads the content of the ``gen/`` directory and writes its output either back to the ``gen/`` directory or to a new ``gen_[target]/`` directory.

Please contribute metamodels, language support and tooling only via pull requests.

## Licensing

The dataset and all developed tools shall be available under GLPv3 License

This work uses the third-party application "PlantUML" (plantuml-lgpl-1.2024.8.jar) licensed under the LGPL license. A copy of the PlantUML JAR is located under tools/libs/.
Find more information about PlantUML: https://github.com/plantuml/plantuml

# Walkthrough by Example

In this section we look at the ``data/EXAMPLE`` data point to explain the workings of the XML/XSD core of the benchmark.

The data point contains:
* a base model ``base.xml``
* two evolutions ``evolution_a.xml`` and ``evolution_b.xml``
* a short metadata description ``meta.md``

The metadata is not processed by the tooling and just for documentation purposes.

The base model contains a graph using the ``graph.xsd`` metamodel which is located in ``meta/XSL/graph.xsd``. 
The preamble of the XML shows that we use a local schema path. This means a XML validator only works if the relative locations of the graph model and metamodel are not changed. Otherwise, the preamble must be updated accordingly.

```XML
<?xml version="1.0"?>
<Graph xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns="http://mergebench.org/ns"
          xsi:schemaLocation="http://mergebench.org/ns ../../meta/XSL/graph.xsd">
```

The body of the model describes the relationship of humans and pets. 
The metamodel has four top-level model elements: *Group*, *Node*, *Property* and *DirectedEdge*

* A *Graph* contains 0..n *Group* elements and 0..n *DirectedEdge* elements.
* A *Group* contains 0..n *Node* elements.
* A *Node* contains 0..n *Property* elements.
* *Group*, *Node*, and *Property* have a *name* field. It is mandatory, unique and uses URI format.
  * Note that *Group*s cannot be nested.
* *DirectedEdge* has fields for *start*, *end*, and *semantics*. All three fields are mandatory and use URI format. 
  * *start* and *end* must be *name*s of *Group*s or *Node*s
  * A *DirectedEdge* can connect all combinations of *Group* and *Node* elements.
  * A *DirectedEdge* must be unique.

The example uses a class-diagram-like modeling approach. However, we do not restrict the semantics of what *Groups*, *Nodes*, *Properties* and *DirectedEdges* could be.

```XML
<Group name="pets">
  <Node name="cat">
    <Property name="name"/>
    <Property name="age"/>
  </Node>
  <Node name="dog">
    <Property name="name"/>
    <Property name="age"/>
  </Node>
</Group>

<Group name="humans">
  <Node name="parent" />
  <Node name="child" />
</Group>

<DirectedEdge start="cat" end="dog" semantics="likes"/>
<DirectedEdge start="parent" end="child" semantics="take_care_of"/>
<DirectedEdge start="humans" end="pets" semantics="take_care_of" />
```

The two files ``evolution_a`` and ``evolution_b`` contain possible scenarios how two collaborators could change the base model independently.

Let us have a look at ``evolution_b`` first:
```XML
<?xml version="1.0"?>
<Evolution xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns="http://mergebench.org/ns"
          xsi:schemaLocation="http://mergebench.org/ns ../../meta/XSL/operations.xsd">
</Evolution>
```
As shown, the XML preamble is similar to the graph model. The only difference is that we now use the ``operations.xsd`` metamodel.
The remainder of the evolution model is empty. This example models an empty model transformation, which we consider totally fine.

The file ``evolution_b`` contains a number of operations. The operations are grouped into *SemanticEdit*s whith a *Category* and *Description*.

* An *Evolution* contains 0..n *SemanticEdit* elements.
* A *SemanticEdit* contains 1..n *Operation*s.
  * A *SemanticEdit groups *Operation*s that aim to fulfill a common goal, for example achieving a certain high-level refactoring operation.
  * A *SemanticEdit* has a *Category* classifying the purpose. The ``operations.xsd`` metamodel contains the full list of possible categorties.
  * A *SemanticEdit* has a *Description*. This is a free text string to describe in huma-readable text the purpose of the edit.
* An *Operation* must wraps one of the following elements. Please take their exact descriptions and fields from the ``operations.xsd``.
  * *DeleteNode*
  * *DeleteDirectedEdge*
  * *DeleteGroup*
  * *DeleteProperty*
  * *AddNode*
  * *AddDirectedEdge*
  * *AddGroup*
  * *RenameProperty*
  * *AddProperty*
  * *RenameGroup*
  * *RenameNode*
  * *ChangeSemanticsDirectedEdge*
  * *MoveNodeToOtherGroup*
  * *JoinGroups*

Each *SemanticEdit* and each *Operation* has an index field of type int to avoid ambiguities and ease transformations. The index must reflext the execution order. Our tooling interprets the index with higher priority as the physical ordering. But please keep physical ordering and index ordering consistent.

The following example evolution modifies the above presented examplary graph.

```XML
<SemanticEdit index="0">
  <Semantic>
    <Category>REPURPOSE</Category>
    <Description>
      Change the names of the pets.
      The model is migrated for a new customer with different pets.
    </Description>
  </Semantic>
  <Operation index="0">
    <RenameNode oldNodeName="dog" newNodeName="mouse" />
  </Operation>
  <Operation index="1">
    <RenameNode oldNodeName="cat" newNodeName="hamster" />
  </Operation>
</SemanticEdit>

<SemanticEdit index="1">
  <Semantic>
    <Category>SIMPLYFY</Category>
    <Description>
      Remove the age property from the pets.
      The new customer does not need to know the age of the pets.
    </Description>
  </Semantic>
  <Operation index="0">
    <DeleteProperty nodeName="mouse" propertyName="age" />
  </Operation>
  <Operation index="1">
    <DeleteProperty nodeName="hamster" propertyName="age" />
  </Operation>
</SemanticEdit>
```

The evolution contains two *SemanticEdit*s. The first performs a *REPURPOSE* modification and the second one a *SIMPLIFY* modification. Both *SemanticEdit*s have a short human readable *Description*. In summary, the first edit changes the animal types "cat" and "dog" to "hamster" and "mouse". The second edit simplifies the model by removing the "age" property from both animal types.