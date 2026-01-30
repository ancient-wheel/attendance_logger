from __future__ import annotations
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
)
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Date,
    Float,
    DateTime,
    ForeignKey,
    Column,
    Table,
    Time,
    LargeBinary,
)
import datetime as dt
from attendance_logger.models.database import db
from attendance_logger.models.models import VisitRoles
from attendance_logger.utils import utils


class CreatedAtMixin(db.Model):
    __abstract__ = True

    created_datetime: Mapped[dt.datetime] = mapped_column(DateTime)
    created_timezone: Mapped[int] = mapped_column(Integer)
    changed_datetime: Mapped[dt.datetime | None] = mapped_column(DateTime)
    changed_timezone: Mapped[int | None] = mapped_column(Integer)

    @property
    def created_at(self) -> tuple[dt.datetime, int]:
        return self.created_datetime, self.created_timezone

    @property
    def changed_at(self) -> tuple[dt.datetime | None, int | None]:
        return self.changed_datetime, self.changed_timezone

    @changed_at.setter
    def changed_at(self, datetime_utc: dt.datetime, timezone: int = 0) -> None:
        self.changed_datetime = datetime_utc
        self.changed_timezone = timezone


_UserRole_User = Table(
    "_user_roles_users",
    db.Model.metadata,
    Column("User", ForeignKey("users.id_"), primary_key=True),
    Column("UserRole", ForeignKey("user_roles.id_"), primary_key=True),
)


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str | None] = mapped_column(String(256))
    permissions: Mapped[str | None] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"<Role id_:{self.id_} name:{self.name}>"


class User(CreatedAtMixin):
    __tablename__ = "users"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(256))
    password: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed_at_utc: Mapped[dt.datetime | None] = mapped_column(DateTime)
    current_login_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    current_login_ip: Mapped[str | None] = mapped_column(String(100))
    last_login_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    last_login_ip: Mapped[str | None] = mapped_column(String(100))
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    roles: Mapped[list[UserRole]] = relationship(secondary=_UserRole_User)
    works: Mapped[list[Teacher]] = relationship(back_populates="user")
    groups: Mapped[list[UserParticipant]] = relationship(back_populates="user")
    favorites: Mapped[Favorites] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User id_:{self.id_} email:{self.email} active:{self.active} name:{self.username} roles:{[role.name for role in self.roles]}>"

    def get_id(self) -> str:
        return str(self.id_)

    def is_active(self) -> bool:
        return self.active


class Client(CreatedAtMixin):
    __tablename__ = "clients"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    name: Mapped[str] = mapped_column(String(100))
    child_name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(100))
    childs_birthday: Mapped[dt.date] = mapped_column(Date)
    notes: Mapped[str] = mapped_column(String(1000), default="")
    contracts: Mapped[list[Contract]] = relationship(back_populates="client")
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="client")
    participations: Mapped[list[ClientParticipant]] = relationship(
        back_populates="client"
    )

    def __repr__(self):
        return f"<Client id_:{self.id_} name:{self.name} active:{self.active}>"


class Contract(CreatedAtMixin):
    __tablename__ = "contracts"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(100), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id_"))
    client: Mapped[Client] = relationship(back_populates="contracts")
    signed_on: Mapped[dt.date | None] = mapped_column(Date)
    canceled: Mapped[dt.date | None] = mapped_column(Date)
    signed_pdf: Mapped[bytes | None] = mapped_column(LargeBinary)
    canceled_pdf: Mapped[bytes | None] = mapped_column(LargeBinary)

    def __repr__(self):
        return f"<Contract id_:{self.id_} number:{self.number} active:{self.active}>"


class Group(CreatedAtMixin):
    __tablename__ = "groups"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    active_from: Mapped[dt.date] = mapped_column(Date, default=dt.date.today())
    active_until: Mapped[dt.date] = mapped_column(
        Date, default=dt.date.today() + dt.timedelta(days=365)
    )
    teachers: Mapped[list["UserParticipant"]] = relationship(back_populates="group")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="group")
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id_"))
    location: Mapped[Location | None] = relationship(back_populates="groups")
    participants: Mapped[list[ClientParticipant]] = relationship(back_populates="group")
    schedules: Mapped[list[Schedule]] = relationship(
        secondary=lambda: _group_schedule_table, back_populates="groups"
    )
    favorites: Mapped[list[Favorites]] = relationship(
        secondary=lambda: _favorites_groups, back_populates="groups"
    )

    def __repr__(self):
        return f"<Group id_:{self.id_} name:{self.name} active_from:{self.active_from} active_until:{self.active_until}>"


class ParticipentMixin(CreatedAtMixin):
    __abstract__ = True
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[dt.date] = mapped_column(Date)
    end_date: Mapped[dt.date] = mapped_column(Date)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id_"), primary_key=True)


class ClientParticipant(ParticipentMixin):
    __tablename__ = "client_participants"
    group: Mapped[Group] = relationship(back_populates="participants")
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id_"), primary_key=True)
    client: Mapped[Client] = relationship(back_populates="participations")


class UserParticipant(ParticipentMixin):
    __tablename__ = "user_participants"
    group: Mapped[Group] = relationship(back_populates="teachers")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id_"), primary_key=True)
    user: Mapped[User] = relationship(back_populates="groups")


class Schedule(db.Model):
    __tablename__ = "schedules"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    groups: Mapped[list[Group]] = relationship(
        secondary=lambda: _group_schedule_table, back_populates="schedules"
    )
    weekday: Mapped[int] = mapped_column(Integer)
    start_time_utc: Mapped[dt.time] = mapped_column(Time)
    start_timezone: Mapped[int] = mapped_column(Integer)
    end_time_utc: Mapped[dt.time] = mapped_column(Time)
    end_timezone: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<Schedule id_:{self.id_} weekday:{self.weekday} start_time:{self.start_time_utc} end_time:{self.end_time_utc}>"


_group_schedule_table = Table(
    "_groups_schedules",
    db.Model.metadata,
    Column("Group", ForeignKey("groups.id_"), primary_key=True),
    Column("Schedule", ForeignKey("schedules.id_"), primary_key=True),
)


class Subscription(CreatedAtMixin):
    __tablename__ = "subscriptions"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    total_visits: Mapped[int] = mapped_column(Integer)
    full_price_id: Mapped[int] = mapped_column(ForeignKey("prices.id_"))
    full_price: Mapped[Price] = relationship()
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)
    start_date: Mapped[dt.date] = mapped_column(Date, default=dt.date.today())
    end_date: Mapped[dt.date | None] = mapped_column(
        Date, default=dt.date.today() + dt.timedelta(days=31)
    )
    freezed: Mapped[bool] = mapped_column(Boolean, default=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id_"))
    client: Mapped[Client] = relationship(back_populates="subscriptions")
    visits: Mapped[list[Visitor]] = relationship(back_populates="subscription")

    def __repr__(
        self,
    ):
        return f"<Subscription id_:{self.id_} active:{self.active} freezed:{self.freezed} total_visits:{self.total_visits} used_visits:{self.open_visits}>"

    @property
    def open_visits(self) -> int:
        return self.total_visits - len(
            [
                visit
                for visit in self.visits
                if visit.state in [VisitRoles.PRESENT.value, VisitRoles.ILL.value]
            ]
        )

    @property
    def active(self) -> bool:
        if self.end_date and self.end_date > dt.date.today() and not self.freezed:
            return False
        return True


class Lesson(CreatedAtMixin):
    __tablename__ = "lessons"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(256))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id_"))
    group: Mapped[Group] = relationship(back_populates="lessons")
    start_datetime_utc: Mapped[dt.datetime] = mapped_column(DateTime)
    start_timezone: Mapped[int] = mapped_column(Integer)
    end_datetime_utc: Mapped[dt.datetime] = mapped_column(DateTime)
    end_timezone: Mapped[int] = mapped_column(Integer)
    teachers: Mapped[list[Teacher]] = relationship(back_populates="lesson")
    visitors: Mapped[list[Visitor]] = relationship(back_populates="lesson")
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id_"))
    location: Mapped[Location | None] = relationship(back_populates="lessons")
    favorites: Mapped[list[Favorites]] = relationship(
        secondary=lambda: _favorites_lessons, back_populates="lessons"
    )

    def __repr__(self):
        return f"<Lesson id_:{self.id_} group:{self.group.name} start:{self.start_datetime_utc} state:{self.state}>"

    @property
    def duration(self) -> dt.timedelta:
        return self.end_datetime_utc - self.start_datetime_utc

    @property
    def start_datetime(self) -> tuple[dt.datetime, int]:
        return self.start_datetime_utc, self.start_timezone

    @property
    def end_datetime(self) -> tuple[dt.datetime, int]:
        return self.end_datetime_utc, self.end_timezone


class VisitorMixin(CreatedAtMixin):
    __abstract__ = True
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(256))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id_"), primary_key=True)


class Teacher(VisitorMixin):
    __tablename__ = "teachers"
    lesson: Mapped[Lesson] = relationship(back_populates="teachers")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id_"), primary_key=True)
    user: Mapped[User] = relationship(back_populates="works")


class Visitor(VisitorMixin):
    __tablename__ = "visitors"
    lesson: Mapped[Lesson] = relationship(back_populates="visitors")
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id_"), primary_key=True
    )
    subscription: Mapped[Subscription] = relationship(back_populates="visits")


class Price(CreatedAtMixin):
    __tablename__ = "prices"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_: Mapped[int] = mapped_column(Integer)
    value: Mapped[float] = mapped_column(Float)
    start_datetime_utc: Mapped[dt.datetime] = mapped_column(DateTime)
    start_timezone: Mapped[int] = mapped_column(Integer)
    end_datetime_utc: Mapped[dt.datetime | None] = mapped_column(DateTime)
    end_timezone: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(256))

    def __repr__(self) -> str:
        return f"<Price id_:{self.id_} type_:{self.type_} value:{self.value} start:{self.start_datetime_utc} end:{self.end_datetime_utc}>"


class Location(db.Model):
    __tablename__ = "locations"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256))
    address: Mapped[str] = mapped_column(String(256), unique=True)
    url: Mapped[str | None] = mapped_column(String(256))
    groups: Mapped[list[Group]] = relationship(back_populates="location")
    lessons: Mapped[list[Lesson]] = relationship(back_populates="location")

    def __repr__(self) -> str:
        return f"<Location id_:{self.id_}, name:{self.name}, address:{self.address}"


class EmailConfirmation(CreatedAtMixin):
    __tablename__ = "email_confirmations"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(256))
    token: Mapped[str] = mapped_column(String(256), unique=True)
    confirmed_at_utc: Mapped[dt.datetime | None] = mapped_column(DateTime)
    expired_datetime_utc: Mapped[dt.datetime] = mapped_column(
        DateTime, default=utils.get_current_utc_datetime_plus_hours(2)
    )


class Favorites(CreatedAtMixin):
    __tablename__ = "favorites"
    id_: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id_"), primary_key=True)
    user: Mapped[User] = relationship(back_populates="favorites")
    groups: Mapped[list[Group]] = relationship(secondary=lambda: _favorites_groups)
    lessons: Mapped[list[Lesson]] = relationship(secondary=lambda: _favorites_lessons)


_favorites_groups = Table(
    "_favorites_groups",
    db.Model.metadata,
    Column("Favorites", ForeignKey("favorites.id_"), primary_key=True),
    Column("Group", ForeignKey("groups.id_"), primary_key=True),
)

_favorites_lessons = Table(
    "_favorites_lessons",
    db.Model.metadata,
    Column("Favorites", ForeignKey("favorites.id_"), primary_key=True),
    Column("lessons", ForeignKey("lessons.id_"), primary_key=True),
)
