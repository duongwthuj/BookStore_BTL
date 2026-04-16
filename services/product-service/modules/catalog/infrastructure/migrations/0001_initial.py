from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='ProductModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField(default=0)),
                ('category_id', models.IntegerField()),
                ('collection_ids', models.JSONField(default=list)),
                ('attributes', models.JSONField(default=dict)),
                ('cover_image', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'products',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='productmodel',
            index=models.Index(fields=['category_id'], name='products_category_idx'),
        ),
        migrations.AddIndex(
            model_name='productmodel',
            index=models.Index(fields=['title'], name='products_title_idx'),
        ),
        migrations.AddIndex(
            model_name='productmodel',
            index=models.Index(fields=['author'], name='products_author_idx'),
        ),
    ]
