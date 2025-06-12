from django.db.models import TextChoices


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
