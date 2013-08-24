import os
import msvcrt

from . import const, util

class walker:
    def __init__(self, root):
        self.root = root
        self.keyboard_hit_exit = False

    def __iter__(self):
        return next(self)

    def create_partial_path(self, name, dirpath):
        p = os.path.join(dirpath, name)
        full_abs_path = os.path.abspath(p)
        root_abs_path = os.path.abspath(self.root)
        partial_path = full_abs_path.replace(root_abs_path, "")
        if partial_path[0] == util.get_folder_sep():
            # Generally these strings end up with an extra separator at the start we need to remove.
            # These should cover both Windows and Linux.
            partial_path = partial_path[1:]
        return partial_path

    def __next__(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            metadata_dir_name = const.METADATA_DIR_NAME
            # todo: also check that it's a hidden directory before we decide to remove it (at least in Windows)
            if metadata_dir_name in dirnames:
                # don't visit metadata directories (see os.walk docs - this is a little tricky)
                dirnames.remove(metadata_dir_name)

            # do the directories/folders first
            for name in dirnames:
                # note the separator delineates a folder/directory
                partial_path = self.create_partial_path(name, dirpath) + util.get_folder_sep()
                if self.check_exit():
                    break
                else:
                    yield partial_path

            for name in filenames:
                partial_path = self.create_partial_path(name, dirpath)
                if self.check_exit():
                    break
                else:
                    yield partial_path # just the part to the right of the 'root'

    # todo: get this working.
    # For some reason, msvcrt.kbhit() blocks.  It seems like it shouldn't
    def check_exit(self):
        return False # just don't allow forced exit for now ...
        #print("check_exit_start", self.keyboard_hit_exit)
        #if not self.keyboard_hit_exit:
        #    if msvcrt.kbhit():
        #        print ("keyboard interrupt")
        #        self.keyboard_hit_exit = True
        #print("check_exit_end", self.keyboard_hit_exit)
        #return(self.keyboard_hit_exit)

    def get_path(self, partial_path):
        #print(partial_path)
        p = os.path.join(self.root, partial_path)
        if partial_path[:-1] == util.get_folder_sep():
            # folder/directory
            p += util.get_folder_sep()
        #print(p)
        return p