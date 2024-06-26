from abc import ABC, abstractmethod
from contextlib import contextmanager, suppress
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from ichor.core.common.functools import buildermethod
from ichor.core.common.io import move
from ichor.core.common.types import NoStr
from ichor.core.files.path_object import PathObject


class FileReadError(Exception):
    pass


class FileState(Enum):
    """An enum that is used to make it easier to check the current file state.
    Blocked is actually not used currently."""

    Unread = 1
    Reading = 2
    Read = 3
    Blocked = -1


class FileContentsType(NoStr):
    """A class whose instance is used for class attributes that are read in from a file.
    If a class attribute is FileContents type, then we read the file and store the read in value.
    This class allows for lazily reading files (i.e. files are not directly read in when
    an instance of a File (or its subclasses) is made, but only when attributes of that
    instance (which are FileContents) are being accessed."""

    def __bool__(self):
        """FileContents instances must evaluate to False (as NoneType)."""
        return False

    def __str__(self):
        """
        More readable to print out as FileContents
        in stdout
        """

        return "FileContents"

    def __repr__(self):
        """
        More readable to print out as FileContents
        in stdout
        """

        return "FileContents"


# make an instance of FileContentsType which to use everywhere.
FileContents = FileContentsType()


class File(PathObject, ABC):
    """Abstract Base Class for any type of file that is used by ICHOR."""

    # default filetype is None
    # if there is no filetype, can leave as empty string as well
    _filetype = None

    # from https://stackoverflow.com/a/53769173
    def __init_subclass__(cls, **kwargs):
        if getattr(cls, "_filetype") is None:
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} without '_filetype' class variable defined."
            )
        return super().__init_subclass__(**kwargs)

    def __init__(self, path: Union[Path, str]):

        self.state = FileState.Unread
        # need to check if path exists here because if it does, we need to read in file contents
        super().__init__(path)

    @classmethod
    def check_path(cls, path: Union[str, Path]) -> bool:
        """Checks the suffix of the given path matches the filetype associated with class that subclasses from File
        :param path: A Path object to check
        :return: True if the Path object has the same suffix as the class filetype, False otherwise
        """
        path = Path(path)
        # add check if list of possible filetypes is given
        if isinstance(cls._filetype, (list, tuple)):
            for ty_ in cls._filetype:
                if path.suffix == ty_:
                    return True
            return False

        return cls._filetype == path.suffix

    @classmethod
    def get_filetype(cls) -> str:
        """Returns a filetype for the particular kind of file

        :return: A string containing the suffix of the file (the filetype)
        """

        # if multiple filetypes are given
        if isinstance(cls._filetype, (list, tuple)):
            return cls._filetype[0]

        return cls._filetype

    def move(self, dst):
        """Move the file to a new destination.

        :param dst: The new path to the file. If a directory, the file is moved inside the directory.
        """
        if dst.is_dir():
            # pathlib's Path class uses / operator to add to the path
            dst /= self.path.name
        move(self.path, dst)

    @contextmanager
    def block(self):
        """Blocks a file from being read. Contents of the file cannot be read."""
        self._save_state = self.state
        try:
            self.state = FileState.Blocked
            yield
        finally:
            self.unblock()

    def unblock(self):
        """Unblocks a blocked file."""
        if self.state is FileState.Blocked:
            self.state = self._save_state

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"


class ReadFile(File, ABC):

    _filetype = ""

    def _initialise_contents(self):
        """Initialize contents of a file to default values. This is needed in the case
        a file does not exist on disk yet (so the file cannot be read from). This means
        that the read method (and subsequently self._read_file) is not called.

        Example: If a gjf file does not exist, then gjf_file.link0 will be FileContents.
        But then we cannot do things like gjf_file.set_nproc(2) because it will try to add
        an element to FileContents and will crash.
        """
        pass

    @buildermethod
    def read(self, *args, **kwargs):
        """Read the contents of the file. Depending on the type of file, different parts will be read in.

        .. note::
            Only files which exist on disk can be read from. Otherwise, nothing will be read in.
        """
        if self.state is FileState.Unread:
            self.state = FileState.Reading
            self._initialise_contents()
            if self.path.exists():
                self._read_file(
                    *args, **kwargs
                )  # self._read_file is different based on which type of file is being read (GJF, AIMALL, etc.)
                # else:
                #     raise FileNotFoundError(f"File with path path {self.path}
                # of type {self.__class__.__name__} does not exist on disk.") # todo: talk to yulian about this
                self.state = FileState.Read
            else:
                self.state = FileState.Unread

    @abstractmethod
    def _read_file(self, *args, **kwargs):
        """Abstract method detailing how to read contents of a file. Every type of file (gjf, int, etc.)
        is written in a different format and contains different information, so every file reading is
        different."""
        raise NotImplementedError(
            f"'_read_file' not implemented for '{self.__class__.__name__}'"
        )

    def __getattribute__(self, item):
        """This is what gets called when accessing an attribute of an instance.
        Here, we check if the attribute exists or not.

        If the attribute does not exist, then read the file and update its filestate.
        Then try to return the value of the attribute, if the attribute still does not exist
        after reading the file, then return an AttributeError.

        One must be careful to make sure all attributes that want to be accessed
        lazily must be an attribute of the class and not to override __getattribute__
        in subclasses of PathObject.

        :param item: The attribute that needs to be accessed.
        """

        # check if the attribute has value FileContents, if not read file

        with suppress(AttributeError):
            if object.__getattribute__(self, item) is FileContents:
                self.read()

        try:
            return object.__getattribute__(self, item)
        except AttributeError as e:
            raise AttributeError(f"{self} does not have attribute {item}.") from e

    def __getitem__(self, item):
        """Tries to return the item indexed with [] brackets.
        If the item does not exist and the filestate is Unread, then read the file
        and try to access the item again. If the item still does not exist, then throw a KeyError."""
        try:
            return super().__getitem__(item)
        except (KeyError, AttributeError):
            if self.state is FileState.Unread:
                self.read()
                return self.__getitem__(item)
        raise KeyError(f"No '{item}' item found for '{self.path}'")


class FileWriteError(Exception):
    pass


class WriteFile(File, ABC):

    _filetype = ""

    def _set_write_defaults_if_needed(self):
        """Set default values for attributes if bool(self.attribute) evaluates to False.
        So if an attribute is still FileContents, an empty string, an empty list, etc.,
        then default values will be used."""
        pass

    def _check_values_before_writing(self):
        """This check is just here so that the file is read before attempting to write the file.
        This is to prevent a situation where the original file has not been read yet,
        but a new file with the same path is being written
        (so therefore the new file is empty and all the data has been
        lost and has not been read in into an instance yet).

        ..note::
            Even though the file could already be read in and some attributes might be modified by the user,
            reading the file a second time prior to writing will not change any user attributes because of the
            way the read file is written (i.e. any user-set attributes are kept even after the file is read again).

        Can be used to check the values prior to writing. If the values do not meet
        the requirements, an error is thrown out. This is to prevent writing out files
        that are then going to crash in calculations with other programs.
        """
        pass

    @abstractmethod
    def _write_file(self, path: Path, *args, **kwargs) -> str:
        """Each sub-class should return a string which is the contents of the file to be written out.

        :param path: path of file
        :type path: Path
        """
        raise NotImplementedError(
            f"'_write_file' not implemented for '{self.__class__.__name__}'"
        )

    def write(self, path: Optional[Union[Path, str]] = None, *args, **kwargs):
        """This write method should only be called if no other write method exists. A
        write method is implemented for files that we typically write out (such as
        .xyz or .gjf files). But other files (which are outputs of a program, such as .wfn,
        and .int), we only need to read and do not have to write out ourselves."""
        path = Path(path or self.path)
        if not path:
            raise ValueError(
                f"Path where contents will be written is not allowed, value of path: {path}."
            )

        try:
            self._set_write_defaults_if_needed()
            self._check_values_before_writing()
            # try to put the contents into a string, if that is ok, then write to file
            tmp_str = self._write_file(path, *args, **kwargs)

        # raise warning, but do not remove the file
        # this way, if the file already exists on disk, it will not be overwritten.
        except Exception as e:
            raise FileWriteError(
                f"Exception occurred while writing file '{path.absolute()}'. File was not been written/modified."
            ) from e

        if tmp_str:
            # if we got to here, we can safely assume that we got a string which can be written to a file
            # even if the actual string contains wrong things it it
            with open(path, "w") as f:
                f.write(tmp_str)
        else:
            raise TypeError("The contents type cannot be written to a file.")
