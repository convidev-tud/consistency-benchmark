from lxml import etree
import sys

def xml_from_file(file_path):
    input_root = etree.parse(file_path)
    return input_root

def xsd_from_file(file_path):
    xmlschema_doc = etree.parse(file_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    return xmlschema

def validate_xml_xsd(xml_root, xsd):
    return xsd.validate(xml_root)

def xml_to_puml(input_root):
    puml = ""
    context = etree.iterwalk(input_root, events=("start", "end"))
    for action, elem in context:
        tag = elem.tag.removeprefix("{http://mergebench.org/ns}")
        
        if action == "start":
            if tag == "Graph":
                puml += "@startuml\n"
            if tag == "Group":
                puml += "package %s {\n" % elem.get("name")
            if tag == "Node":
                puml += "object %s {\n" % elem.get("name")
            if tag == "Property":
                puml += elem.get("name") + "\n"
            if tag == "DirectedEdge":
                puml += "%s --> %s : %s\n" % (elem.get("start"), elem.get("end"), elem.get("semantics"))
            
        if action == "end":
            if tag == "Graph":
                puml += "@enduml\n"
            if tag == "Group":
                puml += "}\n"
            if tag == "Node":
                puml += "}\n"
        
    print("generated puml:\n %s" % puml)
    return puml

def main():
    first_arg_xml = sys.argv[1]
    second_arg_xsd = sys.argv[2]
    third_arg_output = sys.argv[3]
    
    xml = xml_from_file(first_arg_xml)
    xsd = xsd_from_file(second_arg_xsd)
    
    is_valid = validate_xml_xsd(xml, xsd)
    print("Valid input:" + str(is_valid))
    
    puml_string = xml_to_puml(xml)
    
    output_file = open(third_arg_output, "w")
    output_file.write(puml_string)
    output_file.close()
    
if __name__ == "__main__":
    main()