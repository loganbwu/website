from django.validators import FileExtensionValidator

validate_csv = FileExtensionValidator('csv', 'Upload file as a CSV')
