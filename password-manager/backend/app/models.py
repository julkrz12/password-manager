from sqlalchemy import String, Integer, DateTime, ForeignKey, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Argon2id hash do weryfikacji hasła głównego
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)

    # Sól do wyprowadzenia klucza szyfrującego (KDF)
    kdf_salt: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    entries: Mapped[list['Entry']] = relationship(back_populates='user', cascade='all, delete-orphan')


class Entry(Base):
    __tablename__ = 'entries'
    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='uq_entry_title_per_user'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(512), default='', nullable=False)

    # Zaszyfrowany blob JSON: {account_username, password, notes}
    secret_ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    secret_nonce: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # Fingerprint (do wykrywania duplikatów hasła bez przechowywania w czystej postaci)
    pw_fingerprint: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped['User'] = relationship(back_populates='entries')
