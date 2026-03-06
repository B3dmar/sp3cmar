"""Tests for symlink-safe file operations."""

from pathlib import Path
from unittest.mock import patch

import pytest

from sp3cmar.exceptions import PathTraversalError, Sp3cMarError, SymlinkError
from sp3cmar.utils.files import (
    safe_mkdir,
    safe_read_text,
    safe_rmdir,
    safe_unlink,
    safe_write_text,
)


class TestSafeWriteText:
    """Test safe_write_text rejects symlinks."""

    def test_safe_write_rejects_symlink(self, tmp_path: Path):
        """
        Given: A symlink pointing to a target file
        When: safe_write_text is called on the symlink path
        Then: SymlinkError is raised and target file is unchanged
        """
        target = tmp_path / "sensitive_file.txt"
        target.write_text("original content")
        symlink = tmp_path / "symlink.txt"
        symlink.symlink_to(target)

        with pytest.raises(SymlinkError, match="Refusing to write to symlink"):
            safe_write_text(symlink, "malicious content")

        assert target.read_text() == "original content"

    def test_safe_write_works_on_regular_file(self, tmp_path: Path):
        """
        Given: A regular file path
        When: safe_write_text is called
        Then: File content is written successfully
        """
        file_path = tmp_path / "normal.txt"

        safe_write_text(file_path, "content")

        assert file_path.read_text() == "content"

    def test_safe_write_creates_new_file(self, tmp_path: Path):
        """
        Given: A path that doesn't exist
        When: safe_write_text is called
        Then: File is created with content
        """
        file_path = tmp_path / "new_file.txt"
        assert not file_path.exists()

        safe_write_text(file_path, "new content")

        assert file_path.exists()
        assert file_path.read_text() == "new content"

    def test_safe_write_overwrites_existing_file(self, tmp_path: Path):
        """
        Given: An existing regular file
        When: safe_write_text is called
        Then: File content is overwritten
        """
        file_path = tmp_path / "existing.txt"
        file_path.write_text("old content")

        safe_write_text(file_path, "new content")

        assert file_path.read_text() == "new content"

    def test_safe_write_rejects_symlink_to_directory(self, tmp_path: Path):
        """
        Given: A symlink pointing to a directory
        When: safe_write_text is called on the symlink path
        Then: SymlinkError is raised
        """
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        symlink = tmp_path / "symlink_to_dir"
        symlink.symlink_to(target_dir)

        with pytest.raises(SymlinkError, match="Refusing to write to symlink"):
            safe_write_text(symlink, "content")


class TestSafeReadText:
    """Test safe_read_text rejects symlinks."""

    def test_safe_read_rejects_symlink(self, tmp_path: Path):
        """
        Given: A symlink pointing to a target file
        When: safe_read_text is called on the symlink path
        Then: SymlinkError is raised
        """
        target = tmp_path / "sensitive_file.txt"
        target.write_text("secret content")
        symlink = tmp_path / "symlink.txt"
        symlink.symlink_to(target)

        with pytest.raises(SymlinkError, match="Refusing to read from symlink"):
            safe_read_text(symlink)

    def test_safe_read_works_on_regular_file(self, tmp_path: Path):
        """
        Given: A regular file with content
        When: safe_read_text is called
        Then: Content is returned
        """
        file_path = tmp_path / "normal.txt"
        file_path.write_text("file content")

        result = safe_read_text(file_path)

        assert result == "file content"

    def test_safe_read_raises_on_missing_file(self, tmp_path: Path):
        """
        Given: A path that doesn't exist
        When: safe_read_text is called
        Then: FileNotFoundError is raised
        """
        file_path = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            safe_read_text(file_path)


class TestSafeExists:
    """Test safe_exists doesn't follow symlinks."""

    def test_safe_exists_returns_false_for_symlink(self, tmp_path: Path):
        """
        Given: A symlink pointing to an existing target
        When: safe_exists is called
        Then: Returns False (symlink itself is rejected)
        """
        from sp3cmar.utils.files import safe_exists

        target = tmp_path / "target.txt"
        target.write_text("content")
        symlink = tmp_path / "symlink.txt"
        symlink.symlink_to(target)

        # safe_exists should reject symlinks
        assert safe_exists(symlink) is False

    def test_safe_exists_returns_true_for_regular_file(self, tmp_path: Path):
        """
        Given: A regular file
        When: safe_exists is called
        Then: Returns True
        """
        from sp3cmar.utils.files import safe_exists

        file_path = tmp_path / "regular.txt"
        file_path.write_text("content")

        assert safe_exists(file_path) is True

    def test_safe_exists_returns_false_for_nonexistent(self, tmp_path: Path):
        """
        Given: A path that doesn't exist
        When: safe_exists is called
        Then: Returns False
        """
        from sp3cmar.utils.files import safe_exists

        file_path = tmp_path / "nonexistent.txt"

        assert safe_exists(file_path) is False


class TestSafeUnlink:
    """Test safe_unlink rejects symlinks."""

    def test_safe_unlink_removes_regular_file(self, tmp_path: Path):
        f = tmp_path / "test.md"
        f.write_text("content")

        safe_unlink(f)

        assert not f.exists()

    def test_safe_unlink_rejects_symlink(self, tmp_path: Path):
        target = tmp_path / "real.md"
        target.write_text("content")
        link = tmp_path / "link.md"
        link.symlink_to(target)

        with pytest.raises(SymlinkError, match="symlink"):
            safe_unlink(link)

        assert target.exists()
        assert link.is_symlink()

    def test_safe_unlink_raises_on_missing(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            safe_unlink(tmp_path / "nonexistent.md")


class TestSafeRmdir:
    """Test safe_rmdir rejects symlinks."""

    def test_safe_rmdir_removes_empty_dir(self, tmp_path: Path):
        d = tmp_path / "empty"
        d.mkdir()

        safe_rmdir(d)

        assert not d.exists()

    def test_safe_rmdir_rejects_symlink(self, tmp_path: Path):
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        link_dir = tmp_path / "link"
        link_dir.symlink_to(real_dir)

        with pytest.raises(SymlinkError, match="symlink"):
            safe_rmdir(link_dir)

        assert real_dir.exists()
        assert link_dir.is_symlink()

    def test_safe_rmdir_raises_on_nonempty(self, tmp_path: Path):
        d = tmp_path / "nonempty"
        d.mkdir()
        (d / "file.txt").write_text("content")

        with pytest.raises(OSError):
            safe_rmdir(d)


class TestSafeMkdir:
    """Test safe_mkdir rejects symlinks."""

    def test_safe_mkdir_creates_directory(self, tmp_path: Path):
        d = tmp_path / "newdir"

        safe_mkdir(d)

        assert d.is_dir()

    def test_safe_mkdir_rejects_symlink(self, tmp_path: Path):
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real_dir)

        with pytest.raises(SymlinkError, match="symlink"):
            safe_mkdir(link)

    def test_safe_mkdir_creates_parents(self, tmp_path: Path):
        d = tmp_path / "a" / "b" / "c"

        safe_mkdir(d, parents=True)

        assert d.is_dir()

    def test_safe_mkdir_exist_ok(self, tmp_path: Path):
        d = tmp_path / "existing"
        d.mkdir()

        safe_mkdir(d, exist_ok=True)

        assert d.is_dir()


class TestSp3cMarErrorHierarchy:
    """Test exception hierarchy."""

    def test_symlink_error_is_sp3cmar_error(self):
        assert issubclass(SymlinkError, Sp3cMarError)

    def test_path_traversal_error_is_sp3cmar_error(self):
        assert issubclass(PathTraversalError, Sp3cMarError)

    def test_sp3cmar_error_is_exception(self):
        assert issubclass(Sp3cMarError, Exception)

    def test_catch_sp3cmar_error_catches_symlink(self):
        with pytest.raises(Sp3cMarError):
            raise SymlinkError("test")

    def test_catch_sp3cmar_error_catches_path_traversal(self):
        with pytest.raises(Sp3cMarError):
            raise PathTraversalError("test")


class TestAtomicWrite:
    """Test atomic write behavior."""

    def test_atomic_write_no_partial_on_failure(self, tmp_path: Path):
        """If write fails mid-stream, target file should not be left corrupted."""
        target = tmp_path / "target.txt"
        target.write_text("original")

        with (
            patch("os.replace", side_effect=OSError("disk full")),
            pytest.raises(OSError, match="disk full"),
        ):
            safe_write_text(target, "new content")

        assert target.read_text() == "original"

    def test_atomic_write_cleans_temp_on_failure(self, tmp_path: Path):
        """Temp file should be cleaned up after failure."""
        target = tmp_path / "target.txt"

        with (
            patch("os.replace", side_effect=OSError("disk full")),
            pytest.raises(OSError, match="disk full"),
        ):
            safe_write_text(target, "content")

        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0, f"Temp files not cleaned up: {tmp_files}"
