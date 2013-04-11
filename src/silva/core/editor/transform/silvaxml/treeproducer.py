
from lxml import etree
from lxml.sax import _getNsTag


def saxify(element, producer, namespaces={}, prefixes={}):
    """Generate SAX-like events out of an lxml element. This is
    expected to be used with an XMLExport producer, that is not 100%
    pure SAX.
    """
    tag = element.tag
    if tag in (etree.Comment, etree.ProcessingInstruction):
        if element.tail:
            producer.characters(element.tail)
        return

    if prefixes and not namespaces:
        namespaces = {n: p for p, n in prefixes.items()}

    new_prefixes = []
    all_namespaces = namespaces.copy()
    all_prefixes = prefixes.copy()

    def check_namespace_prefix(namespace):
        if namespace is not None and namespace not in all_namespaces:
            prefix = namespace.rstrip('/').split('/')[-1]
            if not prefix or prefix in all_prefixes:
                prefix = 'ns{0:02}'.format(len(all_namespaces))
            new_prefixes.append((namespace, prefix))
            all_namespaces[namespace] = prefix
            all_prefixes[prefix] = namespace

    attributes_values = {}
    attributes = element.items()
    if attributes:
        for ns_name, value in attributes:
            namespace, name = _getNsTag(ns_name)
            check_namespace_prefix(namespace)
            attributes_values[(namespace, name)] = value

    tag_namespace, tag_name = _getNsTag(tag)
    check_namespace_prefix(tag_namespace)

    for namespace, prefix,  in new_prefixes:
        producer.startPrefixMapping(prefix, namespace)

    producer.startElementNS(tag_namespace, tag_name, attributes_values)
    if element.text:
        producer.characters(element.text)

    for child in element:
        saxify(child, producer, all_namespaces)

    producer.endElementNS(tag_namespace, tag_name)
    for namespace, prefix in new_prefixes:
        producer.endPrefixMapping(namespace)
    if element.tail:
        producer.characters(element.tail)

