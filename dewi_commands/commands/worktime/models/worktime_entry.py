import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime

from dewi_commands.commands.worktime.models.base import Base


class WorktimeEntry(Base):
    __tablename__ = 'worktime_entries'

    id = Column(Integer, primary_key=True)
    event_at = Column(DateTime, nullable=False)
    is_login = Column(Boolean, nullable=False)
    year = Column(Integer)
    month = Column(Integer)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def fill_year_month(self):
        self.year = self.event_at.year
        self.month = self.event_at.month

    def init_fields(self):
        self.fill_year_month()
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
