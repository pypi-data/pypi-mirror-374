=====================================
 Component-based Vocabulary Registry
=====================================

This package provides a vocabulary registry for zope.schema,
based on the component architecture.

It replaces the zope.schema's simple vocabulary registry
when ``zope.vocabularyregistry`` package is imported, so it's done
automatically. All we need is provide vocabulary factory
utilities:

  >>> import zope.vocabularyregistry
  >>> from zope.component import provideUtility
  >>> from zope.schema.interfaces import IVocabularyFactory
  >>> from zope.schema.vocabulary import SimpleTerm
  >>> from zope.schema.vocabulary import SimpleVocabulary

  >>> def makeVocabularyFactory(*values):
  ...     def vocabularyFactory(context=None):
  ...         terms = [SimpleTerm(v) for v in values]
  ...         return SimpleVocabulary(terms)
  ...     return vocabularyFactory

  >>> zope.component.provideUtility(
  ...     makeVocabularyFactory(1, 2), IVocabularyFactory,
  ...     name='SomeVocabulary')

Now we can get the vocabulary using standard zope.schema
way:

  >>> from zope.schema.vocabulary import getVocabularyRegistry
  >>> vr = getVocabularyRegistry()
  >>> voc = vr.get(None, 'SomeVocabulary')
  >>> [term.value for term in voc]
  [1, 2]


If vocabulary is not found, VocabularyRegistryError is raised.

  >>> try:
  ...     vr.get(None, 'NotAvailable')
  ... except LookupError as error:
  ...     print("%s.%s: %s" % (error.__module__, error.__class__.__name__, error))
  zope.schema.vocabulary.VocabularyRegistryError: unknown vocabulary: 'NotAvailable'


We can also use vocabularies defined in local component registries.
Let's define some local sites with a vocabulary.

  >>> import zope.component.hooks
  >>> from zope.component import globalregistry
  >>> from zope.component.globalregistry import getGlobalSiteManager

  >>> from zope.interface.registry import Components
  >>> class LocalSite(object):
  ...   def __init__(self, name):
  ...      self.sm = Components(
  ...          name=name, bases=(globalregistry.getGlobalSiteManager(), ))
  ...
  ...   def getSiteManager(self):
  ...       return self.sm

  >>> local_site_even = LocalSite('local_site_even')
  >>> local_site_even.sm.registerUtility(
  ...     makeVocabularyFactory(4, 6, 8), IVocabularyFactory,
  ...     name='SomeVocabulary', event=False)

  >>> local_site_odd = LocalSite('local_site_odd')
  >>> local_site_odd.sm.registerUtility(
  ...     makeVocabularyFactory(3, 5, 7), IVocabularyFactory,
  ...     name='SomeVocabulary', event=False)


Vocabularies defined in local component registries can be accessed
in two ways.

1. Using the registry from within a site.

  >>> with zope.component.hooks.site(local_site_even):
  ...     voc = getVocabularyRegistry().get(None, 'SomeVocabulary')
  ...     [term.value for term in voc]
  [4, 6, 8]

2. Binding to a context that can be used to look up a local site manager.

  >>> from zope.interface.interfaces import IComponentLookup
  >>> zope.component.provideAdapter(
  ...    lambda number: ((local_site_even, local_site_odd)[number % 2]).sm,
  ...    adapts=(int, ), provides=IComponentLookup)

  >>> context = 4
  >>> voc = getVocabularyRegistry().get(context, 'SomeVocabulary')
  >>> [term.value for term in voc]
  [4, 6, 8]

Binding to a context takes precedence over active site, so we can look
up vocabularies from other sites.

  >>> context = 7
  >>> with zope.component.hooks.site(local_site_even):
  ...     voc = getVocabularyRegistry().get(context, 'SomeVocabulary')
  ...     [term.value for term in voc]
  [3, 5, 7]


If we cannot find a local site for given context, currently active
site is used.

  >>> from zope.interface.interfaces import ComponentLookupError
  >>> def raisingGetSiteManager(context=None):
  ...    if context == 42:
  ...        raise ComponentLookupError(context)
  ...    return zope.component.hooks.getSiteManager(context)
  >>> hook = zope.component.getSiteManager.sethook(raisingGetSiteManager)

  >>> context = 42
  >>> with zope.component.hooks.site(local_site_odd):
  ...     voc = getVocabularyRegistry().get(context, 'SomeVocabulary')
  ...     [term.value for term in voc]
  [3, 5, 7]


Configuration
=============

This package provides configuration that ensures the vocabulary
registry is established:


  >>> from zope.configuration import xmlconfig
  >>> _ = xmlconfig.string(r"""
  ... <configure xmlns="http://namespaces.zope.org/zope" i18n_domain="zope">
  ...   <include package="zope.vocabularyregistry" />
  ... </configure>
  ... """)
