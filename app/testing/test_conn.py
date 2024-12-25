from unittest.mock import patch

from app.models.conn import create_tables, drop_tables


def test_create_table():
    with patch("app.models.conn.Base.metadata.create_all") as mock_create_all:
        create_tables()
        mock_create_all.assert_called_once()


def test_drop_table():
    with patch("app.models.conn.Base.metadata.drop_all") as mock_drop_all:
        drop_tables()
        mock_drop_all.assert_called_once()
