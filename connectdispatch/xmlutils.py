"""The utils module contains functions to manipulate XML objects."""


def strip_xml_ns(el):
    """Recursively search specified element tree, removing namespaces."""
    if el.tag.startswith("{"):
        el.tag = el.tag.split('}', 1)[1]
    for k in el.attrib.keys():
        if k.startswith("{"):
            k2 = k.split('}', 1)[1]
            el.attrib[k2] = el.attrib[k]
            del el.attrib[k]
    for child in el:
        strip_xml_ns(child)
    return el


def xmltolist(xml, element):
    """Takes an XML object, iterates on the specified element, and returns a list of dictionaries with the element's
    child tag and text elements."""
    element_list = []
    for i in xml.iter(element):
        i_dict = {}
        for e in i.iter():
            i_dict[e.tag] = e.text
        element_list.append(i_dict)
    return element_list
