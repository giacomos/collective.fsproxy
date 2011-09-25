def syncUpponProxyFolderCreation(mycontent, event):
    sync_view = mycontent.restrictedTraverse('@@resync')
    sync_view()

