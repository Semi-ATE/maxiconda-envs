#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time

from maxiconda import supported_subdirs

SUBDIR_SLEEP = 2*60  # 2 minutes
PACKAGE_SLEEP = 10  # seconds

def release():
    """
    This function uploads the packages in `./build` to anaconda.org/Semi-ATE.
    It uses the `CONDA_UPLOAD_TOKEN` and `MAXICONDA_ENV_RELEASE` environment
    variables to do so.
    Returns
    -------
    bool (True for success, False for failure)
    """
    
    build_version = os.getenv('MAXICONDA_ENV_RELEASE', "0.0.0")
    repo_root = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
    build_root = os.path.join(repo_root, "build")

    if build_version == "0.0.0":
        print("Can not upload v0.0.0 as it is a test build")
        return
    else:
        print(f"Uploading : (v{build_version})")

    for subdir in supported_subdirs:
        upload_dir = os.path.join(build_root, subdir)
        print(f"  {subdir} : ", end="", flush=True)
        os.environ["CONDA_SUBDIR"] = subdir
        if os.path.exists(upload_dir):
            upload_files = os.listdir(upload_dir)
            files_to_upload = 0
            for upload_file in upload_files:
                if upload_file.endswith(".tar.bz2") and (build_version in upload_file):
                    files_to_upload += 1
            if files_to_upload == 0:
                print(f"nothing to upload. ('build/{subdir}' is empty)")
            else:
                print("")
                for upload_file in upload_files:
                    if upload_file.endswith(".tar.bz2") and (build_version in upload_file):
                        do_upload(os.path.join(upload_dir, upload_file))
                        time.sleep(PACKAGE_SLEEP)                        
            time.sleep(SUBDIR_SLEEP)
        else:
            print(f"nothing to upload. ('build/{subdir}' does not exist)")

def do_upload(fpath):
    """
    This function uploads the file pointed to by `fpath` (that is guaranteed
    to exist to anaconda.org/Semi-ATE.
    It uses the `CONDA_UPLOAD_TOKEN` variable to do so.
    
    Returns
    -------
    /
    """
    fname = os.path.basename(fpath)

    print(f"    {fname} : ", end="", flush=True)
    
    retval = True
    cmd = ["anaconda", "-t", os.environ.get("CONDA_UPLOAD_TOKEN", "Woops"), "upload", "-u", "semi-ate", fpath, "--force"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, output = p.communicate()
    output_lines = output.decode("utf-8").split("\n")  

    for output_line in output_lines:
        if "[ERROR]" in output_line:
            retval = False
            
    if retval == False:
        print("Failed.")
    else:
        print("Done.")

    
if __name__ == '__main__':
    release()
