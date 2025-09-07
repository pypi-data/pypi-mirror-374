import time

from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import select

from .models import Base 
from .models import Jid 
from .models import Device 
from .models import Session as OmemoSession 

class OmemoStorage:
    def __init__(self, store_path: str):
        self._engine = create_engine(f"sqlite:///{store_path}")
        Base.metadata.create_all(self._engine)

    def add_device(self, jid: str, device: int) -> None:
        with Session(self._engine) as session:
            stmt = select(Jid).where(Jid.jid == jid)
            ojid = session.scalar(stmt)

            if (ojid):
                ojid.devices.append(Device(device=device))
                session.add(ojid)
            else:
                ojid = Jid(jid=jid, devices=[Device(device=device)])
                session.add(ojid)
            session.commit()

    def add_session(
                self,
                jid: str,
                device: int, 
                receive_secret_key: str, 
                send_secret_key: str, 
            ) -> None:
        with Session(self._engine) as session:
            stmt = select(Device).join(Jid).where(Jid.jid == jid).where(Device.device == device)
            odevice = session.scalar(stmt)
            if (odevice):
                osession = OmemoSession(
                    timestamp=time.time(),
                    receive_secret_key=receive_secret_key,
                    send_secret_key=send_secret_key,
                    receive_count=0,
                    send_count=0,
                )
                odevice.session = osession
                session.commit()
            else:
                raise Exception("Thas JID or device does not exist in the database.")


    def get_device_list(self, jid: str) -> List[int]:
        devices = []
        with Session(self._engine) as session:
            stmt = select(Jid).where(Jid.jid == jid)
            ojid = session.scalar(stmt)

            if (ojid):
                for device in ojid.devices:
                    devices.append(device.device)
            else:
                raise Exception("That JID does not exist in the database.")
        return devices

    def get_session(self, jid: str, device: int) -> OmemoSession:
        with Session(self._engine) as session:
            stmt = select(Device).join(Jid).where(Jid.jid == jid).where(Device.device == device)
            odevice = session.scalar(stmt)
            if (odevice):
                return odevice.session
            else:
                raise Exception("Thas JID or device does not exist in the database.")

    def increase_receive_count(self, jid: str, device: int) -> None:
        with Session(self._engine) as session:
            stmt = select(Device).join(Jid).where(Jid.jid == jid).where(Device.device == device)
            odevice = session.scalar(stmt)
            if (odevice):
                if (odevice.session):
                    odevice.session.receive_count += 1
                    session.commit()
                else:
                    raise Exception("No session for this device.")
            else:
                raise Exception("Thas JID or device does not exist in the database.")

    def increase_send_count(self, jid: str, device: int) -> None:
        with Session(self._engine) as session:
            stmt = select(Device).join(Jid).where(Jid.jid == jid).where(Device.device == device)
            odevice = session.scalar(stmt)
            if (odevice):
                if (odevice.session):
                    odevice.session.send_count += 1
                    session.commit()
                else:
                    raise Exception("No session for this device.")
            else:
                raise Exception("Thas JID or device does not exist in the database.")

    def update_receive_secret(self, jid: str, device: int, secret: str):
        with Session(self._engine) as session:
            stmt = select(Device).join(Jid).where(Jid.jid == jid).where(Device.device == device)
            odevice = session.scalar(stmt)
            if (odevice):
                if (odevice.session):
                    odevice.session.receive_secret_key = secret
                    session.commit()
                else:
                    raise Exception("No session for this device.")
            else:
                raise Exception("Thas JID or device does not exist in the database.")

    def update_send_secret(self, jid: str, device: int, secret: str):
        with Session(self._engine) as session:
            stmt = select(Device).join(Jid).where(Jid.jid == jid).where(Device.device == device)
            odevice = session.scalar(stmt)
            if (odevice):
                if (odevice.session):
                    odevice.session.send_secret_key = secret
                    session.commit()
                else:
                    raise Exception("No session for this device.")
            else:
                raise Exception("Thas JID or device does not exist in the database.")
