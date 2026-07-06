from enum import Enum


class ProcessingState(str, Enum):
    RAW = "RAW"
    PROCESSING = "PROCESSING"
    CLEAN = "CLEAN"
    ENRICHED = "ENRICHED"
    PUBLISHED = "PUBLISHED"


class GovernanceStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    RESTRICTED = "restricted"
    DEPRECATED = "deprecated"


class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    HIGH_RISK = "high-risk"


class LegalReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs-review"


class PiiRiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AcquisitionVector(str, Enum):
    SCRAPING = "scraping_automatise"
    API = "api_officielle"
    DIRECT_DOWNLOAD = "telechargement_direct"
    MANUAL_OSINT = "osint_manuel"
    LEAK = "fuite_leak"


class SourceType(str, Enum):
    API = "api"
    SCRAPING = "scraping"
    MANUAL = "manual"
    LEAK = "leak"
    DOWNLOAD = "download"
    ARCHIVE = "archive"


class AuditType(str, Enum):
    INTEGRITY = "integrity"
    SCHEMA_DRIFT = "schema_drift"
    FRESHNESS = "freshness"
    PII = "pii"
    QUALITY = "quality"


class AuditStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"