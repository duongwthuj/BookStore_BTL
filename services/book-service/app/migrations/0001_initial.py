from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField(default=0)),
                ('category_id', models.IntegerField()),
                ('collection_ids', models.JSONField(default=list)),
                ('cover_image', models.URLField(blank=True, null=True)),
                ('isbn', models.CharField(blank=True, max_length=20)),
                ('publisher', models.CharField(blank=True, max_length=255)),
                ('published_date', models.DateField(blank=True, null=True)),
                ('pages', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['category_id'], name='app_book_categor_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['title'], name='app_book_title_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['author'], name='app_book_author_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['isbn'], name='app_book_isbn_idx'),
        ),
    ]
