# ===============================================
# IMPORTS
# ===============================================
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404
from django.db import IntegrityError
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

def lock_contract_fields(contract_form):

    for field_name, field in contract_form.fields.items():
        field.disabled = True
        field.widget.attrs['readonly'] = True
        field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' readonly-field'

# ===============================================
# CUSTOMER LIST + SEARCH
# ===============================================
def home(request):
    q = request.GET.get('q', '').strip()
    customers = Customer.objects.all()

    if q:
        customers = customers.filter(
            Q(customer_code__icontains=q) |
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    sliders = Slider.objects.filter(is_active=True)
    mascots = Mascot.objects.filter(is_active=True)
    nhanhieudocquyen = NhanHieuDocQuyen.objects.filter(is_active=True).order_by('id')

    return render(request, 'khachhang.html', {
        'customers': customers,
        'sliders': sliders,
        'mascots': mascots,
        "nhanhieudocquyen": nhanhieudocquyen,
    })

# ===============================================
# CUSTOMER CREATE (ĐÃ SỬA - XỬ LÝ TRÙNG MÃ)
# ===============================================
def add_contract(request):
    if request.method == 'POST':
        print("\n" + "=" * 60)
        print("🔍 POST REQUEST RECEIVED")
        print("=" * 60)

        # Debug: Print all POST data
        print("\n📋 POST Data Keys:")
        for key in request.POST.keys():
            if 'trademark' in key or 'copyright' in key:
                print(f"  {key}: {request.POST.get(key)}")

        # ===== VALIDATE CONTRACT FORM =====
        contract_form = ContractForm(request.POST, request.FILES)

        if not contract_form.is_valid():
            print("\n❌ Contract form invalid:")
            print(contract_form.errors)
            for field, errors in contract_form.errors.items():
                for error in errors:
                    field_label = contract_form.fields.get(field).label if field in contract_form.fields else field
                    messages.error(request, f"{field_label}: {error}")

            return render(request, "add_contract.html", {
                'contract_form': contract_form,
                'trademark_formset': TrademarkFormSet(request.POST, request.FILES, prefix='trademark'),
                'copyright_formset': CopyrightFormSet(request.POST, request.FILES, prefix='copyright'),
                'business_form': BusinessRegistrationForm(request.POST, request.FILES),
                'investment_form': InvestmentForm(request.POST, request.FILES),
                'other_form': OtherServiceForm(request.POST, request.FILES),
            })

        print("✅ Contract form valid")

        # ===== SAVE CONTRACT =====
        contract = contract_form.save(commit=False)
        contract.status = 'completed' if contract.payment_type == 'full' else 'processing'

        try:
            contract.save()
            print(f"✅ Contract saved: {contract.contract_no}")
            
            # ===== HANDLE SERVICE BASED ON TYPE =====
            service_type = contract.service_type
            print(f"\n📦 Processing service type: {service_type}")

            # ==================================================
            #           🔥 NHÃN HIỆU (TRADEMARK)
            # ==================================================
            if service_type == 'nhanhieu':
                print("\n🏷️ Processing TRADEMARK formset...")

                trademark_formset = TrademarkFormSet(
                    request.POST,
                    request.FILES,
                    prefix='trademark'
                )

                print(f"   Management form - TOTAL_FORMS: {request.POST.get('trademark-TOTAL_FORMS')}")
                print(f"   Management form - INITIAL_FORMS: {request.POST.get('trademark-INITIAL_FORMS')}")

                if not trademark_formset.is_valid():
                    print("❌ Trademark formset invalid:")
                    print(f"   Errors: {trademark_formset.errors}")
                    print(f"   Non-form errors: {trademark_formset.non_form_errors()}")

                    contract.delete()

                    # Show formset errors properly
                    for idx, form_errors in enumerate(trademark_formset.errors):
                        if form_errors:
                            for field, errors in form_errors.items():
                                for error in errors:
                                    messages.error(request, f"Nhãn hiệu #{idx + 1} - {field}: {error}")

                    # Show non-form errors
                    for error in trademark_formset.non_form_errors():
                        messages.error(request, f"Lỗi formset: {error}")

                    return render(request, "add_contract.html", {
                        'contract_form': contract_form,
                        'trademark_formset': trademark_formset,
                        'copyright_formset': CopyrightFormSet(prefix='copyright',
                                                            queryset=CopyrightService.objects.none()),
                        'business_form': BusinessRegistrationForm(),
                        'investment_form': InvestmentForm(),
                        'other_form': OtherServiceForm(),
                    })

                print("✅ Trademark formset valid")

                # Count valid forms BEFORE saving
                valid_forms = [
                    form for form in trademark_formset
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                ]

                # 🔥 CHO PHÉP LƯU KHÔNG CẦN DỊCH VỤ
                if len(valid_forms) == 0:
                    print("⚠️ No trademark data provided, but contract saved")
                    messages.warning(request, "⚠️ Hợp đồng đã lưu nhưng chưa có thông tin nhãn hiệu")
                else:
                    # Save valid forms
                    saved_count = 0
                    for idx, form in enumerate(valid_forms):
                        # 🔥 LƯU TRADEMARK TRƯỚC
                        instance = form.save(commit=False)
                        instance.contract = contract
                        instance.save()
                        saved_count += 1

                        # 🔥 SAU ĐÓ MỚI XỬ LÝ FILE (instance đã tồn tại)
                        files = request.FILES.getlist(f'trademark_files_{idx}')
                        print(f"   📎 Found {len(files)} files for trademark #{idx}")

                        for f in files:
                            Certificate.objects.create(
                                content_object=instance,
                                file=f,
                                name=f.name,
                            )
                            print(f"      ✅ Saved file: {f.name}")

                    print(f"✅ Saved {saved_count} trademarks")

            # ==================================================
            # 🔥 BẢN QUYỀN (COPYRIGHT)
            # ==================================================
            elif service_type == 'banquyen':
                print("\n©️ Processing COPYRIGHT formset...")

                copyright_formset = CopyrightFormSet(
                    request.POST,
                    request.FILES,
                    prefix='copyright'
                )

                print(f"   Management form - TOTAL_FORMS: {request.POST.get('copyright-TOTAL_FORMS')}")
                print(f"   Management form - INITIAL_FORMS: {request.POST.get('copyright-INITIAL_FORMS')}")

                if not copyright_formset.is_valid():
                    print("❌ Copyright formset invalid:")
                    print(f"   Errors: {copyright_formset.errors}")
                    print(f"   Non-form errors: {copyright_formset.non_form_errors()}")

                    contract.delete()

                    for idx, form_errors in enumerate(copyright_formset.errors):
                        if form_errors:
                            for field, errors in form_errors.items():
                                for error in errors:
                                    messages.error(request, f"Bản quyền #{idx + 1} - {field}: {error}")

                    for error in copyright_formset.non_form_errors():
                        messages.error(request, f"Lỗi formset: {error}")

                    return render(request, "add_contract.html", {
                        'contract_form': contract_form,
                        'trademark_formset': TrademarkFormSet(prefix='trademark',
                                                            queryset=TrademarkService.objects.none()),
                        'copyright_formset': copyright_formset,
                        'business_form': BusinessRegistrationForm(),
                        'investment_form': InvestmentForm(),
                        'other_form': OtherServiceForm(),
                    })

                print("✅ Copyright formset valid")

                # Count valid forms BEFORE saving
                valid_forms = [
                    form for form in copyright_formset
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                ]

                # 🔥 CHO PHÉP LƯU KHÔNG CẦN DỊCH VỤ
                if len(valid_forms) == 0:
                    print("⚠️ No copyright data provided, but contract saved")
                    messages.warning(request, "⚠️ Hợp đồng đã lưu nhưng chưa có thông tin bản quyền")
                else:
                    # Save valid forms
                    saved_count = 0
                    for idx, form in enumerate(valid_forms):
                        # 🔥 LƯU COPYRIGHT TRƯỚC
                        instance = form.save(commit=False)
                        instance.contract = contract
                        instance.save()
                        saved_count += 1

                        # 🔥 SAU ĐÓ MỚI XỬ LÝ FILE
                        files = request.FILES.getlist(f'copyright_files_{idx}')
                        print(f"   📎 Found {len(files)} files for copyright #{idx}")

                        for f in files:
                            Certificate.objects.create(
                                content_object=instance,
                                file=f,
                                name=f.name,
                            )
                            print(f"      ✅ Saved file: {f.name}")

                    print(f"✅ Saved {saved_count} copyrights")
            # ==================================================
            # OTHER SERVICES (DKKD, DAUTU, KHAC)
            # ==================================================
            elif service_type == 'dkkd':
                form = BusinessRegistrationForm(request.POST, request.FILES)
                if not form.is_valid():
                    contract.delete()
                    for field, errors in form.errors.items():
                        for error in errors:
                            field_label = form.fields.get(field).label if field in form.fields else field
                            messages.error(request, f"ĐKKD - {field_label}: {error}")

                    return render(request, "add_contract.html", {
                        'contract_form': contract_form,
                        'trademark_formset': TrademarkFormSet(prefix='trademark',
                                                            queryset=TrademarkService.objects.none()),
                        'copyright_formset': CopyrightFormSet(prefix='copyright',
                                                            queryset=CopyrightService.objects.none()),
                        'business_form': form,
                        'investment_form': InvestmentForm(),
                        'other_form': OtherServiceForm(),
                    })

                # 🔥 CHỈ LƯU NẾU CÓ DỮ LIỆU
                if any(form.cleaned_data.values()):
                    # 🔥 LƯU BUSINESS TRƯỚC
                    obj = form.save(commit=False)
                    obj.contract = contract
                    obj.save()
                    
                    # 🔥 SAU ĐÓ MỚI XỬ LÝ FILE
                    files = request.FILES.getlist('business_files')
                    print(f"   📎 Found {len(files)} files for business")
                    
                    for f in files:
                        Certificate.objects.create(
                            content_object=obj,
                            file=f,
                            name=f.name,
                        )
                        print(f"      ✅ Saved file: {f.name}")
                    
                    print("✅ Saved business registration")
                else:
                    print("⚠️ No business data provided")
                    messages.warning(request, "⚠️ Hợp đồng đã lưu nhưng chưa có thông tin ĐKKD")

            elif service_type == 'dautu':
                form = InvestmentForm(request.POST, request.FILES)
                if not form.is_valid():
                    contract.delete()
                    for field, errors in form.errors.items():
                        for error in errors:
                            field_label = form.fields.get(field).label if field in form.fields else field
                            messages.error(request, f"Đầu tư - {field_label}: {error}")

                    return render(request, "add_contract.html", {
                        'contract_form': contract_form,
                        'trademark_formset': TrademarkFormSet(prefix='trademark',
                                                            queryset=TrademarkService.objects.none()),
                        'copyright_formset': CopyrightFormSet(prefix='copyright',
                                                            queryset=CopyrightService.objects.none()),
                        'business_form': BusinessRegistrationForm(),
                        'investment_form': form,
                        'other_form': OtherServiceForm(),
                    })

                # 🔥 CHỈ LƯU NẾU CÓ DỮ LIỆU
                if any(form.cleaned_data.values()):
                    # 🔥 LƯU INVESTMENT TRƯỚC
                    obj = form.save(commit=False)
                    obj.contract = contract
                    obj.save()
                    
                    # 🔥 SAU ĐÓ MỚI XỬ LÝ FILE
                    files = request.FILES.getlist('investment_files')
                    print(f"   📎 Found {len(files)} files for investment")
                    
                    for f in files:
                        Certificate.objects.create(
                            content_object=obj,
                            file=f,
                            name=f.name,
                        )
                        print(f"      ✅ Saved file: {f.name}")

                    print("✅ Saved investment")
                else:
                    print("⚠️ No investment data provided")
                    messages.warning(request, "⚠️ Hợp đồng đã lưu nhưng chưa có thông tin đầu tư")

            else:  # khac
                form = OtherServiceForm(request.POST, request.FILES)
                if not form.is_valid():
                    contract.delete()
                    for field, errors in form.errors.items():
                        for error in errors:
                            field_label = form.fields.get(field).label if field in form.fields else field
                            messages.error(request, f"Dịch vụ khác - {field_label}: {error}")

                    return render(request, "add_contract.html", {
                        'contract_form': contract_form,
                        'trademark_formset': TrademarkFormSet(prefix='trademark',
                                                            queryset=TrademarkService.objects.none()),
                        'copyright_formset': CopyrightFormSet(prefix='copyright',
                                                            queryset=CopyrightService.objects.none()),
                        'business_form': BusinessRegistrationForm(),
                        'investment_form': InvestmentForm(),
                        'other_form': form,
                    })

                # 🔥 CHỈ LƯU NẾU CÓ DỮ LIỆU
                if any(form.cleaned_data.values()):
                    # 🔥 LƯU OTHER SERVICE TRƯỚC
                    obj = form.save(commit=False)
                    obj.contract = contract
                    obj.save()
                    
                    # 🔥 SAU ĐÓ MỚI XỬ LÝ FILE
                    files = request.FILES.getlist('other_files')
                    print(f"   📎 Found {len(files)} files for other service")
                    
                    for f in files:
                        Certificate.objects.create(
                            content_object=obj,
                            file=f,
                            name=f.name,
                        )
                        print(f"      ✅ Saved file: {f.name}")
                    
                    print("✅ Saved other service")
                else:
                    print("⚠️ No service data provided")
                    messages.warning(request, "⚠️ Hợp đồng đã lưu nhưng chưa có thông tin dịch vụ")

            # Thay thế phần xử lý PREPAID PAYMENT trong add_contract view

            # ===== HANDLE PREPAID PAYMENT =====
            if contract.payment_type == 'installment':
                # 🆕 TỰ ĐỘNG TẠO CÁC ĐỢT THANH TOÁN
                contract.create_installments()
                print(f"✅ Created {contract.number_of_installments} installments")
            else:
                # Trả dứt điểm - tự động hoàn thành
                contract.status = 'completed'
                contract.save(update_fields=['status'])

            # ===== UPDATE CUSTOMER STATUS =====
            customer = contract.customer
            customer.status = 'pending'
            customer.save()
            print(f"✅ Updated customer status: {customer.customer_code}")

            print("\n" + "=" * 60)
            print("✅ CONTRACT CREATED SUCCESSFULLY!")
            print("=" * 60 + "\n")

            messages.success(request, "✅ Tạo hợp đồng thành công!")
            return redirect('contract_detail', id=contract.id)

        except Exception as e:
            import traceback
            print("\n" + "=" * 60)
            print("❌ ERROR OCCURRED")
            print("=" * 60)
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print("=" * 60 + "\n")

            # Rollback
            if contract.id:
                contract.delete()

            messages.error(request, f"❌ Có lỗi xảy ra: {str(e)}")
            return redirect('add_contract')

    # ===== GET REQUEST =====
    print("\n📄 GET REQUEST - Rendering empty form")
    return render(request, "add_contract.html", {
        'contract_form': ContractForm(),
        'trademark_formset': TrademarkFormSet(prefix='trademark', queryset=TrademarkService.objects.none()),
        'copyright_formset': CopyrightFormSet(prefix='copyright', queryset=CopyrightService.objects.none()),
        'business_form': BusinessRegistrationForm(),
        'investment_form': InvestmentForm(),
        'other_form': OtherServiceForm(),
    })


def contract_delete(request, pk):
    print("🔥 DELETE VIEW CALLED:", pk)
    contract = get_object_or_404(Contract, pk=pk)
    contract.delete()
    return redirect('contract_list')



# ===============================================
# CUSTOMER DETAIL
# ===============================================
def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)
    contracts = customer.contracts.all()

    return render(request, 'customer_detail.html', {
        'customer': customer,
        'contracts': contracts
    })


# ===============================================
# CUSTOMER CHANGE STATUS
# (❗ KHÓA SỬA TAY KHI ĐÃ CÓ HỢP ĐỒNG)
# ===============================================
def customer_change_status(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerStatusForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Cập nhật trạng thái thành công!")
            return redirect('customer_detail', id=customer.id)
    else:
        form = CustomerStatusForm(instance=customer)

    return render(request, 'customer_change_status.html', {
        'customer': customer,
        'form': form
    })



# ===============================================
# CUSTOMER EDIT (ĐÃ SỬA - XỬ LÝ TRÙNG MÃ)
# ===============================================
def customer_edit(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Cập nhật khách hàng thành công!")
                return redirect('customer_detail', id=id)
            except IntegrityError as e:
                customer_code = form.cleaned_data.get('customer_code', '')
                messages.error(request, f"⚠️ Mã khách hàng '{customer_code}' đã tồn tại! Vui lòng nhập mã khác.")
            except Exception as e:
                messages.error(request, f"❌ Có lỗi xảy ra: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request,
                                f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customer_edit.html', {
        'form': form,
        'customer': customer
    })


# ===============================================
# CUSTOMER DELETE
# ===============================================
def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.delete()
        messages.success(request, "✅ Đã xóa khách hàng!")
        return redirect('home')

    return render(request, 'customer_delete_confirm.html', {
        'customer': customer
    })



# ===============================================
# CONTRACT LIST
# ===============================================
def contract_list(request):
    contracts = Contract.objects.select_related("customer").order_by("-created_at")
    return render(request, "contract_list.html", {"contracts": contracts})


# ===============================================
# CONTRACT DETAIL
# ===============================================
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import QuerySet


def contract_detail(request, id):
    contract = get_object_or_404(Contract, id=id)
    installments = contract.installments.all()

    # ✅ ĐếM SỐ ĐỢT ĐÃ TRẢ
    paid_count = installments.filter(is_paid=True).count()

    # Lấy dịch vụ
    service = None
    if contract.service_type == "nhanhieu":
        service = contract.trademarks.all()
    elif contract.service_type == "banquyen":
        service = contract.copyrights.all()
    elif contract.service_type == "dkkd":
        service = BusinessRegistrationService.objects.filter(contract=contract)
    elif contract.service_type == "dautu":
        service = InvestmentService.objects.filter(contract=contract)
    else:
        service = OtherService.objects.filter(contract=contract)

    # Auto hoàn thành nếu trả dứt
    if contract.payment_type == "full" and contract.status != "completed":
        contract.status = "completed"
        contract.save(update_fields=["status"])

    # 🆕 XỬ LÝ THANH TOÁN ĐƠN GIẢN
    if request.method == "POST":
        action = request.POST.get("action")

        # 1️⃣ ĐÁNH DẤU ĐÃ XUẤT HÓA ĐƠN
        if action == "log_toggle_bill":
            log_id = request.POST.get("log_id")
            log_entry = get_object_or_404(PaymentLog, id=log_id)

            if not log_entry.is_exported_bill:
                log_entry.is_exported_bill = True
                log_entry.bill_exported_at = timezone.now()
                log_entry.save()
                messages.success(request, f"✅ Đã đánh dấu xuất hóa đơn")
            return redirect("contract_detail", id=contract.id)

        # 2️⃣ THANH TOÁN ĐỢT (CHỈ CẦN 1 CLICK)
        elif action == "pay_installment":
            installment_id = request.POST.get("installment_id")

            try:
                ins = contract.installments.get(id=installment_id)

                if ins.is_paid:
                    messages.warning(request, "⚠️ Đợt này đã được thanh toán rồi")
                    return redirect("contract_detail", id=contract.id)

                # Tính số tiền còn phải trả
                remaining = ins.amount - ins.paid_amount

                # Cập nhật thanh toán
                ins.paid_amount = ins.amount
                ins.is_paid = True
                ins.paid_date = timezone.now().date()
                ins.save()

                # Ghi log
                PaymentLog.objects.create(
                    contract=contract,
                    installment=ins,
                    amount_paid=remaining,
                    paid_at=timezone.now()
                )

                # Cập nhật status contract nếu đã trả hết
                if contract.remaining_amount <= 0:
                    contract.status = "completed"
                    contract.save(update_fields=["status"])

                messages.success(request, f"✅ Đã thanh toán đợt {ins.notes} - Số tiền: {remaining:,.0f} VNĐ")
                return redirect("contract_detail", id=contract.id)

            except PaymentInstallment.DoesNotExist:
                messages.error(request, "❌ Không tìm thấy đợt thanh toán")
                return redirect("contract_detail", id=contract.id)
            except Exception as e:
                messages.error(request, f"❌ Có lỗi xảy ra: {str(e)}")
                return redirect("contract_detail", id=contract.id)

        # 3️⃣ THANH TOÁN TỪNG PHẦN (NẾU CẦN)
        elif action == "partial_payment":
            installment_id = request.POST.get("installment_id")
            paid_amount_raw = request.POST.get("paid_amount")

            if not paid_amount_raw:
                messages.error(request, "❌ Vui lòng nhập số tiền thanh toán")
                return redirect("contract_detail", id=contract.id)

            try:
                paid_amount = Decimal(paid_amount_raw)
                ins = contract.installments.get(id=installment_id)

                # Cập nhật số tiền
                ins.paid_amount += paid_amount

                # Kiểm tra xem đã đủ chưa
                if ins.paid_amount >= ins.amount:
                    ins.is_paid = True
                    ins.paid_date = timezone.now().date()

                ins.save()

                # Ghi log
                PaymentLog.objects.create(
                    contract=contract,
                    installment=ins,
                    amount_paid=paid_amount,
                    paid_at=timezone.now()
                )

                # Cập nhật status
                if contract.remaining_amount <= 0:
                    contract.status = "completed"
                    contract.save(update_fields=["status"])

                messages.success(request, f"✅ Đã ghi nhận thanh toán: {paid_amount:,.0f} VNĐ")
                return redirect("contract_detail", id=contract.id)

            except Exception as e:
                messages.error(request, f"❌ Có lỗi xảy ra: {str(e)}")
                return redirect("contract_detail", id=contract.id)
        
        # 4️⃣ XUẤT HÓA ĐƠN
        if action == 'export_bill':
            installment_id = request.POST.get('installment_id')
            print(f"DEBUG: installment_id = {installment_id}")
            
            try:
                installment = PaymentInstallment.objects.get(id=installment_id)
                print(f"DEBUG: TRƯỚC KHI LƯU - is_exported_bill = {installment.is_exported_bill}")
                
                if installment.is_paid:
                    installment.is_exported_bill = True
                    installment.bill_exported_at = timezone.now()
                    installment.save()
                    
                    # Kiểm tra lại
                    installment.refresh_from_db()
                    print(f"DEBUG: SAU KHI LƯU - is_exported_bill = {installment.is_exported_bill}")
                    print(f"DEBUG: bill_exported_at = {installment.bill_exported_at}")
                    
                    messages.success(request, f'✅ Đã xuất hóa đơn đỏ!')
                else:
                    messages.error(request, '⚠️ Đợt này chưa thanh toán!')
                    print(f"DEBUG: is_paid = {installment.is_paid}")
                    
            except PaymentInstallment.DoesNotExist:
                messages.error(request, '❌ Không tìm thấy đợt thanh toán!')
            
            return redirect('contract_detail', id=id)

    return render(request, "contract_detail.html", {
        "contract": contract,
        "service": service,
        "installments": installments,
        "paid_count": paid_count,
    })




from .forms import InstallmentFormSet


@login_required
def edit_installment_amounts(request, contract_id):
    """View để nhập số tiền cho từng đợt thanh toán"""
    contract = get_object_or_404(Contract, id=contract_id)

    if contract.payment_type != 'installment':
        messages.error(request, "❌ Hợp đồng này không phải trả góp")
        return redirect('contract_detail', id=contract_id)

    installments = contract.installments.all().order_by('due_date')

    if request.method == 'POST':
        formset = InstallmentFormSet(request.POST, queryset=installments)

        if formset.is_valid():
            # Tính tổng số tiền đã nhập
            total_entered = 0
            for form in formset:
                if form.cleaned_data:  # ✅ Kiểm tra cleaned_data tồn tại
                    amount = form.cleaned_data.get('amount', 0)
                    if amount:
                        total_entered += amount

            # Kiểm tra tổng có khớp với giá trị hợp đồng không
            if total_entered != contract.contract_value:
                messages.warning(
                    request,
                    f"⚠️ Tổng số tiền các đợt ({total_entered:,.0f} VNĐ) "
                    f"khác với giá trị hợp đồng ({contract.contract_value:,.0f} VNĐ)"
                )

            # Lưu các đợt
            instances = formset.save(commit=False)
            for instance in instances:
                # ✅ Không cần kiểm tra paid_amount ở đây
                instance.save()

            messages.success(request, "✅ Đã cập nhật số tiền các đợt thanh toán!")
            return redirect('contract_detail', id=contract_id)
        else:
            # ✅ Hiển thị lỗi đúng cách
            messages.error(request, "❌ Có lỗi trong form, vui lòng kiểm tra lại")
            # In ra console để debug
            print("Formset errors:", formset.errors)
            print("Non-form errors:", formset.non_form_errors())
    else:
        formset = InstallmentFormSet(queryset=installments)

    # Tính tổng hiện tại
    current_total = sum(ins.amount for ins in installments)

    return render(request, 'edit_installment_amounts.html', {
        'contract': contract,
        'formset': formset,
        'installments': installments,
        'current_total': current_total,
    })

# ===============================================
# CONTRACT EDIT (ĐÃ SỬA - CẬP NHẬT TRẠNG THÁI)
# ===============================================
@login_required
def contract_edit(request, id):
    # ==========================
    # 1. LẤY HỢP ĐỒNG
    # ==========================
    contract = get_object_or_404(Contract, id=id)

    contract_form = None
    service_form = None
    service_formset = None

    # ==========================
    # 2. XÁC ĐỊNH LOẠI DỊCH VỤ
    # ==========================
    FormSetClass = None     # Dùng cho nhanhieu / banquyen
    ServiceForm = None      # Dùng cho dkkd / dautu / khac
    queryset = None
    prefix = None
    service = None

    if contract.service_type == "nhanhieu":
        FormSetClass = TrademarkFormSet
        queryset = TrademarkService.objects.filter(contract=contract)
        prefix = "trademark"

    elif contract.service_type == "banquyen":
        FormSetClass = CopyrightFormSet
        queryset = CopyrightService.objects.filter(contract=contract)
        prefix = "copyright"

    elif contract.service_type == "dkkd":
        ServiceForm = BusinessRegistrationForm
        service = BusinessRegistrationService.objects.filter(contract=contract).first()

    elif contract.service_type == "dautu":
        ServiceForm = InvestmentForm
        service = InvestmentService.objects.filter(contract=contract).first()

    else:  # 🔥 khac
        ServiceForm = OtherServiceForm
        service = OtherService.objects.filter(contract=contract).first()

    # ==========================
    # 3. POST – LƯU DỮ LIỆU
    # ==========================
    if request.method == "POST":
        # 🔒 KHÓA TRƯỜNG HỢP ĐỒNG
        contract_form = ContractForm(request.POST, instance=contract)
        lock_contract_fields(contract_form)

        # ===== 3.1 FORMSET (NHÃN HIỆU / BẢN QUYỀN) =====
        if FormSetClass:
            service_formset = FormSetClass(
                request.POST,
                request.FILES,
                queryset=queryset,
                prefix=prefix
            )

            if contract_form.is_valid() and service_formset.is_valid():
                # Lưu hợp đồng (chỉ những field cho phép)
                contract_form.save()

                # Lưu / update service
                instances = service_formset.save(commit=False)
                for obj in instances:
                    obj.contract = contract
                    obj.save()

                # Xóa service bị đánh dấu DELETE
                for obj in service_formset.deleted_objects:
                    obj.delete()

                messages.success(request, "✅ Cập nhật hợp đồng thành công!")
                return redirect("contract_detail", id=contract.id)

        # ===== 3.2 SERVICE ĐƠN (DKKD / ĐẦU TƯ / KHÁC) =====
        else:
            service_form = ServiceForm(
                request.POST,
                request.FILES,
                instance=service   # 🔥 có thì update, không có thì tạo
            )

            if contract_form.is_valid() and service_form.is_valid():
                contract_form.save()

                obj = service_form.save(commit=False)
                obj.contract = contract   # 🔥 đảm bảo gắn contract
                obj.save()

                messages.success(request, "✅ Cập nhật hợp đồng thành công!")
                return redirect("contract_detail", id=contract.id)

    # ==========================
    # 4. GET – HIỂN THỊ FORM
    # ==========================
    else:
        contract_form = ContractForm(instance=contract)
        lock_contract_fields(contract_form)

        if FormSetClass:
            service_formset = FormSetClass(
                queryset=queryset,
                prefix=prefix
            )
        else:
            service_form = ServiceForm(instance=service)

    # ==========================
    # 5. RENDER
    # ==========================
    return render(request, "contract_edit.html", {
        "contract": contract,
        "contract_form": contract_form,
        "service_formset": service_formset,
        "service_form": service_form,
    })



# ===============================================
# DOWNLOAD CERTIFICATE
# ===============================================
def download_certificate(request, id):
    contract = get_object_or_404(Contract, id=id)

    if contract.service_type == "nhanhieu":
        service = contract.trademarks.first()
        if not service or not service.certificate_file:
            raise Http404("Không có giấy chứng nhận")

    elif contract.service_type == "banquyen":
        service = CopyrightService.objects.get(contract=contract)
    elif contract.service_type == "dkkd":
        service = BusinessRegistrationService.objects.get(contract=contract)
    elif contract.service_type == "dautu":
        service = InvestmentService.objects.get(contract=contract)
    else:
        service = OtherService.objects.get(contract=contract)

    if not service.certificate_file:
        raise Http404("Không có giấy chứng nhận")

    return FileResponse(
        service.certificate_file.open("rb"),
        as_attachment=True,
        filename=os.path.basename(service.certificate_file.name)
    )
    
def register_certificate(request, business_id):
    business = get_object_or_404(
        BusinessRegistrationService,
        id=business_id
    )
    file_field = business.registration_certificate

    if not file_field:
        raise Http404("Chưa có file đăng ký kinh doanh")

    file_path = file_field.path

    if not os.path.exists(file_path):
        raise Http404("File không tồn tại")

    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(file_path)
    )
    
# ===============================================
# CUSTOMER CREATE
# ===============================================
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Thêm khách hàng thành công!")
                return redirect('home')
            except IntegrityError:
                messages.error(request, "⚠️ Mã khách hàng đã tồn tại!")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomerForm()

    return render(request, 'add_customer.html', {'form': form})


from django.http import JsonResponse
from django.db.models import Q

from django.http import JsonResponse
from django.db.models import Q


def search_customer(request):
    """
    API tìm kiếm khách hàng theo mã hoặc tên
    URL: /api/search-customer/?q=ma123
    """
    query = request.GET.get('q', '').strip()

    # Yêu cầu ít nhất 1 ký tự để test
    if len(query) < 1:
        return JsonResponse([], safe=False)

    try:
        # Tìm kiếm theo customer_code hoặc name
        customers = Customer.objects.filter(
            Q(customer_code__icontains=query) |
            Q(name__icontains=query)
        )[:10]

        # Tạo danh sách kết quả
        results = []
        for c in customers:
            results.append({
                'id': c.id,
                'code': c.customer_code,
                'name': c.name,
                'phone': str(c.phone) if c.phone else '',
                'email': c.email if c.email else ''
            })

        return JsonResponse(results, safe=False)

    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print(traceback.format_exc())

        return JsonResponse({
            'error': str(e)
        }, status=500)
# ===============================================
# LOGIN / LOGOUT
# ===============================================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
# ===============================================
# REQUIRE LOGIN FOR ALL VIEWS
# ===============================================
def protect_views(*views):
    for view in views:
        globals()[view.__name__] = login_required(view)


protect_views(
    home,
    add_contract,
    customer_detail,
    customer_change_status,
    customer_edit,
    customer_delete,
    contract_list,
    contract_detail,
    contract_edit,
    download_certificate,
    add_customer,
    search_customer,
  
)

# ===============================================
# CONTRACT SEARCH (NHÃN HIỆU)
# ===============================================
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Contract, TrademarkService


def contract_search(request):
    q = request.GET.get('q', '').strip()

    # Mặc định lấy tất cả hợp đồng nhãn hiệu
    contracts = Contract.objects.filter(service_type='nhanhieu').order_by('-created_at')
    trademarks = []  # 🔥 THÊM BIẾN ĐỂ LƯU DANH SÁCH NHÃN HIỆU

    if q:
        # 🔥 TÌM TẤT CẢ NHÃN HIỆU CÓ CHỨA SỐ ĐƠN
        trademarks = TrademarkService.objects.filter(
            app_no__icontains=q
        ).select_related('contract', 'contract__customer')

        # Nếu tìm thấy nhãn hiệu, lọc các hợp đồng liên quan
        if trademarks.exists():
            contract_ids = trademarks.values_list('contract_id', flat=True)
            contracts = Contract.objects.filter(
                id__in=contract_ids
            ).order_by('-created_at')
        else:
            # Nếu không tìm thấy theo số đơn, tìm theo thông tin hợp đồng
            contracts = contracts.filter(
                Q(contract_no__icontains=q) |
                Q(customer__customer_code__icontains=q) |
                Q(customer__name__icontains=q)
            ).distinct()

    context = {
        'contracts': contracts,
        'trademarks': trademarks,  # 🔥 TRUYỀN DANH SÁCH NHÃN HIỆU VÀO TEMPLATE
        'q': q,
    }
    return render(request, 'contract_search.html', context)

# ===============================================
# Bản quyền tác giả
# ===============================================
def contract_copyright_search(request):
    q = request.GET.get('q', '').strip()

    # Mặc định lấy tất cả hợp đồng bản quyền
    contracts = Contract.objects.filter(service_type='banquyen').order_by('-created_at')
    copyrights = []  # 🔥 THÊM BIẾN ĐỂ LƯU DANH SÁCH BẢN QUYỀN

    if q:
        # 🔥 TÌM TẤT CẢ BẢN QUYỀN CÓ CHỨA SỐ GIẤY CHỨNG NHẬN
        copyrights = CopyrightService.objects.filter(
            certificate_no__icontains=q
        ).select_related('contract', 'contract__customer')

        # Nếu tìm thấy bản quyền, lọc các hợp đồng liên quan
        if copyrights.exists():
            contract_ids = copyrights.values_list('contract_id', flat=True)
            contracts = Contract.objects.filter(
                id__in=contract_ids
            ).order_by('-created_at')
        else:
            # Nếu không tìm thấy theo số chứng nhận, tìm theo thông tin hợp đồng
            contracts = contracts.filter(
                Q(contract_no__icontains=q) |
                Q(customer__customer_code__icontains=q) |
                Q(customer__name__icontains=q)
            ).distinct()

    return render(request, 'contract_copyright_search.html', {
        'contracts': contracts,
        'copyrights': copyrights,  # 🔥 TRUYỀN DANH SÁCH BẢN QUYỀN VÀO TEMPLATE
        'q': q
    })
# ===============================================
# dkkq search
# ===============================================

def contract_business_search(request):
    q = request.GET.get('q', '').strip()
    contracts = Contract.objects.filter(service_type='dkkd')

    if q:
        # Kiểm tra xem có phải mã số thuế không
        business = BusinessRegistrationService.objects.filter(tax_code__icontains=q).first()

        if business:
            # Nếu tìm thấy, chuyển đến trang chi tiết
            return redirect('business_detail', business_id=business.id)

        # Nếu không phải mã số thuế, tìm kiếm hợp đồng bình thường
        contracts = contracts.filter(
            Q(contract_no__icontains=q) |
            Q(customer__customer_code__icontains=q) |
            Q(customer__name__icontains=q)
        )

    contracts = contracts.order_by('-created_at')

    return render(request, 'contract_business_search.html', {
        'contracts': contracts,
        'q': q
    })
# ===============================================
# ĐK đầu tư
# ===============================================
def contract_investment_search(request):
    q = request.GET.get('q', '').strip()
    contracts = Contract.objects.filter(service_type='dautu')

    if q:
        # Kiểm tra xem có phải mã dự án không
        investment = InvestmentService.objects.filter(project_code__icontains=q).first()

        if investment:
            # Nếu tìm thấy, chuyển đến trang chi tiết
            return redirect('investment_detail', investment_id=investment.id)

        # Nếu không phải mã dự án, tìm kiếm hợp đồng bình thường
        contracts = contracts.filter(
            Q(contract_no__icontains=q) |
            Q(customer__customer_code__icontains=q) |
            Q(customer__name__icontains=q)
        )

    contracts = contracts.order_by('-created_at')

    return render(request, 'contract_investment_search.html', {
        'contracts': contracts,
        'q': q
    })

# ===============================================
# Dịch Vụ Khác
# ===============================================
def contract_other_service_search(request):
    q = request.GET.get('q', '').strip()

    contracts = Contract.objects.filter(
        service_type='khac'   # ✅ DỊCH VỤ KHÁC
    )

    if q:
        contracts = contracts.filter(
            Q(contract_no__icontains=q) |
            Q(customer__customer_code__icontains=q) |
            Q(customer__name__icontains=q)
        )

    contracts = contracts.order_by('-created_at')

    return render(request, 'contract_other_service_search.html', {
        'contracts': contracts,
        'q': q
    })






def trademark_search(request):
    q = request.GET.get('q', '').strip()

    if q:
        trademark = TrademarkService.objects.filter(app_no__icontains=q).first()

        if trademark:
            return redirect('trademark_detail', trademark_id=trademark.id)
        else:
            return render(request, 'trademark_search.html', {
                'q': q,
                'not_found': True
            })

    return render(request, 'trademark_search.html', {'q': q})


def trademark_detail(request, trademark_id):
    trademark = get_object_or_404(TrademarkService, id=trademark_id)
    contract = trademark.contract

    context = {
        'trademark': trademark,
        'contract': contract,
    }
    return render(request, 'trademark_detail.html', context)




# ===============================================
# COPYRIGHT SEARCH & DETAIL
# ===============================================
def copyright_search(request):
    q = request.GET.get('q', '').strip()

    if q:
        # Tìm bản quyền theo số giấy chứng nhận
        copyright = CopyrightService.objects.filter(certificate_no__icontains=q).first()

        if copyright:
            # Nếu tìm thấy, chuyển đến trang chi tiết
            return redirect('copyright_detail', copyright_id=copyright.id)
        else:
            # Nếu không tìm thấy, hiển thị thông báo
            return render(request, 'copyright_search.html', {
                'q': q,
                'not_found': True
            })

    return render(request, 'copyright_search.html', {'q': q})


def copyright_detail(request, copyright_id):
    copyright = get_object_or_404(CopyrightService, id=copyright_id)
    contract = copyright.contract

    context = {
        'copyright': copyright,
        'contract': contract,
    }
    return render(request, 'copyright_detail.html', context)


# ===============================================
# BUSINESS REGISTRATION SEARCH & DETAIL
# ===============================================
def business_search(request):
    q = request.GET.get('q', '').strip()

    if q:
        # Tìm đăng ký kinh doanh theo mã số thuế
        business = BusinessRegistrationService.objects.filter(tax_code__icontains=q).first()

        if business:
            # Nếu tìm thấy, chuyển đến trang chi tiết
            return redirect('business_detail', business_id=business.id)
        else:
            # Nếu không tìm thấy, hiển thị thông báo
            return render(request, 'business_search.html', {
                'q': q,
                'not_found': True
            })

    return render(request, 'business_search.html', {'q': q})


def business_detail(request, business_id):
    business = get_object_or_404(BusinessRegistrationService, id=business_id)
    contract = business.contract

    context = {
        'business': business,
        'contract': contract,
    }
    return render(request, 'business_detail.html', context)

# ===============================================
# INVESTMENT SEARCH & DETAIL
# ===============================================
def investment_search(request):
    q = request.GET.get('q', '').strip()

    if q:
        # Tìm dự án đầu tư theo mã dự án
        investment = InvestmentService.objects.filter(project_code__icontains=q).first()

        if investment:
            # Nếu tìm thấy, chuyển đến trang chi tiết
            return redirect('investment_detail', investment_id=investment.id)
        else:
            # Nếu không tìm thấy, hiển thị thông báo
            return render(request, 'investment_search.html', {
                'q': q,
                'not_found': True
            })

    return render(request, 'investment_search.html', {'q': q})


def investment_detail(request, investment_id):
    investment = get_object_or_404(InvestmentService, id=investment_id)
    contract = investment.contract

    context = {
        'investment': investment,
        'contract': contract,
    }
    return render(request, 'investment_detail.html', context)


# Thêm vào cuối file views.py
# FILE ĐÍNH KÈM
def delete_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)

    # xóa file vật lý
    if cert.file:
        cert.file.delete(save=False)

    contract_id = cert.content_object.contract.id  # quay về đúng hợp đồng
    cert.delete()

    return redirect("contract_detail", contract_id)
def upload_certificate(request):
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        service_id = request.POST.get('service_id')

        file = request.FILES.get('file')
        name = request.POST.get('name')

        if not file:
            messages.error(request, 'Chưa chọn file')
            return redirect(request.META.get('HTTP_REFERER'))

        # lấy đúng service
        MODEL_MAP = {
            'nhanhieu': TrademarkService,
            'banquyen': CopyrightService,
            'dkkd': BusinessRegistrationService,
            'dautu': InvestmentService,
            'khac': OtherService,
        }

        model = MODEL_MAP.get(service_type)
        service = get_object_or_404(model, id=service_id)

        Certificate.objects.create(
            content_object=service,   # nếu dùng GenericForeignKey
            name=name,
            file=file
        )

        messages.success(request, 'Đã thêm tài liệu')
        return redirect(request.META.get('HTTP_REFERER'))


#ho so
from .models import UserProfile

@login_required
def profile_view(request):
    # Tự động tạo profile nếu chưa có
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Cập nhật hồ sơ thành công!')
            return redirect('profile')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'profile.html', {
        'form': form,
        'profile': profile,
    })