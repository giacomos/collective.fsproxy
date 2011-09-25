def syncUpponProxyFolderCreation(mycontent, event):
    if mycontent.getField('fsposition').get(mycontent):
        mycontent.scan_folder()

