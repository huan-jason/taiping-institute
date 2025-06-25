from django.db.models import TextChoices


class ComplianceTypeChoices(TextChoices):
    TERMS_AND_CONDITIONS = "terms and conditions"
    INDEMNITY_WAIVER = "indemnity waiver"


class GenderChoices(TextChoices):
    MALE = "male"
    FEMALE = "female"


class CourseStatusChoices(TextChoices):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"


class UserTypeChoices(TextChoices):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
