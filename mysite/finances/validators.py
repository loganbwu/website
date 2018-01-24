from django.core.validators import FileExtensionValidator

validate_csv = FileExtensionValidator(['csv', 'CSV'], 'Upload file as a CSV')
