import os
import pytest
import pytest_asyncio
import json

from sparrow.archive.archiver import create_archive, import_archive, list_archives
from sparrow.database import Database
from sparrow.models import Trace


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.init()
    yield database
    await database.close()


@pytest_asyncio.fixture
async def db_with_traces(db):
    async with db.session() as session:
        for i in range(10):
            session.add(
                Trace(
                    request_method="POST",
                    request_path="/v1/chat/completions",
                    model_name="gpt-4o" if i % 2 == 0 else "gpt-3.5-turbo",
                    status="success",
                    is_streaming=False,
                    prompt_tokens=i * 10,
                    completion_tokens=i * 5,
                    total_tokens=i * 15,
                )
            )
        await session.commit()
    return db


class TestArchive:
    @pytest.mark.asyncio
    async def test_create_archive_all(self, db_with_traces, tmp_path):
        archive_dir = str(tmp_path / "archives")
        path = await create_archive(db_with_traces, archive_dir)
        assert path.endswith(".tar.gz")
        assert os.path.exists(path)

        import tarfile

        with tarfile.open(path, "r:gz") as tar:
            names = tar.getnames()
            assert "metadata.json" in names
            assert "traces.jsonl" in names

            meta_f = tar.extractfile("metadata.json")
            metadata = json.loads(meta_f.read())
            assert metadata["trace_count"] == 10

    @pytest.mark.asyncio
    async def test_create_archive_deletes_traces(self, db_with_traces, tmp_path):
        from sqlalchemy import select, func

        archive_dir = str(tmp_path / "archives")
        await create_archive(db_with_traces, archive_dir)

        async with db_with_traces.session() as session:
            result = await session.execute(select(func.count(Trace.id)))
            assert result.scalar() == 0

    @pytest.mark.asyncio
    async def test_import_archive(self, db_with_traces, tmp_path):
        archive_dir = str(tmp_path / "archives")
        path = await create_archive(db_with_traces, archive_dir)

        count = await import_archive(db_with_traces, path)
        assert count == 10

        from sqlalchemy import select, func

        async with db_with_traces.session() as session:
            result = await session.execute(select(func.count(Trace.id)))
            assert result.scalar() == 10

    @pytest.mark.asyncio
    async def test_import_no_duplicates(self, db_with_traces, tmp_path):
        archive_dir = str(tmp_path / "archives")
        path = await create_archive(db_with_traces, archive_dir)

        count1 = await import_archive(db_with_traces, path)
        assert count1 == 10

        count2 = await import_archive(db_with_traces, path)
        assert count2 == 0

    @pytest.mark.asyncio
    async def test_empty_archive(self, db, tmp_path):
        archive_dir = str(tmp_path / "archives")
        path = await create_archive(db, archive_dir)
        assert path == ""

    @pytest.mark.asyncio
    async def test_list_archives(self, db_with_traces, tmp_path):
        archive_dir = str(tmp_path / "archives")
        await create_archive(db_with_traces, archive_dir)

        archives = await list_archives(archive_dir)
        assert len(archives) == 1
        assert archives[0]["trace_count"] == 10
