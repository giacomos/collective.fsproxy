"""Definition of the Proxy Folder content type
"""
import os
import transaction
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from collective.fsproxy.interfaces import IProxyFolder
from collective.fsproxy.config import PROJECTNAME
from collective.fsproxy import fsproxyMessageFactory as _
from AccessControl import ClassSecurityInfo

ProxyFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='fsposition',
        required=1,
        validators = ( "isValidFilesystemPath", ),
        widget=atapi.StringWidget(
            label=_(u"label_file_fs_position", default=u"Filesystem position for file to proxy"),
            description=_(u"help_file_position", default=u"Please enter the filesystem position where the file is."),
            i18n_domain="collective.fsproxy",
        ),
    ),

    atapi.BooleanField('recursive',
        required=0,
        widget=atapi.BooleanWidget(
            label=_(u"label_recursive", default=u"Recursive Search"),
            description=_(u"description_recursive", default=u"Include files in subfolders recursively."),
            i18n_domain="collective.fsproxy",
        ),
    ),

    atapi.LinesField('blacklist',
        multiValued=1,
        required=0,
        widget=atapi.LinesWidget(
                label=_(u"label_blacklist", default=u"Blacklist"),
                        description=_(u"help_blacklist", default=u"..."),
                        i18n_domain="collective.fsproxy",
                    ),
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ProxyFolderSchema['title'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['title'].required = False
ProxyFolderSchema['description'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['fsposition'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['fsposition'].widget.visible = {'edit': 'visible', 'view': 'invisible'}
ProxyFolderSchema['recursive'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['recursive'].widget.visible = {'edit': 'visible', 'view': 'invisible'}
ProxyFolderSchema['blacklist'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['blacklist'].widget.visible = {'edit': 'visible', 'view': 'invisible'}

schemata.finalizeATCTSchema(
    ProxyFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class ProxyFolder(folder.ATFolder):
    """Description of the Example Type"""
    implements(IProxyFolder)

    meta_type = "ProxyFolder"
    schema = ProxyFolderSchema
    _at_rename_after_creation = True

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    fsposition = atapi.ATFieldProperty('fsposition')
    recursive = atapi.ATFieldProperty('recursive')
    blacklist = atapi.ATFieldProperty('blacklist')
    security = ClassSecurityInfo()
    
    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """Renames an object like its normalized title.
        """
        path = self.getField('fsposition').get(self)
        if not path:
            # Can't work w/o a title
            return False
#        pu = getToolByName(self, 'plone_utils')
#        new_id = pu.normalizeString(self.filename())
        new_id = self.filename()
        invalid_id = False
        check_id = getattr(self, 'check_id', None)
        if check_id is not None:
            invalid_id = check_id(new_id, required=1)
        else:
            # If check_id is not available just look for conflicting ids
            parent = aq_parent(aq_inner(self))
            invalid_id = new_id in parent.objectIds()

        if not invalid_id:
            # Can't rename without a subtransaction commit when using
            # portal_factory!
            transaction.commit()
            self.setId(new_id)
            self.setTitle(new_id)
            self.reindexObject()
            return new_id

    def filename(self):
        path = self.getField('fsposition').get(self)
        filename = path.split('/')[-1]
        return filename

atapi.registerType(ProxyFolder, PROJECTNAME)
