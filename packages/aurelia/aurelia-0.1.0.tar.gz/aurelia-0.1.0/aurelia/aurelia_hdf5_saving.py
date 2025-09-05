"""
This script provides functionality to serialize Python dictionaries and class instances into HDF5 files using the ``h5py`` library. 
It supports nested structures, compresses NumPy arrays, and stores primitive types as attributes. 
These functions are used to save the simulations into .h5 files.
"""
import numpy as np
import h5py
import os

class DictGroup(h5py.Group):
    """
    A helper class that recursively stores dictionary contents into HDF5 groups and datasets.
    """
    def __init__(self, parent, name, data):
        super().__init__(parent, name)
        for key, value in data.items():
            self.__setitem__(key, value)
    
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            self.create_group(key)
            for subkey, subvalue in value.items():
                self[key].__setitem__(subkey, subvalue)
        else:
            self.create_dataset(key, data=value)

def convert_strings_to_utf8(obj):
    """
    This function recursively converts strings in objects to UTF-8 encoded bytes for HDF5 compatibility. 
    Handles strings, lists, tuples, dictionaries, and objects with ``__dict__``.
    """
    if isinstance(obj, str):
        return obj.encode('utf-8')
    elif isinstance(obj, (list, tuple)):
        return [convert_strings_to_utf8(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_strings_to_utf8(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        new_dict = obj.__dict__.copy()
        for attr_name, attr_value in new_dict.items():
            new_dict[attr_name] = convert_strings_to_utf8(attr_value)
        return new_dict
    else:
        return obj

def save_dict_to_hdf5(dict_obj, folderpath, filename, groupname):
    """
    Saves a dictionary into an HDF5 file.

    *args*:

    - ``dict_obj``: A python dictionary. Dictionary to save.
    - ``folderpath``: A string. Path to save the file.
    - ``filename``: A string. Name of the HDF5 file.
    - ``groupname``: A string. Name of the group inside the file.

    """
    dataset_types = [np.ndarray]
    attributes_types = [int,str,float,np.float32, np.float64, np.int64,tuple]
    dict_types = [dict]
    with h5py.File(os.path.join(folderpath,filename), 'a') as f:
        cls_group = f[groupname]
        for key,value in dict_obj.items():
            if type(value) in dataset_types:
            #if isinstance(attr_value, (int, float, str)): ## and numpy
                cls_group.create_dataset(key,data=value,compression="gzip")
            elif type(value) in attributes_types:
                cls_group.attrs[key] = value
            elif type(value) in dict_types:
                sub_group = cls_group.create_group(key)
                save_dict_to_hdf5(value,folderpath,filename, sub_group.name)


#class Class2H5:
def save_class_to_hdf5(obj,folderpath, filename, groupname=None):
    """
    Saves a class into an HDF5 file.

    *args*:

    - ``obj``: A python object. Object to save.
    - ``folderpath``: A string. Path to save the file.
    - ``filename``: A string. Name of the HDF5 file.
    - ``groupname``: A string. Name of the group inside the file.

    """
    # Open the HDF5 file for writing
    dataset_types = [np.ndarray]
    attributes_types = [int,str,float,np.float32, np.float64, np.int64,tuple]
    dict_types = [dict]
    with h5py.File(os.path.join(folderpath,filename), 'a') as f:
        # Create a group for the object's class with the name of the class
        if not groupname:
            cls_group = f.create_group(type(obj).__name__)
        else:
            cls_group = f[groupname]
        # Loop over the object's attributes and save them to the group
        for attr_name in dir(obj):
            if not attr_name.startswith('__') and  not callable(getattr(obj, attr_name)):
                attr_value = getattr(obj, attr_name)
                if type(attr_value) in dataset_types:
                #if isinstance(attr_value, (int, float, str)): ## and numpy
                    cls_group.create_dataset(attr_name,data=attr_value,compression="gzip")
                elif type(attr_value) in attributes_types:
                    cls_group.attrs[attr_name] = attr_value
                elif type(attr_value) in dict_types:
                    sub_group = cls_group.create_group(attr_name)
                    save_dict_to_hdf5(attr_value,folderpath,filename, sub_group.name)
                        # if isinstance(value, dict):
                        # # Create a subgroup for nested dictionaries
                        #     subgroup = cls_group.create_group(key)
                        #     save_class_to_hdf5(value, folderpath,filename, groupname=sub_group.name)
                        # else:
                        #     if isinstance(value, str):
                        #         # Check string length compatibility with HDF5
                        #         if len(value) > 32767:
                        #             # Truncate the string if it exceeds the limit
                        #             value = value[:32767]
                        #         # Encode the string as UTF-8 for HDF5 compatibility
                        #         value = value.encode('utf-8')
                        #     # Store non-dictionary values directly
                        #     f.create_dataset(key, data=value)
                else:
                    # Recursively save attributes of sub-objects -- this might crash though it it s looking for something that has subs but doesnt 
                    sub_group = cls_group.create_group(attr_name)
                    save_class_to_hdf5(attr_value, folderpath,filename, groupname=sub_group.name)



