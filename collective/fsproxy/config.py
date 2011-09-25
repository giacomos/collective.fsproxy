"""Common configuration constants
"""

PROJECTNAME = 'collective.fsproxy'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'ProxyFolder': 'collective.fsproxy: Add Proxy Folder',
    'ProxyFile': 'collective.fsproxy: Add Proxy File',
}


ADD_INDEXES = [
    ('getKeywordsToAssign', 'KeywordIndex'),
]
