from django.core.management.base import BaseCommand
from app.models import User


class Command(BaseCommand):
    help = 'Seed users (customers, staff, manager)'

    def handle(self, *args, **options):
        # Create manager
        manager, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@bookstore.com',
                'first_name': 'Quản',
                'last_name': 'Lý',
                'role': 'manager',
                'phone': '0901234567',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            self.stdout.write(f'Created: Manager "manager"')
        else:
            self.stdout.write(f'Exists: Manager "manager"')

        # Create staff accounts
        staff_list = [
            {'username': 'staff1', 'email': 'staff1@bookstore.com', 'first_name': 'Nhân', 'last_name': 'Viên A', 'phone': '0911111111'},
            {'username': 'staff2', 'email': 'staff2@bookstore.com', 'first_name': 'Nhân', 'last_name': 'Viên B', 'phone': '0911111112'},
            {'username': 'staff3', 'email': 'staff3@bookstore.com', 'first_name': 'Nhân', 'last_name': 'Viên C', 'phone': '0911111113'},
            {'username': 'nhanvien', 'email': 'nhanvien@bookstore.com', 'first_name': 'Trần', 'last_name': 'Văn Nhân', 'phone': '0911111114'},
            {'username': 'thukho', 'email': 'thukho@bookstore.com', 'first_name': 'Lê', 'last_name': 'Thị Kho', 'phone': '0911111115'},
        ]

        for staff_data in staff_list:
            staff, created = User.objects.get_or_create(
                username=staff_data['username'],
                defaults={
                    'email': staff_data['email'],
                    'first_name': staff_data['first_name'],
                    'last_name': staff_data['last_name'],
                    'role': 'staff',
                    'phone': staff_data['phone'],
                    'is_staff': True,
                }
            )
            if created:
                staff.set_password('staff123')
                staff.save()
                self.stdout.write(f'Created: Staff "{staff.username}"')
            else:
                self.stdout.write(f'Exists: Staff "{staff.username}"')

        # Create customer accounts
        customers = [
            {'username': 'customer1', 'email': 'customer1@gmail.com', 'first_name': 'Nguyễn', 'last_name': 'Văn A', 'phone': '0921111111'},
            {'username': 'customer2', 'email': 'customer2@gmail.com', 'first_name': 'Trần', 'last_name': 'Thị B', 'phone': '0921111112'},
            {'username': 'customer3', 'email': 'customer3@gmail.com', 'first_name': 'Lê', 'last_name': 'Văn C', 'phone': '0921111113'},
            {'username': 'customer4', 'email': 'customer4@gmail.com', 'first_name': 'Phạm', 'last_name': 'Thị D', 'phone': '0921111114'},
            {'username': 'customer5', 'email': 'customer5@gmail.com', 'first_name': 'Hoàng', 'last_name': 'Văn E', 'phone': '0921111115'},
            {'username': 'khachhang', 'email': 'khachhang@gmail.com', 'first_name': 'Khách', 'last_name': 'Hàng', 'phone': '0921111116'},
            {'username': 'nguoidung', 'email': 'nguoidung@gmail.com', 'first_name': 'Người', 'last_name': 'Dùng', 'phone': '0921111117'},
            {'username': 'test', 'email': 'test@gmail.com', 'first_name': 'Test', 'last_name': 'User', 'phone': '0921111118'},
            {'username': 'demo', 'email': 'demo@gmail.com', 'first_name': 'Demo', 'last_name': 'Account', 'phone': '0921111119'},
            {'username': 'user', 'email': 'user@gmail.com', 'first_name': 'User', 'last_name': 'Normal', 'phone': '0921111120'},
        ]

        for cust_data in customers:
            customer, created = User.objects.get_or_create(
                username=cust_data['username'],
                defaults={
                    'email': cust_data['email'],
                    'first_name': cust_data['first_name'],
                    'last_name': cust_data['last_name'],
                    'role': 'customer',
                    'phone': cust_data['phone'],
                }
            )
            if created:
                customer.set_password('customer123')
                customer.save()
                self.stdout.write(f'Created: Customer "{customer.username}"')
            else:
                self.stdout.write(f'Exists: Customer "{customer.username}"')

        self.stdout.write(self.style.SUCCESS('Seed users completed!'))
        self.stdout.write('')
        self.stdout.write('=== LOGIN CREDENTIALS ===')
        self.stdout.write('Manager:  manager / manager123')
        self.stdout.write('Staff:    staff1, staff2, staff3, nhanvien, thukho / staff123')
        self.stdout.write('Customer: customer1-5, khachhang, nguoidung, test, demo, user / customer123')
