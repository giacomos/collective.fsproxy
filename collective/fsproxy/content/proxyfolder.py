"""Definition of the Proxy Folder content type
"""
import os
import re
import transaction
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from collective.fsproxy.interfaces import IProxyFolder
from collective.fsproxy.config import PROJECTNAME
from collective.fsproxy import fsproxyMessageFactory as _
from AccessControl import ClassSecurityInfo
from plone.i18n.normalizer import idnormalizer

pathseparator = os.path.normcase('/')

ProxyFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    
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
                        description=_(u"help_blacklist", default=u"Regular expressions to filter files by name."),
                        i18n_domain="collective.fsproxy",
                    ),
        schemata="import rules",
    ),
    
    atapi.BooleanField('aquireBlacklist',
        required=0,
        default=True,
        widget=atapi.BooleanWidget(
            label=_(u"label_aquire_blacklist", default=u"Aquire blacklist"),
            description=_(u"description_aquire_blacklist", default=u"If enabled the blacklist will be extended from parent Proxy Folders."),
            i18n_domain="collective.fsproxy",
        ),
        schemata="import rules",
    ),

    atapi.LinesField('keywordsToAssign',
        multiValued=1,
        required=0,
        widget=atapi.LinesWidget(
                label=_(u"label_blacklist", default=u"Auto keywords"),
                        description=_(u"help_blacklist", default=u"Auto assign these keywords to imported files. These keywords are also aquired from parent Proxy Folders."),
                        i18n_domain="collective.fsproxy",
                    ),
        schemata="import rules",
    ),
    
))

ProxyFolderSchema['title'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['description'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['blacklist'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['fsposition'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['recursive'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['keywordsToAssign'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['aquireBlacklist'].storage = atapi.AnnotationStorage()
ProxyFolderSchema['title'].required = False
ProxyFolderSchema['fsposition'].widget.visible = {'edit': 'visible', 'view': 'invisible'}
ProxyFolderSchema['recursive'].widget.visible = {'edit': 'visible', 'view': 'invisible'}
ProxyFolderSchema['blacklist'].widget.visible = {'edit': 'visible', 'view': 'invisible'}

schemata.finalizeATCTSchema(
    ProxyFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class ProxyFolder(folder.ATFolder):
    """ """
    implements(IProxyFolder)

    meta_type = "ProxyFolder"
    schema = ProxyFolderSchema
    _at_rename_after_creation = True

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    fsposition = atapi.ATFieldProperty('fsposition')
    recursive = atapi.ATFieldProperty('recursive')
    blacklist = atapi.ATFieldProperty('blacklist')
    keywordsToAssign = atapi.ATFieldProperty('keywordsToAssign')
    aquireBlacklist = atapi.ATFieldProperty('aquireBlacklist')
    security = ClassSecurityInfo()
    
    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """Renames an object like its normalized title.
        """
        path = self.getField('fsposition').get(self)
        if not path:
            return False
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
        filename = path.split(pathseparator)[-1]
        return filename
    
    def get_valid_zope_id(self, new_id):
        """ Returns a valid zope id by removing unvalid chars """
        while new_id.startswith('_') or new_id.startswith('.'):
            new_id = new_id[1:]
        if new_id.startswith('aq_'):
            new_id = new_id[len('aq_'):]
        if new_id.startswith('@@'):
            new_id = new_id[2:]
        new_id = new_id.replace('+','')
        if new_id == 'plone':
            new_id = new_id + '_'
        if new_id.find('.') >= 1:
            fname, fext = new_id.rsplit('.', 1)
        else:
            fname, fext = new_id,''
        new_id = idnormalizer.normalize(fname)
        new_id = fext and '.'.join([new_id, fext]) or new_id
        return new_id

    def getAquiredBlacklist(self):
        """ Builds a blacklist aquiring from parents"""
        parent = self
        bl = []
        if self.getField('aquireBlacklist').get(self):
            while parent and IProxyFolder.providedBy(parent):
                bl = bl + list(parent.getField('blacklist').get(parent))
                parent = parent.aq_parent
        else:
            bl = list(parent.getField('blacklist').get(parent))
        return bl

    def getIcon(self, context):
        return self.portal_url() + "/folder_icon.gif"

    def getAquiredKeywords(self):
        """ Builds a blacklist aquiring from parents"""
        parent = self
        kwa = []
        while parent and IProxyFolder.providedBy(parent):
            kwa = kwa + list(parent.getField('keywordsToAssign').get(parent))
            parent = parent.aq_parent
        return list(set(kwa))

    def blacklistSafe(self, filename):
        """ Checks if the file name is the aquired blacklist. """
        bl_safe = True
        bl = self.getAquiredBlacklist()
        for e in bl:
            try:
                prog = re.compile(e.decode('string_escape'))
                if prog.search(filename):
                    bl_safe = False
            except:
                pass
        return bl_safe

    def addProxy(self, new_id, title, portal_type, absolute_path):
        try:
            if not new_id in self.objectIds():
                new_id = self.invokeFactory(id=new_id, type_name=portal_type)
                obj = self[new_id]
                obj.setFsposition(absolute_path)
                obj.setTitle(title)
                obj.setSubject(self.getAquiredKeywords())
                obj.reindexObject()
                return 1
            else:
                return 0
        except:
            return 0

    def scan_folder(self):
        """ Scans the relative path in the fs and, if the recursion is enabled,
        scans subfolders too
        """
        count = 0
        path = self.getField('fsposition').get(self)
        recursive = self.getField('recursive').get(self)
        files = os.listdir(path)
        for f in files:
            if not self.blacklistSafe(f):
                continue
            new_id = self.get_valid_zope_id(f)
            absolute_path = pathseparator.join([path, f])
            isDirectory = os.path.isdir(absolute_path) == True
            if  isDirectory and recursive:
                count = count + self.addProxy(new_id, f, "Proxy Folder", absolute_path)
                obj = self[new_id]
                obj.setRecursive(True)
                count = count + obj.scan_folder()
                obj.reindexObject()
            if not isDirectory:
                count = count + self.addProxy(new_id, f, "Proxy File", absolute_path)
        return count
atapi.registerType(ProxyFolder, PROJECTNAME)
