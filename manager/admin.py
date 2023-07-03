from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(Proxy)
admin.site.register(ConfirmationCode)


class ExtensionUserAdmin(UserAdmin):
    # Определение полей, которые нужно отобразить в админке
    list_display = ('username', 'email', 'date_joined', 'last_login')

    # Определение полей, по которым можно фильтровать записи
    list_filter = ('is_staff', 'is_superuser')

    # Определение полей, по которым можно искать записи
    search_fields = ('username', 'email', 'first_name', 'last_name')


    # Определение полей, по которым можно упорядочить записи
    ordering = ('-date_joined',)

    # Определение полей, которые будут показаны в деталях записи
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Token', {'fields': ('jwt_access_token',)}),
    )

    # Определение полей, которые будут показаны при создании новой записи
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


# Регистрация модели пользователя и соответствующего ей класса ModelAdmin
admin.site.register(AppUser, ExtensionUserAdmin)
