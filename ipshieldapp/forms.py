from django import forms
from .models import (
    Customer,
    Contract,
    TrademarkService,
    CopyrightService,
    BusinessRegistrationService,
    InvestmentService,
    OtherService,
)

# ======================================================
# CUSTOMER FORM
# ======================================================
class CustomerForm(forms.ModelForm):

    # 🔴 BẮT BUỘC EMAIL
    email = forms.EmailField(
        required=True,
        label='Email',
        error_messages={
            'required': 'Vui lòng nhập email',
            'invalid': 'Email không hợp lệ',
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'required': 'required',
        })
    )
    class Meta:
        model = Customer
        fields = [
            'customer_type',
            'status',
            'customer_code',
            'name',
            'address',
            'email',
            'phone',
            'cccd',
            'tax_code',
            'manager',
            'position',
            'note',
        ]

        labels = {
            'customer_type': 'Loại khách hàng',
            'status': 'Trạng thái khách hàng',
            'customer_code': 'Mã khách hàng',
            'name': 'Tên khách hàng',
            'address': 'Địa chỉ',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'cccd': 'Số CCCD',
            'tax_code': 'Mã số thuế',
            'manager': 'Người phụ trách',
            'position': 'Chức danh',
            'note': 'Ghi chú',
        }

        widgets = {
            'customer_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'customer_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'cccd': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_code': forms.TextInput(attrs={'class': 'form-control'}),
            'manager': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # 🔒 KHÓA LOẠI KHÁCH HÀNG KHI EDIT
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Ẩn select loại khách hàng
            self.fields['customer_type'].widget = forms.HiddenInput()

    # 🧠 DỌN DỮ LIỆU THEO LOẠI KHÁCH
    def clean(self):
        cleaned_data = super().clean()
        ctype = cleaned_data.get('customer_type')

        if ctype == 'personal':
            cleaned_data['tax_code'] = None

        if ctype == 'company':
            cleaned_data['cccd'] = None

        return cleaned_data


# ======================================================
# CUSTOMER STATUS FORM (CHỈ ĐỔI TRẠNG THÁI)
# ======================================================
class CustomerStatusForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['status']

        labels = {
            'status': 'Trạng thái khách hàng',
        }

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

# ======================================================
# CONTRACT FORM  (⚠️ CÓ STATUS – QUAN TRỌNG)
# ======================================================
from django import forms
from .models import Contract

from django import forms
from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'customer',
            'service_type',
            'contract_no',
            'contract_value',
            'payment_type',
            'prepaid_amount',
            'number_of_installments',  # 🆕
            'installment_interval_days',  # 🆕
        ]

        labels = {
            'customer': 'Khách hàng',
            'service_type': 'Loại dịch vụ',
            'contract_no': 'Số hợp đồng',
            'contract_value': 'Giá trị hợp đồng',
            'payment_type': 'Hình thức thanh toán',
            'prepaid_amount': 'Số tiền trả trước (VNĐ)',
        }

        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contract_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: HD-001'
            }),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập giá trị hợp đồng',
                'min': 0
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_payment_type'
            }),
            'prepaid_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số tiền trả trước',
                'min': 0
            }),
            # 🆕 THÊM WIDGETS MỚI
            'number_of_installments': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 3, 6, 12...',
                'min': 1,
                'value': 1,
                'id': 'id_number_of_installments'
            }),
            'installment_interval_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 30 (1 tháng)',
                'min': 1,
                'value': 30,
                'id': 'id_installment_interval_days'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Required fields
        self.fields['customer'].required = True
        self.fields['service_type'].required = True
        self.fields['contract_no'].required = True
        self.fields['contract_value'].required = True
        self.fields['payment_type'].required = True

        # Không bắt buộc
        self.fields['prepaid_amount'].required = False
        self.fields['number_of_installments'].required = False
        self.fields['installment_interval_days'].required = False

    def clean(self):
        cleaned_data = super().clean()
        contract_value = cleaned_data.get('contract_value') or 0
        prepaid_amount = cleaned_data.get('prepaid_amount') or 0
        payment_type = cleaned_data.get('payment_type')
        number_of_installments = cleaned_data.get('number_of_installments') or 1

        # Validate số tiền trả trước
        if prepaid_amount < 0:
            raise forms.ValidationError({
                'prepaid_amount': 'Số tiền trả trước không được nhỏ hơn 0'
            })

        if prepaid_amount > contract_value:
            raise forms.ValidationError({
                'prepaid_amount': 'Số tiền trả trước không được lớn hơn giá trị hợp đồng'
            })

        # 🆕 Validate số đợt trả góp
        if payment_type == 'installment' and number_of_installments < 1:
            raise forms.ValidationError({
                'number_of_installments': 'Số đợt trả góp phải lớn hơn 0'
            })

        return cleaned_data


# ======================================================
# 1. NHÃN HIỆU
# ======================================================
class TrademarkForm(forms.ModelForm):
    class Meta:
        model = TrademarkService
        exclude = ['contract']

        labels = {
            'applicant': 'Người nộp đơn',
            'address': 'Địa chỉ',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'app_no': 'Số đơn',
            'filing_date': 'Ngày nộp đơn',
            'trademark_image': 'Hình ảnh nhãn hiệu',
            'valid_date': 'Ngày hợp lệ hình thức đơn',
            'classification': 'Nhóm sản phẩm/dịch vụ',
            'publish_date': 'Ngày công bố',
            'decision_date': 'Ngày cấp',
            'certificates': 'File chứng nhận',
        }

        widgets = {
            'applicant': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'app_no': forms.TextInput(attrs={'class': 'form-control'}),
            'valid_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'filing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'classification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'publish_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'decision_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'trademark_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'certificates': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ======================================================
# 2. BẢN QUYỀN
# ======================================================
class CopyrightForm(forms.ModelForm):
    class Meta:
        model = CopyrightService
        exclude = ['contract']

        labels = {
            'work_name': 'Tên tác phẩm',
            'author': 'Tác giả',
            'owner': 'Chủ sở hữu',
            'owner_address': 'Địa chỉ chủ sở hữu',
            'type': 'Loại hình tác phẩm',
            'certificate_no': 'Số chứng nhận',
            'certificates': 'File chứng nhận',
        }

        widgets = {
            'work_name': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_address': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'certificate_no': forms.TextInput(attrs={'class': 'form-control'}),
            'certificates': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ======================================================
# 3. ĐĂNG KÝ KINH DOANH
# ======================================================
class BusinessRegistrationForm(forms.ModelForm):
    class Meta:
        model = BusinessRegistrationService
        exclude = ['contract']

        labels = {
            'company_name': 'Tên công ty',
            'business_type': 'Loại hình kinh doanh',
            'tax_code': 'Mã số thuế',
            'address': 'Địa chỉ',
            'email': 'Email',
            'phone': 'SĐT',
            'legal_representative': 'Người đại diện pháp luật',
            'position': 'Chức danh',
            'charter_capital': 'Vốn điều lệ',
            'certificates': 'File chứng nhận',
        }

        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_representative': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'charter_capital': forms.TextInput(attrs={'class': 'form-control'}),
            'certificates': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ======================================================
# 4. ĐĂNG KÝ ĐẦU TƯ
# ======================================================
class InvestmentForm(forms.ModelForm):
    class Meta:
        model = InvestmentService
        exclude = ['contract']

        labels = {
            'project_code': 'Mã dự án',
            'investor': 'Nhà đầu tư',
            'project_name': 'Tên dự án',
            'objective': 'Mục tiêu dự án',
            'address': 'Địa chỉ',
            'total_capital': 'Tổng vốn',
            'certificates': 'File chứng nhận',
        }

        widgets = {
            'project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'investor': forms.TextInput(attrs={'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'total_capital': forms.TextInput(attrs={'class': 'form-control'}),
            'certificates': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ======================================================
# 5. DỊCH VỤ KHÁC
# ======================================================
class OtherServiceForm(forms.ModelForm):
    class Meta:
        model = OtherService
        exclude = ['contract']

        labels = {
            'description': 'Mô tả dịch vụ',
            'legal_representative': 'Người đại diện',
            'position': 'Chức danh',
            'phone': 'Số điện thoại',
            'email': 'Email',
            'certificates': 'File đính kèm',
        }

        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'legal_representative': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chỉ nhập số'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'certificates': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
from .models import PaymentInstallment


class PaymentInstallmentForm(forms.ModelForm):
    class Meta:
        model = PaymentInstallment
        fields = ['is_paid', 'paid_date']

        labels = {
            'is_paid': 'Đã thanh toán',
            'paid_date': 'Ngày thanh toán',
        }

        widgets = {
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Sửa lại thành datetime-local hoặc date để người dùng tự chọn
            'paid_date': forms.DateInput(attrs={
                'type': 'date', # Hoặc 'datetime-local' nếu muốn có cả giờ
                'class': 'form-control'
            }),
        }
from django.forms import modelformset_factory

TrademarkFormSet = modelformset_factory(
    TrademarkService,
    form=TrademarkForm,
    extra=0,
    can_delete=True
)

CopyrightFormSet = modelformset_factory(
    CopyrightService,
    form=CopyrightForm,
    extra=0,
    can_delete=True
)

# Thêm vào cuối file forms.py

from .models import PaymentInstallment


# Trong forms.py

class InstallmentAmountForm(forms.ModelForm):
    """Form để nhập số tiền cho từng đợt"""

    class Meta:
        model = PaymentInstallment
        fields = ['amount', 'due_date', 'notes']

        labels = {
            'amount': 'Số tiền đợt này (VNĐ)',
            'due_date': 'Ngày đến hạn',
            'notes': 'Ghi chú',
        }

        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số tiền',
                'min': 0,
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VD: Đợt 1/3'
            }),
        }

    def clean(self):
        """Override clean để validate riêng, không gọi model.clean()"""
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')

        # Chỉ validate amount
        if amount is not None and amount < 0:
            raise forms.ValidationError({'amount': 'Số tiền không được âm'})

        return cleaned_data




# Tạo formset
InstallmentFormSet = modelformset_factory(
    PaymentInstallment,
    form=InstallmentAmountForm,
    extra=0,
    can_delete=False
)


#trang ho so
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, required=False, label='Tên',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150, required=False, label='Họ',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False, label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone']
        labels = {
            'avatar': 'Ảnh đại diện',
            'phone': 'Số điện thoại',
        }
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
        if commit:
            profile.save()
        return profile




