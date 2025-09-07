from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Jid(Base):
    __tablename__ = "jid"
    id: Mapped[int] = mapped_column(primary_key=True)
    jid: Mapped[str] = mapped_column()
    devices: Mapped[List["Device"]] = relationship(
        back_populates="jid", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"Jid(id={self.id!r}, jid={self.jid!r}"

class Device(Base):
    __tablename__ = "device"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("jid.id"))
    device: Mapped[int] = mapped_column()

    jid: Mapped["Jid"] = relationship(back_populates="devices")
    session: Mapped["Session"] = relationship(
        back_populates="device", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"Device(id={self.id!r}, device={self.device!r})"


class Session(Base):
    __tablename__ = "session"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    timestamp: Mapped[int] = mapped_column()
    receive_secret_key: Mapped[str] = mapped_column()
    send_secret_key: Mapped[str] = mapped_column()
    receive_count: Mapped[int] = mapped_column()
    send_count: Mapped[int] = mapped_column()

    device: Mapped["Device"] = relationship(back_populates="session")

    def __repr__(self) -> str:
        return f"Session(id={self.id!r}, timestamp={self.timestamp!r})"
