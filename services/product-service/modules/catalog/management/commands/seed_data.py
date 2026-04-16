from django.core.management.base import BaseCommand
from modules.catalog.infrastructure.models.product_model import ProductModel
from decimal import Decimal
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed 100 products (books)'

    def handle(self, *args, **options):
        books_data = [
            # Văn học Việt Nam (category_id=1)
            {'title': 'Dế Mèn Phiêu Lưu Ký', 'author': 'Tô Hoài', 'category_id': 1, 'price': 85000},
            {'title': 'Số Đỏ', 'author': 'Vũ Trọng Phụng', 'category_id': 1, 'price': 95000},
            {'title': 'Chí Phèo', 'author': 'Nam Cao', 'category_id': 1, 'price': 75000},
            {'title': 'Vợ Nhặt', 'author': 'Kim Lân', 'category_id': 1, 'price': 65000},
            {'title': 'Tắt Đèn', 'author': 'Ngô Tất Tố', 'category_id': 1, 'price': 80000},
            {'title': 'Lão Hạc', 'author': 'Nam Cao', 'category_id': 1, 'price': 70000},
            {'title': 'Truyện Kiều', 'author': 'Nguyễn Du', 'category_id': 1, 'price': 120000},
            {'title': 'Cho Tôi Xin Một Vé Đi Tuổi Thơ', 'author': 'Nguyễn Nhật Ánh', 'category_id': 1, 'price': 90000},
            {'title': 'Mắt Biếc', 'author': 'Nguyễn Nhật Ánh', 'category_id': 1, 'price': 95000},
            {'title': 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh', 'author': 'Nguyễn Nhật Ánh', 'category_id': 1, 'price': 100000},

            # Văn học nước ngoài (category_id=2)
            {'title': 'Đắc Nhân Tâm', 'author': 'Dale Carnegie', 'category_id': 2, 'price': 88000},
            {'title': 'Nhà Giả Kim', 'author': 'Paulo Coelho', 'category_id': 2, 'price': 79000},
            {'title': 'Hoàng Tử Bé', 'author': 'Antoine de Saint-Exupéry', 'category_id': 2, 'price': 65000},
            {'title': 'Harry Potter và Hòn Đá Phù Thủy', 'author': 'J.K. Rowling', 'category_id': 2, 'price': 150000},
            {'title': 'Harry Potter và Phòng Chứa Bí Mật', 'author': 'J.K. Rowling', 'category_id': 2, 'price': 155000},
            {'title': 'Harry Potter và Tên Tù Nhân Ngục Azkaban', 'author': 'J.K. Rowling', 'category_id': 2, 'price': 165000},
            {'title': 'Harry Potter và Chiếc Cốc Lửa', 'author': 'J.K. Rowling', 'category_id': 2, 'price': 180000},
            {'title': 'Sherlock Holmes Toàn Tập', 'author': 'Arthur Conan Doyle', 'category_id': 2, 'price': 250000},
            {'title': '1984', 'author': 'George Orwell', 'category_id': 2, 'price': 98000},
            {'title': 'Trại Súc Vật', 'author': 'George Orwell', 'category_id': 2, 'price': 75000},
            {'title': 'Cuốn Theo Chiều Gió', 'author': 'Margaret Mitchell', 'category_id': 2, 'price': 185000},
            {'title': 'Bố Già', 'author': 'Mario Puzo', 'category_id': 2, 'price': 145000},
            {'title': 'Gatsby Vĩ Đại', 'author': 'F. Scott Fitzgerald', 'category_id': 2, 'price': 85000},
            {'title': 'Đi Tìm Lẽ Sống', 'author': 'Viktor Frankl', 'category_id': 2, 'price': 95000},
            {'title': 'Suối Nguồn', 'author': 'Ayn Rand', 'category_id': 2, 'price': 220000},

            # Kinh tế (category_id=3)
            {'title': 'Cha Giàu Cha Nghèo', 'author': 'Robert Kiyosaki', 'category_id': 3, 'price': 110000},
            {'title': 'Nghĩ Giàu Làm Giàu', 'author': 'Napoleon Hill', 'category_id': 3, 'price': 99000},
            {'title': 'Dạy Con Làm Giàu Tập 1', 'author': 'Robert Kiyosaki', 'category_id': 3, 'price': 85000},
            {'title': 'Khởi Nghiệp Tinh Gọn', 'author': 'Eric Ries', 'category_id': 3, 'price': 135000},
            {'title': 'Từ Tốt Đến Vĩ Đại', 'author': 'Jim Collins', 'category_id': 3, 'price': 155000},
            {'title': 'Chiến Lược Đại Dương Xanh', 'author': 'W. Chan Kim', 'category_id': 3, 'price': 145000},
            {'title': 'Tư Duy Nhanh Và Chậm', 'author': 'Daniel Kahneman', 'category_id': 3, 'price': 189000},
            {'title': 'Người Giàu Có Nhất Thành Babylon', 'author': 'George S. Clason', 'category_id': 3, 'price': 78000},
            {'title': 'Bí Mật Tư Duy Triệu Phú', 'author': 'T. Harv Eker', 'category_id': 3, 'price': 115000},
            {'title': '7 Thói Quen Hiệu Quả', 'author': 'Stephen Covey', 'category_id': 3, 'price': 125000},

            # Tâm lý - Kỹ năng sống (category_id=4)
            {'title': 'Đời Ngắn Đừng Ngủ Dài', 'author': 'Robin Sharma', 'category_id': 4, 'price': 89000},
            {'title': 'Tuổi Trẻ Đáng Giá Bao Nhiêu', 'author': 'Rosie Nguyễn', 'category_id': 4, 'price': 76000},
            {'title': 'Cà Phê Cùng Tony', 'author': 'Tony Buổi Sáng', 'category_id': 4, 'price': 72000},
            {'title': 'Sức Mạnh Của Thói Quen', 'author': 'Charles Duhigg', 'category_id': 4, 'price': 135000},
            {'title': 'Tâm Lý Học Về Tiền', 'author': 'Morgan Housel', 'category_id': 4, 'price': 145000},
            {'title': 'Atomic Habits - Thay Đổi Tí Hon Hiệu Quả Bất Ngờ', 'author': 'James Clear', 'category_id': 4, 'price': 149000},
            {'title': 'Không Phải Sói Nhưng Cũng Đừng Là Cừu', 'author': 'Lê Hùng', 'category_id': 4, 'price': 95000},
            {'title': 'Bạn Đắt Giá Bao Nhiêu', 'author': 'Vãn Tình', 'category_id': 4, 'price': 85000},
            {'title': 'Người Nam Châm', 'author': 'Jack Canfield', 'category_id': 4, 'price': 98000},
            {'title': 'Dám Bị Ghét', 'author': 'Ichiro Kishimi', 'category_id': 4, 'price': 115000},

            # Thiếu nhi (category_id=5)
            {'title': 'Doraemon Tập 1', 'author': 'Fujiko F. Fujio', 'category_id': 5, 'price': 22000},
            {'title': 'Doraemon Tập 2', 'author': 'Fujiko F. Fujio', 'category_id': 5, 'price': 22000},
            {'title': 'Doraemon Tập 3', 'author': 'Fujiko F. Fujio', 'category_id': 5, 'price': 22000},
            {'title': 'Shin - Cậu Bé Bút Chì Tập 1', 'author': 'Yoshito Usui', 'category_id': 5, 'price': 20000},
            {'title': 'Conan Tập 1', 'author': 'Aoyama Gosho', 'category_id': 5, 'price': 25000},
            {'title': 'Conan Tập 2', 'author': 'Aoyama Gosho', 'category_id': 5, 'price': 25000},
            {'title': 'Doreamon Truyện Dài Tập 1', 'author': 'Fujiko F. Fujio', 'category_id': 5, 'price': 35000},
            {'title': 'Kính Vạn Hoa', 'author': 'Nguyễn Nhật Ánh', 'category_id': 5, 'price': 45000},
            {'title': 'Chuyện Con Mèo Dạy Hải Âu Bay', 'author': 'Luis Sepúlveda', 'category_id': 5, 'price': 55000},
            {'title': 'Charlie Và Nhà Máy Sôcôla', 'author': 'Roald Dahl', 'category_id': 5, 'price': 75000},

            # Khoa học - Công nghệ (category_id=6)
            {'title': 'Lược Sử Thời Gian', 'author': 'Stephen Hawking', 'category_id': 6, 'price': 125000},
            {'title': 'Sapiens Lược Sử Loài Người', 'author': 'Yuval Noah Harari', 'category_id': 6, 'price': 199000},
            {'title': 'Homo Deus Lược Sử Tương Lai', 'author': 'Yuval Noah Harari', 'category_id': 6, 'price': 209000},
            {'title': '21 Bài Học Cho Thế Kỷ 21', 'author': 'Yuval Noah Harari', 'category_id': 6, 'price': 189000},
            {'title': 'Cosmos', 'author': 'Carl Sagan', 'category_id': 6, 'price': 175000},
            {'title': 'Vũ Trụ Trong Vỏ Hạt Dẻ', 'author': 'Stephen Hawking', 'category_id': 6, 'price': 145000},
            {'title': 'Gene Ích Kỷ', 'author': 'Richard Dawkins', 'category_id': 6, 'price': 165000},
            {'title': 'Clean Code', 'author': 'Robert C. Martin', 'category_id': 6, 'price': 350000},
            {'title': 'The Pragmatic Programmer', 'author': 'David Thomas', 'category_id': 6, 'price': 380000},
            {'title': 'Design Patterns', 'author': 'Gang of Four', 'category_id': 6, 'price': 420000},

            # Lịch sử - Địa lý (category_id=7)
            {'title': 'Lịch Sử Việt Nam Bằng Tranh', 'author': 'Trần Bạch Đằng', 'category_id': 7, 'price': 85000},
            {'title': 'Đại Việt Sử Ký Toàn Thư', 'author': 'Ngô Sĩ Liên', 'category_id': 7, 'price': 350000},
            {'title': 'Việt Nam Sử Lược', 'author': 'Trần Trọng Kim', 'category_id': 7, 'price': 145000},
            {'title': 'Những Anh Hùng Trong Lịch Sử VN', 'author': 'Nhiều tác giả', 'category_id': 7, 'price': 125000},
            {'title': 'Thế Chiến Thứ Hai', 'author': 'Winston Churchill', 'category_id': 7, 'price': 295000},
            {'title': 'Súng, Vi Trùng và Thép', 'author': 'Jared Diamond', 'category_id': 7, 'price': 185000},
            {'title': 'Chiến Tranh Và Hòa Bình', 'author': 'Leo Tolstoy', 'category_id': 7, 'price': 245000},
            {'title': 'Một Cõi Đi Về', 'author': 'Trịnh Công Sơn', 'category_id': 7, 'price': 95000},
            {'title': 'Dấu Chân Người Lính', 'author': 'Nguyễn Minh Châu', 'category_id': 7, 'price': 78000},
            {'title': 'Hồi Ký Phạm Duy', 'author': 'Phạm Duy', 'category_id': 7, 'price': 165000},

            # Tiểu sử - Hồi ký (category_id=8)
            {'title': 'Steve Jobs', 'author': 'Walter Isaacson', 'category_id': 8, 'price': 225000},
            {'title': 'Elon Musk', 'author': 'Ashlee Vance', 'category_id': 8, 'price': 195000},
            {'title': 'Tự Truyện Benjamin Franklin', 'author': 'Benjamin Franklin', 'category_id': 8, 'price': 115000},
            {'title': 'Leonardo Da Vinci', 'author': 'Walter Isaacson', 'category_id': 8, 'price': 245000},
            {'title': 'Nhật Ký Anne Frank', 'author': 'Anne Frank', 'category_id': 8, 'price': 85000},
            {'title': 'Mandela Hồi Ký', 'author': 'Nelson Mandela', 'category_id': 8, 'price': 175000},
            {'title': 'Becoming - Michelle Obama', 'author': 'Michelle Obama', 'category_id': 8, 'price': 215000},
            {'title': 'Shoe Dog - Phil Knight', 'author': 'Phil Knight', 'category_id': 8, 'price': 165000},
            {'title': 'Einstein Cuộc Đời Và Vũ Trụ', 'author': 'Walter Isaacson', 'category_id': 8, 'price': 235000},
            {'title': 'Alibaba - Jack Ma', 'author': 'Duncan Clark', 'category_id': 8, 'price': 145000},

            # Giáo khoa - Tham khảo (category_id=9)
            {'title': 'Toán Cao Cấp Tập 1', 'author': 'Nguyễn Đình Trí', 'category_id': 9, 'price': 95000},
            {'title': 'Toán Cao Cấp Tập 2', 'author': 'Nguyễn Đình Trí', 'category_id': 9, 'price': 95000},
            {'title': 'Giải Tích 1', 'author': 'Đỗ Công Khanh', 'category_id': 9, 'price': 85000},
            {'title': 'Đại Số Tuyến Tính', 'author': 'Nguyễn Hữu Việt Hưng', 'category_id': 9, 'price': 75000},
            {'title': 'Vật Lý Đại Cương', 'author': 'Lương Duyên Bình', 'category_id': 9, 'price': 110000},
            {'title': 'Hóa Học Đại Cương', 'author': 'Nguyễn Đức Chung', 'category_id': 9, 'price': 98000},
            {'title': 'Tiếng Anh Giao Tiếp', 'author': 'Nhiều tác giả', 'category_id': 9, 'price': 125000},
            {'title': 'IELTS Academic Writing', 'author': 'Mat Clark', 'category_id': 9, 'price': 185000},
            {'title': 'TOEIC 990', 'author': 'ETS', 'category_id': 9, 'price': 245000},
            {'title': 'N3 Somatome', 'author': 'Sasaki Hitoko', 'category_id': 9, 'price': 165000},

            # Truyện tranh (category_id=10)
            {'title': 'One Piece Tập 1', 'author': 'Oda Eiichiro', 'category_id': 10, 'price': 25000},
            {'title': 'One Piece Tập 2', 'author': 'Oda Eiichiro', 'category_id': 10, 'price': 25000},
            {'title': 'Naruto Tập 1', 'author': 'Masashi Kishimoto', 'category_id': 10, 'price': 25000},
            {'title': 'Dragon Ball Tập 1', 'author': 'Akira Toriyama', 'category_id': 10, 'price': 30000},
            {'title': 'Attack on Titan Tập 1', 'author': 'Hajime Isayama', 'category_id': 10, 'price': 35000},
            {'title': 'Death Note Tập 1', 'author': 'Tsugumi Ohba', 'category_id': 10, 'price': 35000},
            {'title': 'Demon Slayer Tập 1', 'author': 'Koyoharu Gotouge', 'category_id': 10, 'price': 35000},
            {'title': 'My Hero Academia Tập 1', 'author': 'Kohei Horikoshi', 'category_id': 10, 'price': 30000},
            {'title': 'Jujutsu Kaisen Tập 1', 'author': 'Gege Akutami', 'category_id': 10, 'price': 35000},
            {'title': 'Spy x Family Tập 1', 'author': 'Tatsuya Endo', 'category_id': 10, 'price': 40000},
        ]

        publishers = ['NXB Trẻ', 'NXB Kim Đồng', 'NXB Văn Học', 'NXB Tổng Hợp', 'NXB Hội Nhà Văn',
                      'NXB Thế Giới', 'NXB Lao Động', 'Alpha Books', 'First News', 'IPM']

        for i, book_data in enumerate(books_data):
            pub_date = date(2020, 1, 1) + timedelta(days=random.randint(0, 1500))
            pages = random.randint(150, 600)
            stock = random.randint(10, 200)
            collection_ids = random.sample([1, 2, 3, 4, 5], k=random.randint(0, 2))

            product, created = ProductModel.objects.get_or_create(
                title=book_data['title'],
                defaults={
                    'author': book_data['author'],
                    'description': f"Cuốn sách {book_data['title']} của tác giả {book_data['author']}. Một tác phẩm đáng đọc.",
                    'price': Decimal(str(book_data['price'])),
                    'stock': stock,
                    'category_id': book_data['category_id'],
                    'collection_ids': collection_ids,
                    'attributes': {
                        'isbn': f'978-604-{random.randint(100, 999)}-{random.randint(1000, 9999)}-{random.randint(0, 9)}',
                        'publisher': random.choice(publishers),
                        'published_date': str(pub_date),
                        'pages': pages,
                    },
                }
            )
            result = 'Created' if created else 'Exists'
            self.stdout.write(f'{result}: "{product.title}"')

        self.stdout.write(self.style.SUCCESS(f'Seed {len(books_data)} books completed!'))
