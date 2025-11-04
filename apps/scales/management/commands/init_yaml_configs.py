"""
从现有的 YAML 文件初始化 ScaleConfig 的 yaml_config 字段
"""
import os
import yaml
from django.core.management.base import BaseCommand
from apps.scales.models import ScaleConfig

YAML_DIR = os.path.join(os.path.dirname(__file__), '../../yaml_configs')


class Command(BaseCommand):
    help = "从 yaml_configs 目录读取 YAML 文件，初始化现有量表的 yaml_config 字段"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制覆盖已存在的 yaml_config 字段',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        yaml_dir = os.path.abspath(YAML_DIR)
        
        if not os.path.exists(yaml_dir):
            self.stdout.write(self.style.WARNING(f"未找到 yaml 目录: {yaml_dir}"))
            return

        updated_count = 0
        skipped_count = 0

        for fname in os.listdir(yaml_dir):
            if not (fname.endswith('.yaml') or fname.endswith('.yml')):
                continue
                
            fpath = os.path.join(yaml_dir, fname)
            
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                    data = yaml.safe_load(yaml_content)
                
                if not data or 'code' not in data:
                    self.stdout.write(
                        self.style.WARNING(f"{fname} 缺少 code 字段，跳过")
                    )
                    continue
                
                code = data['code']
                
                try:
                    scale = ScaleConfig.objects.get(code=code)
                    
                    if scale.yaml_config and not force:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{scale.name} ({code}) 已有 YAML 配置，跳过（使用 --force 强制覆盖）"
                            )
                        )
                        skipped_count += 1
                        continue
                    
                    # 更新 yaml_config 字段
                    scale.yaml_config = yaml_content
                    scale.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ 已更新 {scale.name} ({code}) 的 YAML 配置"
                        )
                    )
                    updated_count += 1
                    
                except ScaleConfig.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"未找到代码为 {code} 的量表，请先运行 load_scales_from_yaml 命令"
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"处理 {fname} 时出错: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n完成！更新了 {updated_count} 个量表，跳过 {skipped_count} 个"
            )
        )
