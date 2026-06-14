import pytest
import pytest_asyncio

from sparrow.database import Database
from sparrow.models import Trace, truncate_body


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.init()
    yield database
    await database.close()


class TestTruncateBody:
    def test_none(self):
        assert truncate_body(None, 100) is None

    def test_small_body(self):
        assert truncate_body("hello", 100) == "hello"

    def test_exact_size(self):
        body = "a" * 100
        assert truncate_body(body, 100) == body

    def test_truncated(self):
        body = "a" * 200
        result = truncate_body(body, 100)
        assert result.endswith("[TRUNCATED]")
        assert len(result.encode("utf-8")) < 200


class TestDatabase:
    @pytest.mark.asyncio
    async def test_insert_and_read_trace(self, db):
        async with db.session() as session:
            trace = Trace(
                request_method="POST",
                request_path="/v1/chat/completions",
                request_body='{"model":"gpt-4o"}',
                response_status=200,
                response_body='{"usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}',
                model_name="gpt-4o",
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                cost=0.000175,
                status="success",
                is_streaming=False,
            )
            session.add(trace)
            await session.commit()
            await session.refresh(trace)

            assert trace.id is not None
            assert trace.request_method == "POST"
            assert trace.model_name == "gpt-4o"

    @pytest.mark.asyncio
    async def test_query_traces(self, db):
        async with db.session() as session:
            for i in range(5):
                session.add(
                    Trace(
                        request_method="POST",
                        request_path=f"/v1/chat/completions",
                        model_name="gpt-4o" if i % 2 == 0 else "gpt-3.5-turbo",
                        status="success",
                        is_streaming=False,
                    )
                )
            await session.commit()

        from sqlalchemy import select, func

        async with db.session() as session:
            result = await session.execute(select(func.count(Trace.id)))
            total = result.scalar()
            assert total == 5

            result = await session.execute(
                select(Trace).where(Trace.model_name == "gpt-4o")
            )
            gpt4o = result.scalars().all()
            assert len(gpt4o) == 3
