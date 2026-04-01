from django.core.management.base import BaseCommand
from app.models import Category, Collection


class Command(BaseCommand):
    help = 'Seed categories and collections'

    def handle(self, *args, **options):
        # Create categories
        categories = [
            {'name': 'Văn học Việt Nam', 'description': 'Sách văn học Việt Nam'},
            {'name': 'Văn học nước ngoài', 'description': 'Sách văn học nước ngoài'},
            {'name': 'Kinh tế', 'description': 'Sách kinh tế, kinh doanh'},
            {'name': 'Tâm lý - Kỹ năng sống', 'description': 'Sách tâm lý, self-help'},
            {'name': 'Thiếu nhi', 'description': 'Sách dành cho thiếu nhi'},
            {'name': 'Khoa học - Công nghệ', 'description': 'Sách khoa học và công nghệ'},
            {'name': 'Lịch sử - Địa lý', 'description': 'Sách lịch sử, địa lý'},
            {'name': 'Tiểu sử - Hồi ký', 'description': 'Sách tiểu sử, hồi ký'},
            {'name': 'Giáo khoa - Tham khảo', 'description': 'Sách giáo khoa, tham khảo'},
            {'name': 'Truyện tranh', 'description': 'Manga, comic, truyện tranh'},
        ]

        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'{status}: Category "{cat.name}"')

        # Create collections
        collections = [
            {'name': 'Sách bán chạy', 'description': 'Top sách bán chạy nhất'},
            {'name': 'Sách mới', 'description': 'Sách mới xuất bản'},
            {'name': 'Sách giảm giá', 'description': 'Sách đang khuyến mãi'},
            {'name': 'Sách hay nên đọc', 'description': 'Sách được đề xuất'},
            {'name': 'Tác giả nổi tiếng', 'description': 'Sách của các tác giả nổi tiếng'},
        ]

        for col_data in collections:
            col, created = Collection.objects.get_or_create(
                name=col_data['name'],
                defaults={'description': col_data['description']}
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'{status}: Collection "{col.name}"')

        self.stdout.write(self.style.SUCCESS('Seed catalog data completed!'))
