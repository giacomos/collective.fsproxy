from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles
from config import ADD_PERMISSIONS

security = ModuleSecurityInfo('collective.fsproxy.permissions')

security.declarePublic("AddProxyFolder")
AddProxyFolder=ADD_PERMISSIONS['ProxyFolder']
setDefaultRoles(AddProxyFolder, ("Manager",))

security.declarePublic("AddProxyFile")
AddProxyFile=ADD_PERMISSIONS['ProxyFile']
setDefaultRoles(AddProxyFile, ("Manager", "Owner"))
