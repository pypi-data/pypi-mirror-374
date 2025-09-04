"""Various types of DataFiles that have been read back from messages in a topic"""

# imports
import pathlib, os
from hashlib import sha512
from contextlib import nullcontext
from abc import ABC, abstractmethod
from ..config import DATA_FILE_HANDLING_CONST
from .data_file import DataFile


class DownloadDataFile(DataFile, ABC):
    """
    Class to represent a data file that will be read as messages from a topic

    :param filepath: Path to the file
    :type filepath: :class:`pathlib.Path`
    """

    #################### PROPERTIES AND STATIC METHODS ####################

    @staticmethod
    def get_full_filepath(dfc):
        """
        Return the full filepath of a downloaded file given one of its DataFileChunks

        :param dfc: One of the DataFileChunk objects contributing to the file
        :type dfc: :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk`

        :return: the full path to the file
        :rtype: :class:`pathlib.Path`
        """
        if dfc.filename_append == "":
            return dfc.filepath
        return dfc.filepath.with_name(
            dfc.filepath.stem + dfc.filename_append + dfc.filepath.suffix
        )

    @property
    @abstractmethod
    def bytestring(self):
        """
        A bytestring of the data contained in the file. Not implemented in the base class.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def check_file_hash(self):
        """
        The hash of the data in the file after it was read. Not implemented in the base class.
        """
        raise NotImplementedError

    @property
    def relative_filepath(self):
        """
        The path to the file, relative to its root directory
        """
        if self.subdir_str == "":
            return pathlib.Path(self.filename)
        return pathlib.Path(self.subdir_str + "/" + self.filename)

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self, filepath, *args, **kwargs):
        super().__init__(filepath, *args, **kwargs)
        # start an empty set of this file's downloaded offsets
        self._chunk_offsets_downloaded = []
        self.full_filepath = None
        self.subdir_str = None
        self.n_total_chunks = None

    def add_chunk(self, dfc, thread_lock=nullcontext()):
        """
        Process a chunk that's been read from a topic.
        Returns a number of codes based on what effect adding the chunk had.

        This function calls :func:`~_on_add_chunk`,
        with the :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk` as the argument.

        :param dfc: the DataFileChunk object whose data should be added
        :type dfc: :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk`
        :param thread_lock: the lock object to acquire/release so that race conditions
            don't affect reconstruction of the files
            (only needed if running this function asynchronously)
        :type thread_lock: :class:`threading.Lock`, optional

        :return: an internal code indicating whether the chunk: was successfully added to
            a file in progress, was already received, was the last chunk needed and
            the file is successfully reconstructed according to its hash or the
            post-reconstruction hash is mismatched to the hash of the file contents
            originally read from disk.
        :rtype: int
        """
        # if this chunk's offset has already been written to disk, return the "already written" code
        with thread_lock:
            already_written = dfc.chunk_offset_write in self._chunk_offsets_downloaded
        if already_written:
            return DATA_FILE_HANDLING_CONST.CHUNK_ALREADY_WRITTEN_CODE
        # the filepath of this DownloadDataFile and of the given DataFileChunk must match
        if dfc.filepath != self.filepath:
            errmsg = (
                f"ERROR: filepath mismatch between data file chunk with {dfc.filepath} "
                f"and data file with {self.filepath}"
            )
            self.logger.error(errmsg, exc_type=ValueError)
        # modify the filepath to include any append to the name
        full_filepath = self.__class__.get_full_filepath(dfc)
        if self.full_filepath is None:
            self.full_filepath = full_filepath
            self.filename = self.full_filepath.name
        elif self.full_filepath != full_filepath:
            errmsg = (
                f"ERROR: filepath for data file chunk {dfc.chunk_i}/{dfc.n_total_chunks} "
                f"with offset {dfc.chunk_offset_write} is {full_filepath} but the file "
                f"being reconstructed is expected to have filepath {self.full_filepath}"
            )
            self.logger.error(errmsg, exc_type=ValueError)
        # add the subdirectory string to this file
        if self.subdir_str is None:
            self.subdir_str = dfc.subdir_str
        elif self.subdir_str != dfc.subdir_str:
            errmsg = (
                f"Mismatched subdirectory strings! From file = {self.subdir_str}, "
                f"from chunk = {dfc.subdir_str}"
            )
            self.logger.error(errmsg, exc_type=ValueError)
        # set or check the total number of chunks expected
        if self.n_total_chunks is None:
            with thread_lock:
                self.n_total_chunks = dfc.n_total_chunks
        elif self.n_total_chunks != dfc.n_total_chunks:
            errmsg = (
                f"ERROR: {self.__class__.__name__} with filepath {self.full_filepath} "
                f"is expecting {self.n_total_chunks} chunks but found a chunk from a split "
                f"with {dfc.n_total_chunks} total chunks."
            )
            self.logger.error(errmsg, exc_type=ValueError)
        with thread_lock:
            # call the function to actually add the chunk
            self._on_add_chunk(dfc)
            # add the offset of the added chunk to the set of reconstructed file chunks
            self._chunk_offsets_downloaded.append(dfc.chunk_offset_write)
            last_chunk = len(self._chunk_offsets_downloaded) == dfc.n_total_chunks
        # if this chunk was the last that needed to be added, check the hashes
        if last_chunk:
            if self.check_file_hash != dfc.file_hash:
                return DATA_FILE_HANDLING_CONST.FILE_HASH_MISMATCH_CODE
            return DATA_FILE_HANDLING_CONST.FILE_SUCCESSFULLY_RECONSTRUCTED_CODE
        return DATA_FILE_HANDLING_CONST.FILE_IN_PROGRESS

    #################### PRIVATE HELPER FUNCTIONS ####################

    @abstractmethod
    def _on_add_chunk(self, dfc):
        """
        A function to actually process a new chunk being added to the file.
        This function is executed while a thread lock is acquired so it will never
        run asynchronously. Also any DataFileChunks passed to this function are
        guaranteed to have unique offsets.

        Not implemented in the base class.

        :param dfc: the DataFileChunk object whose data should be added
        :type dfc: :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk`
        """
        raise NotImplementedError


class DownloadDataFileToDisk(DownloadDataFile):
    """
    Class to represent a data file that will be reconstructed on disk
    using messages read from a topic

    :param filepath: Path to the file
    :type filepath: :class:`pathlib.Path`
    """

    #################### CONSTANTS ####################

    READ_BUFFER_SIZE = 4096

    #################### PROPERTIES ####################

    @property
    def bytestring(self):
        """
        A bytestring of the data in the file
        """
        with open(self.full_filepath, "rb") as fp:
            data = fp.read()
        return data

    @property
    def check_file_hash(self):
        """
        Hash of the file contents as read from its current location on disk
        """
        check_file_hash = sha512()
        with open(self.full_filepath, "rb") as fp:
            while True:
                data = fp.read(self.READ_BUFFER_SIZE)
                if not data:
                    break
                check_file_hash.update(data)
        return check_file_hash.digest()

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self, filepath, *args, **kwargs):
        super().__init__(filepath, *args, **kwargs)
        # create the parent directory of the file if it doesn't exist yet
        if not self.filepath.parent.is_dir():
            self.filepath.parent.mkdir(parents=True)

    def _on_add_chunk(self, dfc):
        """
        Add the data from a given file chunk to this file on disk

        :param dfc: the DataFileChunk object whose data should be added
        :type dfc: :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk`
        """
        try:
            super()._on_add_chunk(dfc)
        except NotImplementedError:
            pass
        mode = "r+b" if self.full_filepath.is_file() else "w+b"
        with open(self.full_filepath, mode) as fp:
            fp.seek(dfc.chunk_offset_write)
            fp.write(dfc.data)
            fp.flush()
            os.fsync(fp.fileno())
            fp.close()


class DownloadDataFileToMemory(DownloadDataFile):
    """
    Class to represent a data file that will be held in memory
    and populated by the contents of messages from a topic

    :param filepath: Path to the file
    :type filepath: :class:`pathlib.Path`
    """

    #################### PROPERTIES ####################

    @property
    def bytestring(self):
        """
        The bytestring of the file contents (like calling file_pointer.read() for a file
        opened in "rb" mode). Call bytestring.decode() to convert this to a text string.
        """
        if self.__bytestring is None:
            self.__create_bytestring()
        return self.__bytestring

    @bytestring.setter
    def bytestring(self, new_bytestring):
        if self.__bytestring is not None:
            warnmsg = (
                f"WARNING: resetting a non-None bytestring for {self.__class__.__name__} "
                f"with path {self.filepath}"
            )
            self.logger.warning(warnmsg)
        self.__bytestring = new_bytestring

    @property
    def check_file_hash(self):
        """
        The hash of the file contents determined from the bytestring of the file stored in memory
        """
        check_file_hash = sha512()
        check_file_hash.update(self.bytestring)
        return check_file_hash.digest()

    #################### PUBLIC FUNCTIONS ####################

    def __init__(self, filepath, *args, **kwargs):
        super().__init__(filepath, *args, **kwargs)
        # start a dictionary of the file data by their offsets
        self.__chunk_data_by_offset = {}
        # placeholder for the eventual full data bytestring
        self.__bytestring = None

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _on_add_chunk(self, dfc):
        """
        Add the data from a given file chunk to the dictionary of data by offset

        :param dfc: the DataFileChunk object whose data should be added
        :type dfc: :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk`
        """
        try:
            super()._on_add_chunk(dfc)
        except NotImplementedError:
            pass
        self.__chunk_data_by_offset[dfc.chunk_offset_write] = dfc.data

    def __create_bytestring(self):
        """
        Makes all of the data held in the dictionary into a single bytestring
        """
        bytestring = b""
        for data in [
            self.__chunk_data_by_offset[offset]
            for offset in sorted(self.__chunk_data_by_offset.keys())
        ]:
            bytestring += data
        self.__bytestring = bytestring


class DownloadDataFileToMemoryAndDisk(DownloadDataFileToMemory, DownloadDataFileToDisk):
    """
    A file that's written to disk as its messages are read
    from a topic, while also having a bytestring created for it.

    :param filepath: Path to the file
    :type filepath: :class:`pathlib.Path`
    """

    @property
    def check_file_hash(self):
        """
        Hash of the file contents as read from its current location on disk
        and from the bytestring of the file stored in memory.
        Raises an error if they don't match.
        """
        check_file_hash_memory = sha512()
        check_file_hash_memory.update(self.bytestring)
        check_file_hash_memory = check_file_hash_memory.digest()
        check_file_hash_disk = sha512()
        with open(self.full_filepath, "rb") as fp:
            while True:
                data = fp.read(self.READ_BUFFER_SIZE)
                if not data:
                    break
                check_file_hash_disk.update(data)
        check_file_hash_disk = check_file_hash_disk.digest()
        if check_file_hash_disk != check_file_hash_memory:
            errmsg = (
                f"ERROR: hashes of file on disk and in memory are mismatched! "
                f"On disk: {check_file_hash_disk}. In memory: {check_file_hash_memory}."
            )
            self.logger.error(errmsg, exc_type=ValueError)
        return check_file_hash_disk

    def __init__(self, filepath, *args, **kwargs):
        super().__init__(filepath, *args, **kwargs)
