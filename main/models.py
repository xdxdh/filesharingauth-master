from django.db import models
from django.templatetags.static import static

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    pwd = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)

    def __str__(self):
        return self.name

# Определение класса Category перед использованием в File_Upload
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class File_Upload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    # Сделать поле category допускающим null временно для миграции
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='files', null=True)
    file_field = models.FileField(upload_to="")
    def get_icon_path(self):
        file_extension = self.file_field.name.split('.')[-1].lower()
        file_icons = {
            'pdf': 'images/icons/pdf.png',
            'docx': 'images/icons/docx.png',
            'xls': 'images/icons/xls.png',
            'pptx': 'images/icons/pptx.png',
            # Добавьте другие расширения и пути к их изображениям по необходимости
        }
        return static(file_icons.get(file_extension, 'images/icons/default.png'))
    def __str__(self):
        return self.title

class File(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    # Другие поля по необходимости

