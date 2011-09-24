from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

import re

class ProxyFileView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()

        self.context_path = '/'.join(self.context.getPhysicalPath())

    def downloadicon_name(self):
        """Given the currently selected platform, return the name of the
        name of the icon to use.

        This takes the form platform_${name}.gif, where ${name} is the
        platform name, in lowercase, with all non-alpha-numeric characters
        (including whitespace) converted to underscores.
        """
        return ''
        #return 'platform_%s.gif' % \
        #            re.sub(r'\W', '_', self.context.getPlatform()).lower()

    def file_size(self):
        """Return the file size of the download, or None if unknown.
        """
        try:
            return self.context.getObjSize(self.context)
        except RuntimeError: 
            # older products throwing RuntimeError: Filesystem Script (Python) getObjSize has errors.
            return None

    def direct_url(self):
        """Get the direct URL to the download.
        """
        #return '%s/getDownloadableFile' % self.absolute_url()
        return self.context.absolute_url() + '/download'
