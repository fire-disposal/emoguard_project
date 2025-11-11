"""
创建默认管理员账户的管理命令
使用方式: python manage.py create_admin
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = '创建默认管理员账户'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
            help='管理员用户名 (默认: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@emoguard.com'),
            help='管理员邮箱 (默认: admin@emoguard.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123456'),
            help='管理员密码 (默认: admin123456)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='如果管理员已存在，强制重置密码'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        force = options['force']
        
        try:
            # 检查管理员是否已存在
            if User.objects.filter(username=username).exists():
                if force:
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.email = email
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    user.role = 'admin'
                    user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'管理员账户已重置: {username}')
                    )
                    self.stdout.write(
                        self.style.WARNING(f'密码: {password}')
                    )
                    self.stdout.write(
                        self.style.WARNING('请及时修改默认密码！')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'管理员 {username} 已存在。使用 --force 参数强制重置。'
                        )
                    )
                return
            
            # 创建新管理员
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'成功创建管理员账户: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'邮箱: {email}')
            )
            self.stdout.write(
                self.style.WARNING(f'密码: {password}')
            )
            self.stdout.write(
                self.style.WARNING('请及时修改默认密码！')
            )
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'创建管理员失败（数据库完整性错误）: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建管理员失败: {e}')
            )
