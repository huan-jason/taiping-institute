from django.db.models import TextChoices


class ComplianceTypeChoices(TextChoices):
    INSTRUCTOR_TERMS_AND_CONDITIONS = "instructor terms and conditions"
    TERMS_AND_CONDITIONS = "terms and conditions"
    INDEMNITY_WAIVER = "indemnity waiver"


class GenderChoices(TextChoices):
    MALE = "male"
    FEMALE = "female"


class CourseStatusChoices(TextChoices):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"


class CourseStudentStatusChoices(TextChoices):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED_OUT = "dropped_out"
    CANCELLED = "cancelled"


class UserTypeChoices(TextChoices):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
