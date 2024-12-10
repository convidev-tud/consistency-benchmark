'''
Copyright (C) 2024 Karl Kegel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from lxml import etree
import sys

# GRAPH CLASS DEFINITIONS

class DirectedEdge:
    def __init__(self, start: str, end: str, semantics: str):
        self.start: str = start
        self.end: str = end
        self.semantics: str = semantics
        
    def __str__(self):
        return self.start + " -> " + self.end + ": " + self.semantics

class Node:
    def __init__(self, name: str):
        self.name: str = name
        self.properties: list[str] = []
        
    def __str__(self):
        return self.name + " " + str(self.properties)
        
class Group:
    def __init__(self, name: str):
        self.name: str = name
        self.nodes: list[Node] = []
        
    def __str__(self):
        res = self.name + ": {" 
        for node in self.nodes:
            res += str(node) + "; "
        res += "}"
        return res

class Graph:
    def __init__(self):
        self.groups: list[Group] = []
        self.directed_edges: list[DirectedEdge] = []
        
    def __str__(self):
        res = "["
        for group in self.groups:
            res += str(group) + "; "
        res += "] , ["
        for edge in self.directed_edges:
            res += str(edge)
            res += "; "
        res += "]"
        
        return res
        
    def get_group(self, name: str) -> Group:
        for group in self.groups:
            if group.name == name:
                return group
        return None
        
    def get_node(self, name: str) -> Node:
        for group in self.groups:
            for node in group.nodes:
                if node.name == name:
                    return node
        return None
        
    def add_group(self, group: Group) -> bool:
        if not self.is_unique_node_or_group_name(group.name):
            return False
        self.groups.append(group)
        return True
        
    def add_directed_edge(self, directed_edge: DirectedEdge) -> bool:
        if self.is_double_edge(directed_edge.start, directed_edge.end, directed_edge.semantics):
            return False
        if self.is_referenceable_element(directed_edge.start) and self.is_referenceable_element(directed_edge.end):
            self.directed_edges.append(directed_edge)
            return True
        return False
        
    def add_node(self, node: Node, group_name: str) -> bool:
        if not self.is_group(group_name):
            return False
        if not self.is_unique_node_or_group_name(node.name):
            return False
        for group in self.groups:
            if group.name == group_name:
                group.nodes.append(node)
                return True
        return False
     
    def is_group(self, name: str) -> bool:
        for group in self.groups:
            if group.name == name:
                return True
        return False
    
    def is_node(self, name: str) -> bool:
        for group in self.groups:
            for node in group.nodes:
                if node.name == name:
                    return True
        return False
    
    def is_referenceable_element(self, name: str) -> bool:
        return self.is_group(name) or self.is_node(name)
    
    def is_property(self, node_name: str, property_name: str) -> bool:
        node = self.get_node(node_name)
        if node is not None:
            return property_name in node.properties
        return False
    
    def add_property(self, node_name: str, property_name: str) -> bool:
        node = self.get_node(node_name)
        if node is not None:
            node.properties.append(property_name)
            return True
        return False
                        
    def delete_property(self, node_name: str, property_name: str) -> bool:
        for group in self.groups:
            for node in group.nodes:
                if node.name == node_name:
                    if property_name in node.properties:
                        node.properties = [property for property in node.properties if property != property_name]
                        return True
        return False
    
    def update_property(self, node_name: str, old_property_name: str, new_property_name: str) -> bool:
        for group in self.groups:
            for node in group.nodes:
                if node.name == node_name:
                    if old_property_name in node.properties:
                        node.properties = [new_property_name if property == old_property_name else property for property in node.properties]
                        return True
        return False
        
    def delete_node_and_references(self, group_name: str, node_name: str) -> bool:
        found_node = False
        group = self.get_group(group_name)
        if group is None:
            return False
        for group in self.groups:
            for node in group.nodes:
                if node.name == node_name:
                    group.nodes.remove(node)
                    found_node = True
        if found_node:
            self.directed_edges = [edge for edge in self.directed_edges if edge.start != node_name and edge.end != node_name]
            return True
        else:
            return False
    
    def delete_group_and_references(self, group_name: str) -> bool:
        group = self.get_group(group_name)
        if group is None:
            for node in group.nodes:
                self.delete_node_and_references(node.name)
            self.groups = [group for group in self.groups if group.name != group_name]
            self.directed_edges = [edge for edge in self.directed_edges if edge.start != group_name and edge.end != group_name]
            return True
        else:
            return False
        
    def is_unique_node_or_group_name(self, name: str) -> bool:
        for group in self.groups:
            if group.name == name:
                return False
            for node in group.nodes:
                if node.name == name:
                    return False
        return True
    
    def is_double_edge(self, start: str, end: str, semantics: str) -> bool:
        for edge in self.directed_edges:
            if edge.start == start and edge.end == end and edge.semantics == semantics:
                return True
        return False
    
    def replace_name_in_directed_edges(self, old_name: str, new_name: str):
        for edge in self.directed_edges:
            if edge.start == old_name:
                edge.start = new_name
            if edge.end == old_name:
                edge.end = new_name
                
    def delete_directed_edge(self, start: str, end: str, semantics: str) -> bool:
        for edge in self.directed_edges:
            if edge.start == start and edge.end == end and edge.semantics == semantics:
                self.directed_edges.remove(edge)
                return True
        return False
                
    def rename_node_and_references(self, old_name: str, new_name: str) -> bool:
        if not self.is_unique_node_or_group_name(new_name):
            return False
        if not self.is_node(old_name):
            return False
        for group in self.groups:
            for node in group.nodes:
                if node.name == old_name:
                    node.name = new_name
        self.replace_name_in_directed_edges(old_name, new_name)
        return True
        
    def rename_group_and_references(self, old_name: str, new_name: str) -> bool:
        if not self.is_unique_node_or_group_name(new_name):
            return False
        if not self.is_group(old_name):
            return False
        for group in self.groups:
            if group.name == old_name:
                group.name = new_name
        self.replace_name_in_directed_edges(old_name, new_name)
        return True
    
    def move_node_to_other_group(self, node_name: str, old_group_name: str, new_group_name: str) -> bool:
        old_group = self.get_group(old_group_name)
        new_group = self.get_group(new_group_name)
        node = self.get_node(node_name)
        if old_group is None or new_group is None or node is None:
            return False
        old_group.nodes = [node for node in old_group.nodes if node.name != node_name]
        new_group.nodes.append(node)
        
    def join_groups(self, group1_name: str, group2_name: str, new_group_name: str) -> bool:
        group1 = self.get_group(group1_name)
        group2 = self.get_group(group2_name)
        new_group = Group(new_group_name)
        if not (new_group_name == group1_name or new_group_name == group2_name or self.is_unique_node_or_group_name(new_group_name)):
             return False
        if group1 is None or group2 is None:
            return False
        new_group.nodes = group1.nodes + group2.nodes
        self.groups = [group for group in self.groups if group.name != group1_name and group.name != group2_name]
        self.groups.append(new_group)
        self.replace_name_in_directed_edges(group1_name, new_group_name)
        self.replace_name_in_directed_edges(group2_name, new_group_name)
        return True
        
        
# XML FUNCTIONS

def xml_from_file(file_path):
    input_root = etree.parse(file_path)
    return input_root

def xsd_from_file(file_path):
    xmlschema_doc = etree.parse(file_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    return xmlschema

def validate_xml_xsd(xml_root, xsd):
    return xsd.validate(xml_root)

def parse_graph(input_root) -> Graph:
    '''
    Parses the input XML file and creates a Graph object from it.
    Assure that the input XML file is valid according to the XSD schema beforehand.
    '''
    
    graph: Graph = Graph()
    context = etree.iterwalk(input_root, events=("start", "end"))
    active_group = None
    active_node = None
        
    for action, elem in context:
        tag = elem.tag.removeprefix("{http://mergebench.org/ns}")
        res = False
        
        print("--------------------", end='\r')
        print("Graph: " + str(graph), end='\r')
        #print("Active Group: " + str(active_group))
        #print("Active Node: " + str(active_node))
        
        if action == "start":
            if tag == "Graph":
                continue
            if tag == "Group":
                active_group = Group(elem.get("name"))
                res = graph.add_group(active_group)
            if tag == "Node":
                active_node = Node(elem.get("name"))
                res = graph.add_node(active_node, active_group.name)
            if tag == "Property":
                res = graph.add_property(active_node.name, elem.get("name"))
            if tag == "DirectedEdge":
                res = graph.add_directed_edge(DirectedEdge(elem.get("start"), elem.get("end"), elem.get("semantics")))
                
        if action == "end":
            if tag == "Graph":
                continue
            if tag == "Group":
                active_group = None
                continue
            if tag == "Node":
                active_node = None
                continue
            if tag == "Property":
                continue
            if tag == "DirectedEdge":
                continue
                
        if not res:
            print("Could not process element while graph construction on-the-fly: %s" % tag)
            if elem is not None:
                print("Element: %s" % str(elem))
            print("Element: %s" % str(elem))
            print("Graph: " + str(graph))
            raise Exception("Parsing failed")
        
    print("Graph: " + str(graph))
    return graph

# Graph Modification Functions (directly based on XML operations metamodel)

def apply_delete_node(graph: Graph, elem) -> bool:
    node_name = elem.get("nodeName")
    group_name = elem.get("groupName")
    return graph.delete_node_and_references(group_name, node_name)

def apply_delete_directed_edge(graph: Graph, elem) -> bool:
    start = elem.get("start")
    end = elem.get("end")
    semantics = elem.get("semantics")
    return graph.delete_directed_edge(start, end, semantics)

def apply_delete_group(graph: Graph, elem) -> bool:
    group_name = elem.get("groupName")
    return graph.delete_group_and_references(group_name)

def apply_delete_property(graph: Graph, elem) -> bool:
    node_name = elem.get("nodeName")
    property_name = elem.get("propertyName")
    return graph.delete_property(node_name, property_name)

def apply_add_node(graph: Graph, elem) -> bool:
    node_name = elem.get("nodeName")
    group_name = elem.get("groupName")
    return graph.add_node(Node(node_name), group_name)

def apply_add_directed_edge(graph: Graph, elem) -> bool:
    start = elem.get("start")
    end = elem.get("end")
    semantics = elem.get("semantics")
    return graph.add_directed_edge(DirectedEdge(start, end, semantics))

def apply_add_group(graph: Graph, elem) -> bool:
    group_name = elem.get("groupName")
    return graph.add_group(Group(group_name))

def apply_rename_property(graph: Graph, elem) -> bool:
    nodeName = elem.get("nodeName")
    oldPropertyName = elem.get("oldPropertyName")
    newPropertyName = elem.get("newPropertyName")
    return graph.update_property(nodeName, oldPropertyName, newPropertyName)

def apply_add_property(graph: Graph, elem) -> bool:
    nodeName = elem.get("nodeName")
    propertyName = elem.get("propertyName")
    return graph.add_property(nodeName, propertyName)

def apply_rename_group(graph: Graph, elem) -> bool:
    oldGroupName = elem.get("oldGroupName")
    newGroupName = elem.get("newGroupName")
    return graph.rename_group_and_references(oldGroupName, newGroupName)

def apply_rename_node(graph: Graph, elem) -> bool:
    oldNodeName = elem.get("oldNodeName")
    newNodeName = elem.get("newNodeName")
    return graph.rename_node_and_references(oldNodeName, newNodeName)

def apply_change_semantics_directed_edge(graph: Graph, elem) -> bool:
    start = elem.get("start")
    end = elem.get("end")
    oldSemantics = elem.get("oldSemantics")
    newSemantics = elem.get("newSemantics")
    return graph.change_semantics_directed_edge(start, end, oldSemantics, newSemantics)

def apply_move_node_to_other_group(graph: Graph, elem) -> bool:
    nodeName = elem.get("nodeName")
    oldGroupName = elem.get("oldGroupName")
    newGroupName = elem.get("newGroupName")
    return graph.move_node_to_other_group(nodeName, oldGroupName, newGroupName)

def apply_join_groups(graph: Graph, elem):
    group1Name = elem.get("group1Name")
    group2Name = elem.get("group2Name")
    newGroupName = elem.get("newGroupName")
    return graph.join_groups(group1Name, group2Name, newGroupName)

def parse_and_apply_operations(input_root, graph: Graph):
    context = etree.iterwalk(input_root, events=("start", "end"))
    operations = ["DeleteNode", "DeleteDirectedEdge", "DeleteGroup", "DeleteProperty", "AddNode", "AddDirectedEdge",
                  "AddGroup", "RenameProperty", "AddProperty", "RenameGroup", "RenameNode", "ChangeSemanticsDirectedEdge", 
                  "MoveNodeToOtherGroup", "JoinGroups"]
    
    semantic_edits = {}
    current_semantic_edit_index = None
    current_operation_index = None
    
    print("--------------------")
    print("Parsing and applying operations")
    
    for action, elem in context:
        tag = elem.tag.removeprefix("{http://mergebench.org/ns}")    
        if action == "start":
            if tag == "SemanticEdit":    
                index = str(elem.get("index"))
                current_semantic_edit_index = index
                semantic_edits[index] = {}
            if tag == "Operation":
                current_operation_index = str(elem.get("index"))
            if tag in operations:
                print("Operation: %s" % tag)
                if current_semantic_edit_index is None:
                    raise Exception("Operation found outside of a SemanticEdit tag")
                if current_operation_index is None:
                    raise Exception("Operation found outside of an Operation tag")
                operation_index = current_operation_index
                semantic_edits[current_semantic_edit_index][operation_index] = elem
            
        if action == "end":
            if tag == "SemanticEdit":
                current_semantic_edit_index = None
            if tag == "Operation":
                current_operation_index = None
                
    semantic_edit_indices: list[int] = [int(index) for index in semantic_edits.keys()]
    semantic_edit_indices.sort()
    
    for semantic_edit_index in semantic_edit_indices:
        semantic_edit = semantic_edits[str(semantic_edit_index)]
        operation_keys = [int(key) for key in semantic_edit.keys()]
        operation_keys.sort()
        
        for operation_key in operation_keys:
            operation = semantic_edit[str(operation_key)]
            operation_tag = operation.tag.removeprefix("{http://mergebench.org/ns}")
            
            res = False
            if operation_tag == "DeleteNode":
                res = apply_delete_node(graph, operation)
            if operation_tag == "DeleteDirectedEdge":
                res = apply_delete_directed_edge(graph, operation)
            if operation_tag == "DeleteGroup":
                res = apply_delete_group(graph, operation)
            if operation_tag == "DeleteProperty":
                res = apply_delete_property(graph, operation)
            if operation_tag == "AddNode":
                res = apply_add_node(graph, operation)
            if operation_tag == "AddDirectedEdge":
                res = apply_add_directed_edge(graph, operation)
            if operation_tag == "AddGroup":
                res = apply_add_group(graph, operation)
            if operation_tag == "RenameProperty":
                res = apply_rename_property(graph, operation)
            if operation_tag == "AddProperty":
                res = apply_add_property(graph, operation)
            if operation_tag == "RenameGroup":
                res = apply_rename_group(graph, operation)
            if operation_tag == "RenameNode":
                res = apply_rename_node(graph, operation)
            if operation_tag == "ChangeSemanticsDirectedEdge":
                res = apply_change_semantics_directed_edge(graph, operation)
            if operation_tag == "MoveNodeToOtherGroup":
                res = apply_move_node_to_other_group(graph, operation)
            if operation_tag == "JoinGroups":
                res = apply_join_groups(graph, operation)
                
            if not res:
                print("Could not apply operation: %s" % operation_tag)
                print("Semantic Edit Index: %s" % semantic_edit_index)
                print("Operation Index: %s" % operation_key)
                print("Operation: %s" % str(operation))
                raise Exception("Operation failed")
        

def build_property_xml(property_name: str):
    property_elem = etree.Element("{http://mergebench.org/ns}Property")
    property_elem.set("name", property_name)
    return property_elem

def build_node_xml(node: Node):
    node_elem = etree.Element("{http://mergebench.org/ns}Node")
    node_elem.set("name", node.name)
    for property in node.properties:
        node_elem.append(build_property_xml(property))
    return node_elem

def build_group_xml(group: Group):
    group_elem = etree.Element("{http://mergebench.org/ns}Group")
    group_elem.set("name", group.name)
    for node in group.nodes:
        group_elem.append(build_node_xml(node))
    return group_elem

def build_directed_edge_xml(directed_edge: DirectedEdge):
    directed_edge_elem = etree.Element("{http://mergebench.org/ns}DirectedEdge")
    directed_edge_elem.set("start", directed_edge.start)
    directed_edge_elem.set("end", directed_edge.end)
    directed_edge_elem.set("semantics", directed_edge.semantics)
    return directed_edge_elem

def serialize_graph(graph: Graph, output_path: str, template_path: str):
    
    template = xml_from_file(template_path)
    
    context = etree.iterwalk(template, events=("start", "end"))
    template_graph = None   
        
    for action, elem in context:
        tag = elem.tag.removeprefix("{http://mergebench.org/ns}")
        if action == "start":
            if tag == "Graph":
                template_graph = elem
                break
            
    if template_graph is None:
        raise Exception("Could not find Graph element in template")
        
    for group in graph.groups:
        template_graph.append(build_group_xml(group))
        
    for directed_edge in graph.directed_edges:
        template_graph.append(build_directed_edge_xml(directed_edge))
    
    etree.indent(template, space="\t", level=0)
    template.write(output_path, encoding="utf-8", xml_declaration=True)
    

def main():
    first_arg_graph_xml = sys.argv[1]
    second_arg_graph_xsd = sys.argv[2]
    third_arg_operations_xml = sys.argv[3]
    fourth_arg_operations_xsd = sys.argv[4]
    fifth_arg_output_path = sys.argv[5]
    sixth_arg_template_path = sys.argv[6]
    
    graph_xml = xml_from_file(first_arg_graph_xml)
    graph_xsd = xsd_from_file(second_arg_graph_xsd)
    
    graph_is_valid = validate_xml_xsd(graph_xml, graph_xsd)
    print("Valid Graph: " + str(graph_is_valid))
    
    operations_xml = xml_from_file(third_arg_operations_xml)
    operations_xsd = xsd_from_file(fourth_arg_operations_xsd)
    
    operations_is_valid = validate_xml_xsd(operations_xml, operations_xsd)
    print("Valid Operations: " + str(operations_is_valid))
    
    graph = parse_graph(graph_xml)
    parse_and_apply_operations(operations_xml, graph)
    
    serialize_graph(graph, fifth_arg_output_path, sixth_arg_template_path)
    
if __name__ == "__main__":
    main()