from five import grok
import lxml

from zope.interface import Interface
from silva.core.editor.transform.interfaces import ITransformer


class IFakeTarget(Interface):
    pass


class FakeTarget(object):
    grok.implements(IFakeTarget)


class Transformer(grok.MultiAdapter):
    grok.adapts(IFakeTarget, Interface)
    grok.implements(ITransformer)
    grok.provides(ITransformer)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def data(self, name, text, data, interface):
        return data

    def part(self, name, text, data, xpath, interface):
        trees = lxml.html.fromstring(data).xpath(xpath)
        result = []
        for tree in trees:
            result.append(lxml.html.tostring(tree))
        return result


