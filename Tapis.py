# %%
Clear = True
folderName = "DRM_MODEL"
from tapipy.tapis import Tapis
t = Tapis(base_url= "https://designsafe.tapis.io",
          username="amnp95",
          password="031121329413481373@Ap")
t.get_tokens()
# %%
# files = t.files.listFiles(systemId="frontera", path="HOST_EVAL($SCRATCH)" )
# %%
files = t.files.listFiles(systemId="frontera", path="/scratch1/08189/amnp95" )
# check if there is folder names DRM_MODEL
flag = False
for file in files:
    if file.name == folderName:
        flag = True
        break
if not flag:
    t.files.mkdir(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}")
    print("Folder created")
else :
    print("Folder already exists")
    if Clear:
        t.files.delete(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}")
        print("Folder cleared")
        t.files.mkdir(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}")
        print("Folder created")
# %%
files = t.files.listFiles(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}" )
for file in files:
    print(file.name)
# %%
