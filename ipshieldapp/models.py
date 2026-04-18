from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
# ============================
# VALIDATORS (THÔNG BÁO TV)
# ============================
phone_validator = RegexValidator(
    regex=r'^\d+$',
    message='Số điện thoại chỉ được nhập chữ số'
)

number_validator = RegexValidator(
    regex=r'^\d+$',
    message='Trường này chỉ được nhập số'
)


# ============================
# KHÁCH HÀNG
# ============================
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = (
        ('personal', 'Cá nhân'),
        ('company', 'Doanh nghiệp'),
    )

    CUSTOMER_STATUS_CHOICES = (
        ('approved', 'Chờ duyệt'),
        ('pending', 'Đang xử lý'),
        ('completed', 'Hoàn tất'),
    )

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='personal',
        verbose_name='Loại khách hàng'
    )

    status = models.CharField(
        max_length=20,
        choices=CUSTOMER_STATUS_CHOICES,
        default='approved',
        verbose_name='Trạng thái'
    )

    customer_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Mã khách hàng'
    )

    name = models.CharField(
        max_length=255,
        verbose_name='Tên khách hàng'
    )

    address = models.CharField(
        max_length=255,
        verbose_name='Địa chỉ'
    )

    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        verbose_name='Số điện thoại'
    )

    email = models.EmailField(
        verbose_name='Email'
    )

    cccd = models.CharField(
        max_length=20,
        validators=[number_validator],
        blank=True,
        null=True,
        verbose_name='Số CCCD'
    )

    tax_code = models.CharField(
        max_length=20,
        validators=[number_validator],
        blank=True,
        null=True,
        verbose_name='Mã số thuế'
    )

    manager = models.CharField(
        max_length=255,
        verbose_name='Người phụ trách'
    )

    position = models.CharField(
        max_length=100,
        verbose_name='Chức danh'
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ghi chú'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    
    business_license = models.FileField(
        upload_to='images/business_licenses/',
        blank=True,
        null=True,
        verbose_name='File giấy phép kinh doanh'
    )

    register_year = models.DateField(
        blank=True,
        null=True,
        verbose_name='Năm đăng ký'
    )


    class Meta:
        verbose_name = 'Khách hàng'
        verbose_name_plural = 'Khách hàng'
        # 🆕 THÊM 2 FIELD NÀY

    password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Mật khẩu'
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lần đăng nhập cuối'
    )
    
    avatar = models.ImageField(
        upload_to='images/avatars/',
        blank=True,
        null=True,
        verbose_name='Ảnh đại diện'
    )

    def __str__(self):
        return f"{self.customer_code} - {self.name}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password or '')


# ============================
# HỢP ĐỒNG
# ============================
class ContractImage(models.Model):
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.CASCADE,
        related_name='contract_images'
    )
    image = models.ImageField(
        upload_to='images/contracts/',
        verbose_name='Ảnh chụp hợp đồng'
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Tên ảnh'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tải lên'
    )

    class Meta:
        verbose_name = 'Ảnh hợp đồng'
        verbose_name_plural = 'Ảnh hợp đồng'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Ảnh HĐ {self.contract.contract_no} - {self.name or self.id}"
# ============================
# HỢP ĐỒNG (Contract Model - CẬP NHẬT ĐẦY ĐỦ)
# ============================
class Contract(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('nhanhieu', 'Đăng ký nhãn hiệu'),
        ('banquyen', 'Bản quyền tác giả'),
        ('dkkd', 'Đăng ký kinh doanh'),
        ('dautu', 'Đăng ký đầu tư'),
        ('khac', 'Dịch vụ khác'),
    )

    CONTRACT_STATUS_CHOICES = (
        ('pending', 'Đang chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('paused', 'Ngưng'),
    )

    PAYMENT_TYPE_CHOICES = (
        ('full', 'Trả dứt điểm'),
        ('installment', 'Trả nhiều đợt'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contracts'
    )

    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES
    )

    contract_no = models.CharField(max_length=50, unique=True)

    # 🟢 GIÁ TRỊ HỢP ĐỒNG
    contract_value = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name='Giá trị hợp đồng'
    )

    # 🟢 TRẢ ĐỨT ĐIỂM / TRẢ NHIỀU ĐỢT
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        verbose_name='Hình thức thanh toán'
    )

    # 🟢 SỐ TIỀN TRẢ TRƯỚC
    prepaid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name='Số tiền trả trước'
    )

    # 🟢 NGÀY THANH TOÁN (cho trả dứt điểm)
    payment_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày thanh toán'
    )

    # 🆕 SỐ ĐỢT TRẢ GÓP
    number_of_installments = models.PositiveIntegerField(
        default=1,
        verbose_name='Số đợt trả góp',
        help_text='Số lần trả góp (áp dụng khi chọn trả nhiều đợt)'
    )

    # 🆕 KHOẢNG CÁCH GIỮA CÁC ĐỢT
    installment_interval_days = models.PositiveIntegerField(
        default=30,
        verbose_name='Khoảng cách giữa các đợt (ngày)',
        help_text='Số ngày giữa mỗi lần trả góp'
    )

    status = models.CharField(
        max_length=20,
        choices=CONTRACT_STATUS_CHOICES,
        default='pending'
    )
    
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Hợp đồng'
        verbose_name_plural = 'Hợp đồng'
        indexes = [
            models.Index(fields=['contract_no']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
        ]

    def clean(self):
        super().clean()

        if self.payment_type == 'full' and self.payment_date:
            if self.prepaid_amount != self.contract_value:
                raise ValidationError({
                    'prepaid_amount': 'Thanh toán dứt điểm phải bằng giá trị hợp đồng'
                })

        # 🆕 Validate số đợt trả góp
        if self.payment_type == 'installment' and self.number_of_installments < 1:
            raise ValidationError({
                'number_of_installments': 'Số đợt trả góp phải lớn hơn 0'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # Trong class Contract, thay thế phương thức create_installments():

    def create_installments(self):
        """Tự động tạo các đợt thanh toán RỖNG (chưa có số tiền)"""
        if self.payment_type != 'installment':
            return

        # Xóa các đợt cũ nếu có
        self.installments.all().delete()

        # Tạo các đợt thanh toán RỖNG
        from datetime import timedelta
        current_date = timezone.now().date()

        for i in range(self.number_of_installments):
            # Tính ngày đến hạn cho từng đợt
            due_date = current_date + timedelta(days=self.installment_interval_days * i)

            # Đợt đầu tiên có số tiền đã trả trước (nếu có)
            paid_amount = self.prepaid_amount if i == 0 else 0

            PaymentInstallment.objects.create(
                contract=self,
                amount=0,  # 🔥 ĐỂ TRỐNG, CHỜ NHẬP TAY
                paid_amount=paid_amount,
                due_date=due_date,
                is_paid=False,
                paid_date=None,
                notes=f"Đợt {i + 1}/{self.number_of_installments}"
            )

    @property
    def total_paid(self):
        """Tổng số tiền đã thanh toán"""
        return self.installments.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0

    @property
    def remaining_amount(self):
        """Số tiền còn lại phải trả"""
        return self.contract_value - self.total_paid

    @property
    def payment_progress(self):
        """% tiến độ thanh toán"""
        if self.contract_value == 0:
            return 0
        return round((self.total_paid / self.contract_value) * 100, 2)

    @property
    def is_fully_paid(self):
        """Đã thanh toán đủ chưa"""
        return self.total_paid >= self.contract_value
    
    # Trong class Contract
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def __str__(self):
        return f"{self.contract_no} - {self.get_service_type_display()}"


# ============================
# ĐỢT THANH TOÁN (PaymentInstallment Model)
# ============================
class PaymentInstallment(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='installments'
    )

    # TỔNG TIỀN ĐỢT NÀY
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Số tiền đợt thanh toán'
    )

    # SỐ TIỀN ĐÃ TRẢ
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Số tiền đã trả'
    )

    # NGÀY ĐẾN HẠN
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Ngày đến hạn'
    )

    # ĐÃ THANH TOÁN CHƯA
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Đã thanh toán'
    )

    # NGÀY THANH TOÁN THỰC TẾ
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Ngày thanh toán'
    )

    # GHI CHÚ
    notes = models.TextField(
        blank=True,
        verbose_name='Ghi chú'
    )
    # 🔴🔴🔴 THÊM 2 DÒNG NÀY 🔴🔴🔴
    is_exported_bill = models.BooleanField(
        default=False,
        verbose_name='Đã xuất hóa đơn'
    )

    bill_exported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Thời gian xuất hóa đơn'
    )
    # 🔴🔴🔴 KẾT THÚC 🔴🔴🔴
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đợt thanh toán'
        verbose_name_plural = 'Các đợt thanh toán'
        ordering = ['due_date', 'created_at']
        indexes = [
            models.Index(fields=['contract', 'is_paid']),
            models.Index(fields=['paid_date']),
            models.Index(fields=['due_date']),
        ]


    def save(self, *args, **kwargs):
        # ✅ BỎ QUA validation nếu chỉ update một số field nhất định
        if 'update_fields' in kwargs:
            # Không gọi full_clean() khi chỉ update specific fields
            super(PaymentInstallment, self).save(*args, **kwargs)
            return

        # ✅ Tự động cập nhật trạng thái (chỉ khi amount > 0)
        if self.amount > 0 and self.paid_amount >= self.amount:
            self.is_paid = True
            if not self.paid_date:
                self.paid_date = timezone.now().date()
        else:
            self.is_paid = False
            self.paid_date = None

        super().save(*args, **kwargs)

    def add_payment(self, amount, paid_date=None, notes=''):
        """Thêm thanh toán vào đợt này"""
        if amount <= 0:
            raise ValidationError('Số tiền phải lớn hơn 0')

        self.paid_amount += amount

        if self.paid_amount >= self.amount:
            self.is_paid = True
            self.paid_date = paid_date or timezone.now().date()

        if notes:
            self.notes = notes

        self.save()

    @property
    def remaining_amount(self):
        """Số tiền còn lại của đợt này"""
        return max(self.amount - self.paid_amount, 0)

    @property
    def is_overdue(self):
        """Đã quá hạn chưa"""
        if self.is_paid or not self.due_date:
            return False
        return timezone.now().date() > self.due_date

    def __str__(self):
        status = "✓" if self.is_paid else "✗"
        return f"{self.contract.contract_no} - {self.notes} ({status})"


# ============================
# LỊCH SỬ THANH TOÁN (PaymentLog Model)
# ============================
class PaymentLog(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='payment_logs',
        verbose_name='Hợp đồng'
    )

    installment = models.ForeignKey(
        PaymentInstallment,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Đợt thanh toán'
    )

    # SỐ TIỀN ĐÃ TRẢ
    amount_paid = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name='Số tiền thanh toán'
    )

    # THỜI GIAN THANH TOÁN
    paid_at = models.DateTimeField(
        verbose_name='Thời gian thanh toán'
    )

    # ĐÃ XUẤT HÓA ĐƠN CHƯA
    is_exported_bill = models.BooleanField(
        default=False,
        verbose_name='Đã xuất hóa đơn'
    )

    # THỜI GIAN XUẤT HÓA ĐƠN
    bill_exported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Thời gian xuất hóa đơn'
    )

    # GHI CHÚ
    notes = models.TextField(
        blank=True,
        verbose_name='Ghi chú'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lịch sử thanh toán'
        verbose_name_plural = 'Lịch sử thanh toán'
        ordering = ['-paid_at']
        indexes = [
            models.Index(fields=['contract', '-paid_at']),
            models.Index(fields=['installment', '-paid_at']),
        ]

    def __str__(self):
        return f"Thanh toán {self.amount_paid:,.0f} VNĐ - HĐ {self.contract.contract_no} - {self.paid_at.strftime('%d/%m/%Y %H:%M')}"


# Tài liệu đính kèm //
class Certificate(models.Model):
    # GenericForeignKey để liên kết với nhiều model
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        verbose_name='Loại đối tượng'
    )
    object_id = models.PositiveIntegerField(verbose_name='ID đối tượng')
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # File chứng nhận
    certificate_file = models.FileField(
        upload_to='images/certificates/',
        verbose_name='File chứng nhận'
    )
    
    # 🔥 THÊM 2 TRƯỜNG NÀY
    file = models.FileField(
        upload_to='images/certificates/',
        verbose_name='File đính kèm'
    )
    
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Tên file'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Mô tả'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tải lên'
    )
    
    class Meta:
        verbose_name = 'Tài liệu đính kèm'
        verbose_name_plural = 'Tài liệu đính kèm'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Certificate #{self.id} - {self.description or 'No description'}"
    
# ============================
# 1. NHÃN HIỆU
# ============================
class TrademarkService(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='trademarks'
    )

    # 🔥 TẤT CẢ TRƯỜNG ĐỀU blank=True, null=True
    applicant = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Người nộp đơn'
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Địa chỉ'
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )

    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        blank=True,
        null=True,
        verbose_name='Số điện thoại'
    )

    # 🔥 SỐ ĐƠN: UNIQUE + CHO PHÉP TRỐNG (null=True cho phép nhiều giá trị NULL)
    app_no = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Số đơn'
    )

    filing_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày nộp đơn'
    )

    trademark_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Tên nhãn hiệu'
    )

    trademark_image = models.ImageField(
        upload_to='images/trademark/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh nhãn hiệu'
    )

    classification = models.TextField(
        blank=True,
        null=True,
        verbose_name='Nhóm sản phẩm/dịch vụ'
    )

    publish_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày công bố'
    )
    # 🆕 THÊM TRƯỜNG NGÀY HỢP LẼ HÓA ĐƠN
    valid_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày hợp lệ hóa đơn',
        help_text='Ngày đơn được xác nhận hợp lệ'
    )
    decision_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày cấp'
    )

    certificates = GenericRelation(
        Certificate,
        related_query_name='trademark'
    )

    deny_document = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ngày từ chối'
    )

    class Meta:
        verbose_name = 'Nhãn hiệu'
        verbose_name_plural = 'Nhãn hiệu'

    def clean(self):
        super().clean()
        # 🔥 KIỂM TRA SỐ ĐƠN TRÙNG (chỉ khi có giá trị)
        if self.app_no:
            existing = TrademarkService.objects.filter(
                app_no=self.app_no
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({
                    'app_no': f'Số đơn "{self.app_no}" đã tồn tại!'
                })

    def __str__(self):
        return self.trademark_name or f"Nhãn hiệu #{self.id}"


# ============================
# 2. BẢN QUYỀN
# ============================
class CopyrightService(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='copyrights'
    )

    work_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Tên tác phẩm'
    )

    author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Tác giả'
    )

    owner = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Chủ sở hữu'
    )

    owner_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Địa chỉ chủ sở hữu'
    )

    type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Loại hình tác phẩm'
    )

    # 🔥 SỐ CHỨNG NHẬN: UNIQUE + CHO PHÉP TRỐNG
    certificate_no = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Số chứng nhận'
    )

    certificates = GenericRelation(
        Certificate,
        related_query_name='copyright_files'
    )

    class Meta:
        verbose_name = 'Bản quyền'
        verbose_name_plural = 'Bản quyền'

    def clean(self):
        super().clean()
        # 🔥 KIỂM TRA SỐ CHỨNG NHẬN TRÙNG (chỉ khi có giá trị)
        if self.certificate_no:
            existing = CopyrightService.objects.filter(
                certificate_no=self.certificate_no
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({
                    'certificate_no': f'Số chứng nhận "{self.certificate_no}" đã tồn tại!'
                })

    def __str__(self):
        return self.work_name or f"Bản quyền #{self.id}"


# ============================
# 3. ĐĂNG KÝ KINH DOANH
# ============================
class BusinessRegistrationService(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='business'
    )

    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Tên công ty'
    )

    business_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Loại hình kinh doanh'
    )

    # 🔥 MÃ SỐ THUẾ: UNIQUE + CHO PHÉP TRỐNG
    tax_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Mã số thuế'
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Địa chỉ'
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )

    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        blank=True,
        null=True,
        verbose_name='Số điện thoại'
    )

    legal_representative = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Người đại diện pháp luật'
    )

    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Chức danh'
    )

    charter_capital = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Vốn điều lệ'
    )

    certificates = GenericRelation(
        Certificate,
        related_query_name='business_files'
    )

    registration_certificate = models.FileField(
        upload_to='images/registration_certificates/',
        blank=True,
        null=True,
        verbose_name='File chứng nhận đăng ký kinh doanh'
    )
    
    class Meta:
        verbose_name = 'ĐKKD'
        verbose_name_plural = 'ĐKKD'

    def clean(self):
        super().clean()
        # 🔥 KIỂM TRA MÃ SỐ THUẾ TRÙNG (chỉ khi có giá trị)
        if self.tax_code:
            existing = BusinessRegistrationService.objects.filter(
                tax_code=self.tax_code
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({
                    'tax_code': f'Mã số thuế "{self.tax_code}" đã tồn tại!'
                })

    def __str__(self):
        return self.company_name or f"ĐKKD #{self.id}"


# ============================
# 4. ĐĂNG KÝ ĐẦU TƯ
# ============================
class InvestmentService(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='investment'
    )

    # 🔥 MÃ DỰ ÁN: UNIQUE + CHO PHÉP TRỐNG
    project_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Mã dự án'
    )

    investor = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Nhà đầu tư'
    )

    project_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Tên dự án'
    )

    objective = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mục tiêu dự án'
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Địa chỉ'
    )

    total_capital = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Tổng vốn'
    )

    certificates = GenericRelation(
        Certificate,
        related_query_name='investment_files'
    )

    class Meta:
        verbose_name = 'Đầu tư'
        verbose_name_plural = 'Đầu tư'

    def clean(self):
        super().clean()
        # 🔥 KIỂM TRA MÃ DỰ ÁN TRÙNG (chỉ khi có giá trị)
        if self.project_code:
            existing = InvestmentService.objects.filter(
                project_code=self.project_code
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({
                    'project_code': f'Mã dự án "{self.project_code}" đã tồn tại!'
                })

    def __str__(self):
        return self.project_name or f"Dự án #{self.id}"


# ============================
# 5. DỊCH VỤ KHÁC
# ============================
class OtherService(models.Model):
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='other_service'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mô tả dịch vụ'
    )

    legal_representative = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Người đại diện'
    )

    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Chức danh'
    )

    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        blank=True,
        null=True,
        verbose_name='Số điện thoại'
    )

    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )

    certificates = GenericRelation(
        Certificate,
        related_query_name='other_service_files'
    )

    class Meta:
        verbose_name = 'Dịch vụ khác'
        verbose_name_plural = 'Dịch vụ khác'

    def __str__(self):
        return f"Dịch vụ khác #{self.id}"


# ============================
# LỊCH SỬ HỢP ĐỒNG
# ============================
class ContractHistory(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='histories'
    )

    user = models.CharField(max_length=255)
    action = models.CharField(max_length=255)

    old_data = models.TextField(blank=True, null=True)
    new_data = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract.contract_no} - {self.action}"


# ============================
# CAROUSEL
# ============================
class Slider(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='sliders/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# ============================
# MASCOT
# ============================
class Mascot(models.Model):
    title = models.CharField(max_length=100)
    speech = models.CharField(max_length=255, default="Xin chào! Tôi là Toki!")
    image = models.ImageField(upload_to='mascots/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# ============================
# NHÃN HIỆU ĐỘC QUYỀN
# ============================
class NhanHieuDocQuyen(models.Model):
    name = models.CharField("Tên nhãn hiệu", max_length=100, blank=True)
    image = models.ImageField("Ảnh nhãn hiệu", upload_to="logokhachhang/logobrand/")
    is_active = models.BooleanField("Hiển thị", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nhãn hiệu độc quyền"
        verbose_name_plural = "Nhãn hiệu độc quyền"

    def __str__(self):
        return self.name or f"Nhãn hiệu {self.id}"
    
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Ảnh đại diện')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số điện thoại')
    customer = models.OneToOneField(
        'Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profile',
        verbose_name='Khách hàng liên kết'
    )

    def is_customer(self):
        return self.customer is not None
    def __str__(self):
        return f"Profile của {self.user.username}"

# ============================
# NHẬT KÝ HOẠT ĐỘNG KHÁCH HÀNG
# ============================
class CustomerActivityLog(models.Model):
    ACTION_CHOICES = (
        ('login',           'Đăng Nhập'),
        ('logout',          'Đăng Xuất'),
        ('view_contract',   'Xem Hợp Đồng'),
        ('change_password', 'Đổi Mật Khẩu'),
        ('update_profile',  'Cập Nhật Hồ Sơ'),
        ('support_request',  'Yêu Cầu Hỗ Trợ')
    )

    customer   = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='activity_logs', verbose_name='Khách hàng'
    )
    action     = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name='Hành động')
    note       = models.CharField(max_length=255, blank=True, verbose_name='Ghi chú')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')

    class Meta:
        verbose_name = 'Nhật ký hoạt động KH'
        verbose_name_plural = 'Nhật ký hoạt động KH'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]

    def __str__(self):
        return f"{self.customer.customer_code} — {self.get_action_display()} — {self.created_at:%d/%m/%Y %H:%M}"
class CustomerDocument(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file = models.FileField(
        upload_to='images/customer_documents/',
        verbose_name='File đính kèm'
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Tên file'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tải lên'
    )

    class Meta:
        verbose_name = 'Tài liệu khách hàng'
        verbose_name_plural = 'Tài liệu khách hàng'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.customer.customer_code} - {self.name or self.file.name}"