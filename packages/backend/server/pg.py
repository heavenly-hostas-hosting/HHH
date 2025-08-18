import os

import psycopg
from psycopg.rows import tuple_row


async def get_connection() -> psycopg.AsyncConnection:
    return await psycopg.AsyncConnection.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        row_factory=tuple_row,
    )


async def github_files_create_table() -> None:
    async with await get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS github_files (
                    id SERIAL PRIMARY KEY,
                    github_username VARCHAR(39) NOT NULL,
                    filename CHAR(42) NOT NULL,
                    commit_hash CHAR(40) NOT NULL
                );
                """
            )
            await conn.commit()


async def github_files_insert_row(username: str, filename: str, commit_hash: str) -> None:
    await github_files_create_table()

    async with await get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO github_files (github_username, filename, commit_hash)
                VALUES (%s, %s, %s);
                """,
                (username, filename, commit_hash),
            )
            await conn.commit()


async def github_files_check_exists(filename: str, commit_hash: str) -> bool:
    async with await get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT
                    *
                FROM
                    github_files
                WHERE
                    filename=%s
                    AND commit_hash=%s
                """,
                (filename, commit_hash),
            )

            rows = await cur.fetchall()
            return len(rows) == 1


async def github_files_get_all() -> list[tuple[str, str]]:
    async with await get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT
                    github_username,
                    filename
                FROM
                    github_files
                ORDER BY
                    id ASC
                """
            )
            rows = await cur.fetchall()
            return rows
