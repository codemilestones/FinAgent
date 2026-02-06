"""
SQLite 缓存实现

提供基于 SQLite 的本地缓存功能。
"""

import json
import pickle
import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd


class BaseCache(ABC):
    """缓存抽象基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """设置缓存"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """删除缓存"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空缓存"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass


class SQLiteCache(BaseCache):
    """
    SQLite 缓存实现

    支持 TTL 自动过期、统计功能和数据序列化。
    """

    # 默认 TTL 配置
    DEFAULT_TTL = {
        "stock_info": 30 * 24 * 3600,  # 30 天
        "history": 7 * 24 * 3600,  # 7 天
        "dividend": 24 * 3600,  # 1 天
        "financial": 24 * 3600,  # 1 天
    }

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化缓存

        Args:
            db_path: 数据库文件路径，默认 ~/.finagent/cache.db
        """
        if db_path is None:
            cache_dir = Path.home() / ".finagent"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(cache_dir / "cache.db")

        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地数据库连接"""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(
                self.db_path, check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self) -> None:
        """初始化数据库表结构"""
        conn = self._get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                value_type TEXT NOT NULL,
                expire_time REAL NOT NULL,
                created_at REAL NOT NULL
            )
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                hits INTEGER DEFAULT 0,
                misses INTEGER DEFAULT 0
            )
        """
        )

        # 初始化统计
        conn.execute("INSERT OR IGNORE INTO stats (id) VALUES (1)")
        conn.commit()

    def _serialize(self, value: Any) -> tuple[bytes, str]:
        """
        序列化值

        Args:
            value: 要序列化的值

        Returns:
            (序列化后的字节, 值类型)
        """
        if isinstance(value, pd.DataFrame):
            return pickle.dumps(value), "dataframe"
        elif isinstance(value, (dict, list, str, int, float, bool, type(None))):
            return json.dumps(value).encode("utf-8"), "json"
        else:
            return pickle.dumps(value), "pickle"

    def _deserialize(self, data: bytes, value_type: str) -> Any:
        """
        反序列化值

        Args:
            data: 序列化的数据
            value_type: 值类型

        Returns:
            反序列化后的值
        """
        if value_type == "dataframe":
            return pickle.loads(data)
        elif value_type == "json":
            return json.loads(data.decode("utf-8"))
        else:
            return pickle.loads(data)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT value, value_type, expire_time FROM cache WHERE key = ? AND expire_time > ?",
            (key, datetime.now().timestamp()),
        )
        row = cursor.fetchone()

        if row:
            self._increment_hits()
            return self._deserialize(row["value"], row["value_type"])

        self._increment_misses()
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """设置缓存"""
        data, value_type = self._serialize(value)
        expire_time = (datetime.now() + timedelta(seconds=ttl)).timestamp()
        created_at = datetime.now().timestamp()

        conn = self._get_connection()
        conn.execute(
            """
            INSERT OR REPLACE INTO cache (key, value, value_type, expire_time, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (key, data, value_type, expire_time, created_at),
        )
        conn.commit()

    def delete(self, key: str) -> None:
        """删除缓存"""
        conn = self._get_connection()
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()

    def clear(self) -> None:
        """清空缓存"""
        conn = self._get_connection()
        conn.execute("DELETE FROM cache")
        conn.execute("UPDATE stats SET hits = 0, misses = 0 WHERE id = 1")
        conn.commit()

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT 1 FROM cache WHERE key = ? AND expire_time > ?",
            (key, datetime.now().timestamp()),
        )
        return cursor.fetchone() is not None

    def _increment_hits(self) -> None:
        """增加命中次数"""
        conn = self._get_connection()
        conn.execute("UPDATE stats SET hits = hits + 1 WHERE id = 1")
        conn.commit()

    def _increment_misses(self) -> None:
        """增加未命中次数"""
        conn = self._get_connection()
        conn.execute("UPDATE stats SET misses = misses + 1 WHERE id = 1")
        conn.commit()

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """获取缓存统计"""
        conn = self._get_connection()
        cursor = conn.execute("SELECT hits, misses FROM stats WHERE id = 1")
        row = cursor.fetchone()

        hits = row["hits"]
        misses = row["misses"]
        total = hits + misses
        hit_rate = hits / total if total > 0 else 0

        # 获取缓存大小
        cursor = conn.execute("SELECT COUNT(*) as count FROM cache")
        cache_size = cursor.fetchone()["count"]

        return {
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_rate": hit_rate,
            "cache_size": cache_size,
        }

    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        conn = self._get_connection()
        cursor = conn.execute(
            "DELETE FROM cache WHERE expire_time <= ?",
            (datetime.now().timestamp()),
        )
        conn.commit()
        return cursor.rowcount

    def invalidate_pattern(self, pattern: str) -> int:
        """
        按模式删除缓存

        Args:
            pattern: SQL LIKE 模式（如 "stock:sh.600000:%"）

        Returns:
            删除的行数
        """
        conn = self._get_connection()
        cursor = conn.execute("DELETE FROM cache WHERE key LIKE ?", (pattern,))
        conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        """关闭数据库连接"""
        if hasattr(self._local, "conn"):
            self._local.conn.close()
            delattr(self._local, "conn")


def generate_cache_key(
    data_type: str,
    stock_code: str,
    **params: str,
) -> str:
    """
    生成缓存键

    Args:
        data_type: 数据类型 (info, history, dividend, financial)
        stock_code: 股票代码
        **params: 其他参数

    Returns:
        缓存键
    """
    parts = ["stock", stock_code, data_type]
    for key, value in sorted(params.items()):
        parts.append(str(value))
    return ":".join(parts)
