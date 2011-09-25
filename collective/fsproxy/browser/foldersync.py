from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

class FolderSyncView(BrowserView):

    def emptyFolder(self):
        type_filter = {"portal_type" : ("Proxy File",'Proxy Folder')}
        contents = self.context.listFolderContents(contentFilter=type_filter)
        ids = [i.id for i in contents]
        self.context.manage_delObjects(ids)

    def __call__(self):
        if self.request.get('purge', False):
            self.emptyFolder()

        count = self.context.scan_folder()
        self.context.reindexObject()
        messages = IStatusMessage(self.request)
        messages.addStatusMessage(u"Folder resync completed. Items added: %d" % count, type="info")
        self.request.response.redirect(self.context.absolute_url())
