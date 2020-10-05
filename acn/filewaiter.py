# https://stackoverflow.com/a/35925746

import os, time, glob 

class FileWaiter:

    def __init__(self, path):
        self.path = path
        self.files = set(glob.glob(path))

    def wait_new_file(self, timeout):
        """
        Waits for a new file to be created and returns the new file path.
        """
        endtime = time.time() + timeout
        while True:
            diff_files = set(glob.glob(self.path)) - self.files
            if diff_files:
                new_file = diff_files.pop()
                try:
                    os.rename(new_file, new_file)
                    self.files = set(glob.glob(self.path))
                    return new_file
                except:
                    pass
            if time.time() > endtime:
                    raise Exception("Timeout while waiting for a new file in %s" % self.path)
            time.sleep(0.1)