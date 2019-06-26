import errno
import os
from datetime import datetime

from django.conf import settings
from django.core.files import File, locks
from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.utils._os import safe_join
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri, force_text
from django.utils.six.moves.urllib.parse import urljoin


@deconstructible
class RemoteStorage(FileSystemStorage):
    """
    A "remote" storage that does not support the ``path`` method.

    This is just FileSystemStorage with ``path`` renamed ``_path``.
    """

    def path(self, filename):
        raise NotImplementedError("This backend doesn't support absolute paths.")

    def _open(self, name, mode='rb'):
        return File(open(self._path(name), mode))

    def _save(self, name, content):
        full_path = self._path(name)

        # Create any intermediate directories that do not exist.
        # Note that there is a race between os.path.exists and os.makedirs:
        # if os.makedirs fails with EEXIST, the directory was created
        # concurrently, and we can continue normally. Refs #16082.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                if self.directory_permissions_mode is not None:
                    # os.makedirs applies the global umask, so we reset it,
                    # for consistency with file_permissions_mode behavior.
                    old_umask = os.umask(0)
                    try:
                        os.makedirs(directory, self.directory_permissions_mode)
                    finally:
                        os.umask(old_umask)
                else:
                    os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                # This file has a file path that we can move.
                if hasattr(content, 'temporary_file_path'):
                    file_move_safe(content.temporary_file_path(), full_path)

                # This is a normal uploadedfile that we can stream.
                else:
                    # This fun binary flag incantation makes os.open throw an
                    # OSError if the file already exists before we open it.
                    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             getattr(os, 'O_BINARY', 0))
                    # The current umask value is masked out by os.open!
                    fd = os.open(full_path, flags, 0o666)
                    _file = None
                    try:
                        locks.lock(fd, locks.LOCK_EX)
                        for chunk in content.chunks():
                            if _file is None:
                                mode = 'wb' if isinstance(chunk, bytes) else 'wt'
                                _file = os.fdopen(fd, mode)
                            _file.write(chunk)
                    finally:
                        locks.unlock(fd)
                        if _file is not None:
                            _file.close()
                        else:
                            os.close(fd)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    name = self.get_available_name(name)
                    full_path = self._path(name)
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if self.file_permissions_mode is not None:
            os.chmod(full_path, self.file_permissions_mode)

        # Store filenames with forward slashes, even on Windows.
        return force_text(name.replace('\\', '/'))

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        name = self._path(name)
        # If the file exists, delete it from the filesystem.
        # If os.remove() fails with ENOENT, the file may have been removed
        # concurrently, and it's safe to continue normally.
        try:
            os.remove(name)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def exists(self, name):
        return os.path.exists(self._path(name))

    def listdir(self, path):
        path = self._path(path)
        directories, files = [], []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                directories.append(entry)
            else:
                files.append(entry)
        return directories, files

    def _path(self, name):
        return safe_join(self.location, name)

    def size(self, name):
        return os.path.getsize(self._path(name))

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        url = filepath_to_uri(name)
        if url is not None:
            url = url.lstrip('/')
        return urljoin(self.base_url, url)

    def _datetime_from_timestamp(self, ts):
        """
        If timezone support is enabled, make an aware datetime object in UTC;
        otherwise make a naive one in the local timezone.
        """
        if settings.USE_TZ:
            # Safe to use .replace() because UTC doesn't have DST
            return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(ts)

    def get_accessed_time(self, name):
        return self._datetime_from_timestamp(os.path.getatime(self.path(name)))

    def get_created_time(self, name):
        return self._datetime_from_timestamp(os.path.getctime(self.path(name)))

    def get_modified_time(self, name):
        return self._datetime_from_timestamp(os.path.getmtime(self.path(name)))
