##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Implementation of Utility-baed Vocabulary Registry
"""
import zope.component
from zope.interface import implementer
from zope.interface.interfaces import ComponentLookupError
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IVocabularyRegistry


@implementer(IVocabularyRegistry)
class ZopeVocabularyRegistry:
    """IVocabularyRegistry that supports global and local utilities.

    For contexts that have associated local site manager (component registry),
    vocabularies are looked up there.  For all other contexts, vocabularies are
    looked up in the currently active local or global site manager.
    """
    __slots__ = ()

    def get(self, context, name):
        """See zope.schema.interfaces.IVocabularyRegistry"""

        # Find component registry for the context
        globalSiteManager = zope.component.getGlobalSiteManager()
        try:
            contextSiteManager = zope.component.getSiteManager(context)
        except ComponentLookupError:
            contextSiteManager = globalSiteManager

        if contextSiteManager is not globalSiteManager:
            # Context has an associated component registry, let's search
            # for vocabularies defined there.
            sm = contextSiteManager
        else:
            # Component registry for the context is either globalSiteManager,
            # or it is not found.
            #
            # Revert to default getUtility() behaviour - pick manager
            # for the active site, or fall back to global registry.
            sm = zope.component.getSiteManager()

        # Find the vocabulary factory
        factory = sm.queryUtility(IVocabularyFactory, name, None)
        if factory is None:
            raise vocabulary.VocabularyRegistryError(name)

        return factory(context)


vocabularyRegistry = None


def _clear():
    """Re-initialize the vocabulary registry."""
    # This should normally only be needed by the testing framework,
    # but is also used for module initialization.
    global vocabularyRegistry
    # The net effect of these two lines is to have this modules
    # vocabularyRegistry set to zope.schema.vocabulary.VocabularyRegistry()
    vocabulary._clear()
    vocabularyRegistry = vocabulary.getVocabularyRegistry()
    vocabulary._clear()
    # Which we immediately replace
    vocabulary.setVocabularyRegistry(ZopeVocabularyRegistry())


_clear()

try:
    from zope.testing import cleanup
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    cleanup.addCleanUp(_clear)
