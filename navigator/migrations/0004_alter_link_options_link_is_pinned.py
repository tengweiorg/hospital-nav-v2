# Generated by Django 5.1.7 on 2025-03-09 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navigator', '0003_rename_icon_category_icon_class'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='link',
            options={'ordering': ['-is_pinned', '-click_count', 'order', 'title'], 'verbose_name': '链接', 'verbose_name_plural': '链接'},
        ),
        migrations.AddField(
            model_name='link',
            name='is_pinned',
            field=models.BooleanField(default=False, help_text='置顶的链接将优先显示在热门链接区域', verbose_name='置顶显示'),
        ),
    ]
