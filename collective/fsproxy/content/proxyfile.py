"""Definition of the Proxy File content type
"""
import os
import mimetypes
import transaction
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from collective.fsproxy.interfaces import IProxyFile
from collective.fsproxy.config import PROJECTNAME
from collective.fsproxy import fsproxyMessageFactory as _
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from plone.app.blob.subtypes.file import ExtensionBlobField 

pathseparator = os.path.normcase('/')

ProxyFileSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='fsposition',
        required=1,
        validators=('isValidFilesystemFile',),
        widget=atapi.StringWidget(
            label=_(u"label_file_fs_position", default=u"Filesystem position for file to proxy"),
            description=_(u"help_file_position", default=u"Please enter the filesystem position where the file is."),
            i18n_domain="collective.fsproxy",
        ),
    ),

))

ProxyFileSchema['title'].storage = atapi.AnnotationStorage()
ProxyFileSchema['title'].required = False
ProxyFileSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ProxyFileSchema, moveDiscussion=False)


class ProxyFile(base.ATCTFileContent):
    """Description of the Example Type"""
    implements(IProxyFile)

    meta_type = "ProxyFile"
    schema = ProxyFileSchema
    _at_rename_after_creation = True

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    security = ClassSecurityInfo()

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """Renames an object like its normalized title.
        """
        path = self.getField('fsposition').get(self)
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

    def post_validate(self, REQUEST=None, errors=None):
        pass

    @property
    def data(self):
        return self.get_data()

    def get_data(self):
        if self.file_exists():
            tmp = self.get_file()
            return tmp.read()
        else:
            return ''

    def file_exists(self):
        try:
            open(self.getField('fsposition','r').get(self))
            return True
        except IOError as e:
            return False
    def get_file(self):
        return open(self.getField('fsposition','r').get(self))
               

    security.declareProtected(View, 'size')
    def file_size(self):
        """Get size (image_view.pt)
        """
        try:
            path = self.getField('fsposition').get(self)
            return os.path.getsize(path)
        except:
            return 0

    def filename(self):
        path = self.getField('fsposition').get(self)
        filename = path.split(pathseparator)[-1]
        return filename

    def mime_type(self):
        failed = 'text/x-unknown-content-type'
        field = self.getField('fsposition')
        path = field.get(self)
        if mimetypes.guess_type(path) == (None,None):
            return failed
        return mimetypes.guess_type(path)[0]

    def getIcon(self, context):
        mtr = getToolByName(self, 'mimetypes_registry')
        res = mtr.lookup(self.mime_type())
        if len(res):
            return res[0].icon_path
        else:
            return "application.png"
    def mimetype_name(self):
        mtr = getToolByName(self, 'mimetypes_registry')
        res = mtr.lookup(self.mime_type())
        if len(res):
            return res[0].name()
        else:
            return "application"

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (use default index_html)
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getField('fsposition')
        path = field.get(self)
        tmp = open(path, 'r')
        RESPONSE.setHeader("Content-type",self.mime_type()) 
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.filename())
#        RESPONSE.setHeader('Content-Length', len(str(sdata))) 
        return RESPONSE.write(tmp.read())

    def getPrimaryField(self):
        return ExtensionBlobField()

    def getFile(self):
        return self

#    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
#        pass
        return self.download()


    security.declareProtected(View, 'get_content_type')
    def get_content_type(self):
        field = self.getField('fsposition')
        path = field.get(self)
        tmp = open(path, 'r')
        return len(tmp.read())

atapi.registerType(ProxyFile, PROJECTNAME)
