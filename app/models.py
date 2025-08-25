from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for different status and role types
class UserRole(str, Enum):
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    DISTRICT_OPERATOR = "district_operator"
    HEADMASTER = "headmaster"


class TransferStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    DOCUMENT_VERIFICATION = "document_verification"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class TransferType(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class DocumentType(str, Enum):
    BIRTH_CERTIFICATE = "birth_certificate"
    REPORT_CARD = "report_card"
    FAMILY_CARD = "family_card"
    TRANSFER_LETTER = "transfer_letter"
    OTHER = "other"


class NotificationType(str, Enum):
    TRANSFER_SUBMITTED = "transfer_submitted"
    DOCUMENT_REQUIRED = "document_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.TEACHER)
    is_active: bool = Field(default=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)

    # Relationships
    created_transfers: List["StudentTransfer"] = Relationship(back_populates="created_by_user")
    approved_transfers: List["StudentTransfer"] = Relationship(back_populates="approved_by_user")
    notifications: List["Notification"] = Relationship(back_populates="user")


class School(SQLModel, table=True):
    __tablename__ = "schools"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    npsn: str = Field(unique=True, max_length=20)  # Nomor Pokok Sekolah Nasional
    name: str = Field(max_length=200)
    address: str = Field(max_length=500)
    district: str = Field(max_length=100)
    regency: str = Field(max_length=100)
    province: str = Field(max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    headmaster_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    origin_transfers: List["StudentTransfer"] = Relationship(back_populates="origin_school")
    destination_transfers: List["StudentTransfer"] = Relationship(back_populates="destination_school")


class Student(SQLModel, table=True):
    __tablename__ = "students"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nisn: str = Field(unique=True, max_length=20)  # National Student Identification Number
    nis: Optional[str] = Field(default=None, max_length=20)  # School Student Number
    full_name: str = Field(max_length=100)
    birth_place: str = Field(max_length=100)
    birth_date: datetime
    gender: str = Field(max_length=10)  # "Laki-laki" or "Perempuan"
    religion: str = Field(max_length=20)
    address: str = Field(max_length=500)
    parent_name: str = Field(max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    current_grade: str = Field(max_length=10)  # e.g., "1", "2", "3", etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transfers: List["StudentTransfer"] = Relationship(back_populates="student")


class StudentTransfer(SQLModel, table=True):
    __tablename__ = "student_transfers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_number: str = Field(unique=True, max_length=50)  # Auto-generated transfer ID
    student_id: int = Field(foreign_key="students.id")
    transfer_type: TransferType
    origin_school_id: int = Field(foreign_key="schools.id")
    destination_school_id: int = Field(foreign_key="schools.id")
    transfer_reason: str = Field(max_length=1000)
    status: TransferStatus = Field(default=TransferStatus.DRAFT)
    grade_from: str = Field(max_length=10)
    grade_to: str = Field(max_length=10)
    semester: str = Field(max_length=10)
    academic_year: str = Field(max_length=10)  # e.g., "2023/2024"
    transfer_date: datetime = Field(default_factory=datetime.utcnow)

    # User tracking
    created_by_id: int = Field(foreign_key="users.id")
    approved_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    approval_date: Optional[datetime] = Field(default=None)
    approval_notes: Optional[str] = Field(default=None, max_length=1000)

    # Additional metadata
    priority_level: str = Field(default="normal", max_length=20)  # "urgent", "normal", "low"
    notes: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="transfers")
    origin_school: School = Relationship(back_populates="origin_transfers")
    destination_school: School = Relationship(back_populates="destination_transfers")
    created_by_user: User = Relationship(back_populates="created_transfers")
    approved_by_user: Optional[User] = Relationship(back_populates="approved_transfers")
    documents: List["TransferDocument"] = Relationship(back_populates="transfer")
    status_history: List["TransferStatusHistory"] = Relationship(back_populates="transfer")
    notifications: List["Notification"] = Relationship(back_populates="transfer")


class TransferDocument(SQLModel, table=True):
    __tablename__ = "transfer_documents"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_id: int = Field(foreign_key="student_transfers.id")
    document_type: DocumentType
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int  # in bytes
    mime_type: str = Field(max_length=100)
    is_verified: bool = Field(default=False)
    verified_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    verified_at: Optional[datetime] = Field(default=None)
    verification_notes: Optional[str] = Field(default=None, max_length=500)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transfer: StudentTransfer = Relationship(back_populates="documents")


class TransferStatusHistory(SQLModel, table=True):
    __tablename__ = "transfer_status_history"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_id: int = Field(foreign_key="student_transfers.id")
    previous_status: Optional[TransferStatus] = Field(default=None)
    new_status: TransferStatus
    changed_by_id: int = Field(foreign_key="users.id")
    change_reason: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transfer: StudentTransfer = Relationship(back_populates="status_history")


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    transfer_id: Optional[int] = Field(default=None, foreign_key="student_transfers.id")
    notification_type: NotificationType
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    is_read: bool = Field(default=False)
    is_urgent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="notifications")
    transfer: Optional[StudentTransfer] = Relationship(back_populates="notifications")


class SystemSettings(SQLModel, table=True):
    __tablename__ = "system_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    setting_key: str = Field(unique=True, max_length=100)
    setting_value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    action: str = Field(max_length=100)  # e.g., "CREATE", "UPDATE", "DELETE", "LOGIN"
    table_name: str = Field(max_length=50)
    record_id: Optional[int] = Field(default=None)
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransferStatistics(SQLModel, table=True):
    __tablename__ = "transfer_statistics"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    month: int
    total_incoming: int = Field(default=0)
    total_outgoing: int = Field(default=0)
    total_approved: int = Field(default=0)
    total_rejected: int = Field(default=0)
    total_pending: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.TEACHER)
    phone: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = Field(default=None)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None)


class UserLogin(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(max_length=100)


class StudentCreate(SQLModel, table=False):
    nisn: str = Field(max_length=20)
    nis: Optional[str] = Field(default=None, max_length=20)
    full_name: str = Field(max_length=100)
    birth_place: str = Field(max_length=100)
    birth_date: datetime
    gender: str = Field(max_length=10)
    religion: str = Field(max_length=20)
    address: str = Field(max_length=500)
    parent_name: str = Field(max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    current_grade: str = Field(max_length=10)


class StudentUpdate(SQLModel, table=False):
    nis: Optional[str] = Field(default=None, max_length=20)
    full_name: Optional[str] = Field(default=None, max_length=100)
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[datetime] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=10)
    religion: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    current_grade: Optional[str] = Field(default=None, max_length=10)


class SchoolCreate(SQLModel, table=False):
    npsn: str = Field(max_length=20)
    name: str = Field(max_length=200)
    address: str = Field(max_length=500)
    district: str = Field(max_length=100)
    regency: str = Field(max_length=100)
    province: str = Field(max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    headmaster_name: str = Field(max_length=100)


class TransferCreate(SQLModel, table=False):
    student_id: int
    transfer_type: TransferType
    origin_school_id: int
    destination_school_id: int
    transfer_reason: str = Field(max_length=1000)
    grade_from: str = Field(max_length=10)
    grade_to: str = Field(max_length=10)
    semester: str = Field(max_length=10)
    academic_year: str = Field(max_length=10)
    priority_level: str = Field(default="normal", max_length=20)
    notes: Optional[str] = Field(default=None, max_length=2000)


class TransferUpdate(SQLModel, table=False):
    transfer_reason: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TransferStatus] = Field(default=None)
    grade_from: Optional[str] = Field(default=None, max_length=10)
    grade_to: Optional[str] = Field(default=None, max_length=10)
    semester: Optional[str] = Field(default=None, max_length=10)
    academic_year: Optional[str] = Field(default=None, max_length=10)
    priority_level: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=2000)
    approval_notes: Optional[str] = Field(default=None, max_length=1000)


class TransferApproval(SQLModel, table=False):
    status: TransferStatus
    approval_notes: str = Field(max_length=1000)


class DocumentUpload(SQLModel, table=False):
    document_type: DocumentType
    file_name: str = Field(max_length=255)
    file_size: int
    mime_type: str = Field(max_length=100)


class NotificationCreate(SQLModel, table=False):
    user_id: int
    transfer_id: Optional[int] = Field(default=None)
    notification_type: NotificationType
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    is_urgent: bool = Field(default=False)


class TransferReportFilter(SQLModel, table=False):
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    status: Optional[TransferStatus] = Field(default=None)
    transfer_type: Optional[TransferType] = Field(default=None)
    origin_school_id: Optional[int] = Field(default=None)
    destination_school_id: Optional[int] = Field(default=None)
    grade: Optional[str] = Field(default=None, max_length=10)
    academic_year: Optional[str] = Field(default=None, max_length=10)


class DashboardStats(SQLModel, table=False):
    total_transfers: int = Field(default=0)
    total_incoming: int = Field(default=0)
    total_outgoing: int = Field(default=0)
    pending_approvals: int = Field(default=0)
    approved_this_month: int = Field(default=0)
    rejected_this_month: int = Field(default=0)
    monthly_trends: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
