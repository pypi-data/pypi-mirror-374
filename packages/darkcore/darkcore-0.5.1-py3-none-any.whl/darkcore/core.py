# filepath: darkcore/core.py
from __future__ import annotations
from typing import Any, Callable, Generic, Protocol, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class Applicative(Protocol, Generic[A]):
    """
    構造的サブタイピングで表現した最小限の Applicative プロトコル。
    具体型（Maybe, Result, Either など）は、このプロトコルが要求する
    メソッド群（pure, ap）を実装していれば「Applicative 的」に振る舞える。
    """

    @classmethod
    def pure(cls, value: A) -> Applicative[A]:
        """値を Applicative コンテキストに持ち上げる"""
        ...

    def ap(self, fa: Applicative[Any]) -> Applicative[Any]:
        """
        self が f: (A -> B) を含む Applicative,
        fa が A を含む Applicative のとき、
        f を適用して B を含む Applicative を返す。
        """
        ...


# プロトコル定義
class Monad(Protocol, Generic[A]):
    """
    構造的サブタイピングで表現した最小限の Monad プロトコル。
    ・pure: a -> m a
    ・bind: m a -> (a -> m b) -> m b
    ・fmap: m a -> (a -> b) -> m b
    HKTs が無い Python では正確な型制約ができないため Any を許容。
    """

    @classmethod
    def pure(cls, value: A) -> Monad[A]:
        """値を Monad コンテキストに持ち上げる"""
        ...

    def bind(self, f: Callable[[A], Monad[Any]]) -> Monad[Any]:
        """文脈付き値に f: a -> m b を適用して m b を返す"""
        ...

    def fmap(self, f: Callable[[A], B]) -> Monad[B]:
        """文脈付き値に純粋関数を適用して m b を返す"""
        ...


class SupportsFmapBindAp(Protocol, Generic[A]):
    """Protocol for types supporting ``fmap``, ``bind`` and ``ap``."""

    def fmap(self, f: Callable[[A], B]) -> Any:  # pragma: no cover - structural
        ...

    def bind(self, f: Callable[[A], Any]) -> Any:  # pragma: no cover - structural
        ...

    def ap(self, fa: Any) -> Any:  # pragma: no cover - structural
        ...


class MonadOpsMixin(Generic[A]):
    """演算子 DSL を提供するミックスイン。

    ``|`` は ``fmap``、``>>`` は ``bind``、``@`` は ``ap`` に対応する。
    ``fmap``/``bind``/``ap`` を実装する型はこのミックスインを継承するだけで
    これらの演算子を利用できる。
    """

    def __or__(self: SupportsFmapBindAp[A], f: Callable[[A], B]) -> Any:
        return self.fmap(f)

    def __rshift__(self: SupportsFmapBindAp[A], f: Callable[[A], Any]) -> Any:
        return self.bind(f)

    def __matmul__(self: SupportsFmapBindAp[A], fa: Any) -> Any:
        return self.ap(fa)
