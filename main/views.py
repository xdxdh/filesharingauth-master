from django.shortcuts import render, redirect
from .models import User, File_Upload, Category
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import File_Upload
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


@login_required
def index(request):
    all_files = File_Upload.objects.all().order_by('-id')
    paginator = Paginator(all_files, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {'page_obj': page_obj})

def login_view(request):
    # Если пользователь уже аутентифицирован, перенаправляем на главную страницу
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pwd')

        # Получаем пользователя по email, так как authenticate требует username
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, "Неправильный email или пароль.")
            return render(request, 'login.html')

        # Проверяем учетные данные
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Вход в систему
            return redirect('index')
        else:
            messages.error(request, "Неправильный email или пароль.")

    return render(request, 'login.html')
def logout(request):
    del request.session['user']
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        pwd = request.POST['pwd']
        gender = request.POST['gender']
        if not User.objects.filter(email=email).exists():
            create_user = User.objects.create(name=name, email=email, pwd=pwd, gender=gender)
            create_user.save()
            messages.success(request, "Your account is created successfully!")
            return redirect('login')
        else:
            messages.warning(request, "Email is already registered!")
    return render(request, 'signup.html')

@login_required
def file_upload(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Только администратор может загружать файлы")

    if request.method == 'POST':
        title_name = request.POST['title']
        description_name = request.POST['description']
        file_name = request.FILES['file_to_upload']
        category_id = request.POST.get('category', None)

        category_obj = None
        if category_id:
            category_obj = Category.objects.get(id=category_id)

        new_file = File_Upload.objects.create(
            user=request.user,
            title=title_name,
            description=description_name,
            file_field=file_name,
            category=category_obj
        )
        messages.success(request, "File is uploaded successfully!")
        new_file.save()

    categories = Category.objects.all()
    return render(request, 'file_upload.html', {'categories': categories})

def settings(request):
    if 'user' in request.session:
        user_obj = User.objects.get(email=request.session['user'])
        user_files = File_Upload.objects.filter(user=user_obj)

        img_list, audio_list, videos_list, pdfs_list = [], [], [], []

        for file in user_files:
            if str(file.file_field)[-3:] == 'mp3':
                audio_list.append(file)
            elif str(file.file_field)[-3:] in ['mp4', 'mkv']:
                videos_list.append(file)
            elif str(file.file_field)[-3:] in ['jpg', 'png', 'jpeg']:
                img_list.append(file)
            elif str(file.file_field)[-3:] == 'pdf':
                pdfs_list.append(file)

        data = {
            'user_files': user_files,
            'videos': len(videos_list),
            'audios': len(audio_list),
            'images': len(img_list),
            'pdf': len(pdfs_list),
            'img_list': img_list,
            'audio_list': audio_list,
            'videos_list': videos_list,
            'pdfs_list': pdfs_list
        }
        return render(request, 'settings.html', data)

def delete_file(request, id):
    if 'user' in request.session:
        file_obj = File_Upload.objects.get(id=id)
        file_obj.delete()
        return redirect('settings')
    else:
        return redirect('login')

