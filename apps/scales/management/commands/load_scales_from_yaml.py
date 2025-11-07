import os
import yaml
from django.core.management.base import BaseCommand

YAML_DIR = os.path.join(os.path.dirname(__file__), '../../yaml_configs')

class Command(BaseCommand):
    help = "自动加载yaml格式量表文件并导入数据库"

    def handle(self, *args, **options):
        from apps.scales.models import ScaleConfig  # 修正模型导入时机
        yaml_dir = os.path.abspath(YAML_DIR)
        if not os.path.exists(yaml_dir):
            self.stdout.write(self.style.WARNING(f"未找到yaml目录: {yaml_dir}"))
            return

        for fname in os.listdir(yaml_dir):
            if fname.endswith('.yaml') or fname.endswith('.yml'):
                fpath = os.path.join(yaml_dir, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if not data or 'questions' not in data:
                    self.stdout.write(self.style.WARNING(f"{fname} 缺少 questions 字段"))
                    continue
                
                # 将value字段转换为字符串
                for question in data['questions']:
                    if 'options' in question:
                        for option in question['options']:
                            if 'value' in option:
                                option['value'] = str(option['value'])
                
                # 读取原始 YAML 内容
                with open(fpath, 'r', encoding='utf-8') as f_raw:
                    yaml_content = f_raw.read()

                # 避免重复导入，并同步 yaml_config 字段
                obj, created = ScaleConfig.objects.update_or_create(
                    code=data['code'],
                    defaults={
                        'name': data.get('name', ''),
                        'version': data.get('version', ''),
                        'description': data.get('description', ''),
                        'type': data.get('type', ''),
                        'questions': data['questions'],
                        'status': data.get('status', 'draft'),
                        'yaml_config': yaml_content,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"导入新量表: {obj.name}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"更新量表: {obj.name} 并同步 YAML 配置"))