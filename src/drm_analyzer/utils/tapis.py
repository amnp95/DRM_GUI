# %%
import argparse

parser = argparse.ArgumentParser(description='Upload files to Frontera')
parser.add_argument('--path', type=str, help='Path to the files')
args = parser.parse_args()
basepath = args.path

Clear = True
folderName = "DRM_MODEL"
from tapipy.tapis import Tapis
t = Tapis(base_url= "https://designsafe.tapis.io",
          username="",
          password="")
t.get_tokens()
# %%
# files = t.files.listFiles(systemId="frontera", path="HOST_EVAL($SCRATCH)" )
# %%
files = t.files.listFiles(systemId="frontera", path="/scratch1/08189/amnp95")
# check if there is folder names DRM_MODEL
flag = False
for File in files:
    if File.name == folderName:
        flag = True
        break
# %%
if not flag:
    t.files.mkdir(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}")
    files = t.files.listFiles(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}")
    print("Folder created")
else :
    files = t.files.listFiles(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}")
    print("Folder already exists")
    if Clear:
        for File in files:
            if File.name == "Mesh" or File.name == "Results":
                print(f"Deleting {File.name}")
                t.files.delete(systemId="frontera", path=f"/scratch1/08189/amnp95/{folderName}/{File.name}")
        print("Subfolders are cleared")
# %%
import os
print("basepath", basepath)
# add ever files in the folder  and its subfolders
for subpath in ["Mesh", "Results"]:
    path = basepath + "/" + subpath
    for root, dirs, files in os.walk(path):
        for File in files:
            # get relative root
            File = os.path.relpath(os.path.join(root, File), path)
            t.upload(source_file_path=os.path.join(path, File), system_id="frontera", dest_file_path=f"/scratch1/08189/amnp95/{folderName}/{subpath}/{File}")
print("Files are uploaded")
# %%
