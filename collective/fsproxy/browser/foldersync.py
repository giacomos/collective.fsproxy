import os
import re
from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.statusmessages.interfaces import IStatusMessage
from plone.i18n.normalizer import idnormalizer




class FolderSyncView(BrowserView):

#    def __init__(self, context, request):
#        BrowserView.__init__(self, context, request)

    def emptyFolder(self):
        type_filter = {"portal_type" : ("Proxy File",'Proxy Folder')}
        contents = self.context.listFolderContents(contentFilter=type_filter)
        ids = [i.id for i in contents]
        self.context.manage_delObjects(ids)

    def __call__(self):
        if self.request.get('purge', False):
            self.emptyFolder()

        normalizer = getUtility(IIDNormalizer)
        field = self.context.getField('fsposition')
        path = field.get(self.context)
        self.scan_folder(self.context, path, recursive = self.context.getRecursive(), blacklist=self.context.getBlacklist())
        self.context.reindexObject()
        messages = IStatusMessage(self.request)
        messages.addStatusMessage(u"Folder resync completed", type="info")
        self.request.response.redirect(self.context.absolute_url())
#        import pdb;pdb.set_trace()

    def get_valid_id(self, new_id):
        while new_id.startswith('_') or new_id.startswith('.'):
            new_id = new_id[1:]
        if new_id.startswith('aq_'):
            new_id = new_id[len('aq_'):]
        if new_id.startswith('@@'):
            new_id = new_id[2:]
        new_id = new_id.replace('+','')
        if new_id == 'plone':
            new_id = new_id + '_'
        return new_id

    def blacklistSafe(self, blacklist, filename):
        bl_safe = True
        for e in blacklist:
            try:
                prog = re.compile(e.decode('string_escape'))
                if prog.search(filename):
                   bl_safe = False
            except:
                pass
        return bl_safe

    def scan_folder(self, container, path, recursive = False, blacklist = None):
        if blacklist == None:
            blacklisr = []
        count = 0
        files = os.listdir(path)
        for f in files:
            if not self.blacklistSafe(blacklist, f):
                continue
            if os.path.isdir(path + '/' + f) == True and recursive:
                new_id = self.get_valid_id(f)
                if new_id not in container.objectIds():
                    new_id = container.invokeFactory(id=new_id,type_name="Proxy Folder")
                obj = container[new_id]
                obj.setFsposition(path +'/'+ f)
                obj.setTitle(f)
                obj.setRecursive(True)
                count = count + self.scan_folder(obj, path + '/' + f, recursive=recursive, blacklist=blacklist)
            if os.path.isdir(path + '/' + f) == True:
                continue
            new_id = self.get_valid_id(f)
            if new_id.find('.') >= 1:
                fname,fext = new_id.rsplit('.',1)
            else:
                fname,fext = new_id,''
            new_id = idnormalizer.normalize(fname)
            new_id = fext and '.'.join([new_id, fext]) or new_id
            if new_id in container.objectIds():
                continue
            try:
                objId = container.invokeFactory(id=new_id,type_name="Proxy File")
                obj = container[objId]
                obj.setFsposition(path +'/'+ f)
                obj.setTitle(f)
                obj.reindexObject()
                count = count + 1
            except:
                continue
        return count
