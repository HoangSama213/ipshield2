from django.contrib import admin
from .models import *



from django.contrib.auth.hashers import make_password

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ("customer_code", "name", "customer_type", "phone", "email", "created_at")
    list_filter   = ("customer_type", "created_at")
    search_fields = ("customer_code", "name", "phone", "email")
    ordering      = ("-created_at",)

    # 🆕 Action đặt mật khẩu mặc định = mã khách hàng
    actions = ['reset_password_to_code']

    def reset_password_to_code(self, request, queryset):
        for customer in queryset:
            customer.set_password(customer.customer_code)
            customer.save(update_fields=['password'])
        self.message_user(request, f'✅ Đã reset mật khẩu về mã KH cho {queryset.count()} khách.')
    reset_password_to_code.short_description = '🔑 Reset mật khẩu về mã khách hàng'

    def save_model(self, request, obj, form, change):
        # Nếu field password không phải hash thì tự hash
        if obj.password and not obj.password.startswith('pbkdf2_'):
            obj.set_password(obj.password)
        # Nếu chưa có mật khẩu → đặt mặc định = mã KH
        if not obj.password:
            obj.set_password(obj.customer_code)
        super().save_model(request, obj, form, change)


# ============================
# INLINE CHO CÁC DỊCH VỤ
# ============================
class TrademarkServiceInline(admin.StackedInline):
    model = TrademarkService
    extra = 0


class CopyrightServiceInline(admin.StackedInline):
    model = CopyrightService
    extra = 0


class BusinessRegistrationInline(admin.StackedInline):
    model = BusinessRegistrationService
    extra = 0


class InvestmentServiceInline(admin.StackedInline):
    model = InvestmentService
    extra = 0


class OtherServiceInline(admin.StackedInline):
    model = OtherService
    extra = 0


# ============================
# HỢP ĐỒNG
# ============================
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_no", "customer", "service_type", "created_at")
    list_filter = ("service_type", "created_at")
    search_fields = ("contract_no", "customer__name")
    ordering = ("-created_at",)

    inlines = [
        TrademarkServiceInline,
        CopyrightServiceInline,
        BusinessRegistrationInline,
        InvestmentServiceInline,
        OtherServiceInline
    ]

    # Hiển thị label tiếng Việt
    fieldsets = (
        ("Thông tin hợp đồng", {
            "fields": ("customer", "service_type", "contract_no","prepaid_amount","contract_value")
        }),
    )


# ============================
# LỊCH SỬ HỢP ĐỒNG
# ============================
@admin.register(ContractHistory)
class ContractHistoryAdmin(admin.ModelAdmin):
    list_display = ("contract", "user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("contract__contract_no", "user")


# ============================
#carousel
# ============================
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

# ============================
#mascot
# ============================
@admin.register(Mascot)
class MascotAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')




@admin.register(NhanHieuDocQuyen)
class NhanHieuDocQuyenAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

# Thêm vào admin.py
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Hồ sơ & phân quyền'
    # Hiển thị field customer để admin dễ liên kết
    fields = ['avatar', 'phone', 'customer']

class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
