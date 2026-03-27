console.log('🚀 Script started loading...');

// ✅ Biến toàn cục - CHỈ KHAI BÁO 1 LẦN
let formChanged = false;
let formSubmitting = false;
let pendingUrl = null;

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       SERVICE TYPE TOGGLE (FIXED - DISABLE HIDDEN FORMS)
    ===================================================== */
    const serviceTypeSelect = document.getElementById("id_service_type");

    const serviceBlocks = {
        nhanhieu: document.getElementById("nhanhieu_form"),
        banquyen: document.getElementById("banquyen_form"),
        dkkd: document.getElementById("dkkd_form"),
        dautu: document.getElementById("dautu_form"),
        khac: document.getElementById("khac_form"),
    };

    function hideAllServices() {
        Object.values(serviceBlocks).forEach(block => {
            if (!block) return;

            block.style.display = "none";

            // 🔥 FIX: DISABLE tất cả input trong form bị ẩn
            block.querySelectorAll("input, select, textarea").forEach(input => {
                // Bỏ qua các input hidden của formset management
                if (input.type === "hidden" &&
                    (input.name.includes("TOTAL_FORMS") ||
                     input.name.includes("INITIAL_FORMS") ||
                     input.name.includes("MAX_NUM_FORMS"))) {
                    return;
                }

                // Lưu trạng thái required cũ
                if (input.hasAttribute("required")) {
                    input.dataset.wasRequired = "true";
                    input.removeAttribute("required");
                }

                // 🔥 DISABLE input để không submit
                input.disabled = true;
            });
        });
    }

    function showService(type) {
        hideAllServices();

        const block = serviceBlocks[type];
        if (!block) return;

        block.style.display = "block";

        // 🔥 FIX: ENABLE lại tất cả input trong form được hiện
        block.querySelectorAll("input, select, textarea").forEach(input => {
            // Bỏ qua các input hidden của formset management
            if (input.type === "hidden" &&
                (input.name.includes("TOTAL_FORMS") ||
                 input.name.includes("INITIAL_FORMS") ||
                 input.name.includes("MAX_NUM_FORMS"))) {
                return;
            }

            // Khôi phục required
            if (input.dataset.wasRequired === "true") {
                input.setAttribute("required", "required");
                delete input.dataset.wasRequired;
            }

            // 🔥 ENABLE input
            input.disabled = false;
        });
    }

    if (serviceTypeSelect) {
        // Khởi tạo: hiện form tương ứng với giá trị đã chọn
        showService(serviceTypeSelect.value || "nhanhieu");

        serviceTypeSelect.addEventListener("change", function () {
            showService(this.value);
        });
    }

    /* =====================================================
       PAYMENT TYPE – INSTALLMENT TOGGLE
    ===================================================== */
    const paymentType = document.getElementById("id_payment_type");
    const installmentField = document.getElementById("id_installment_count");

    if (paymentType && installmentField) {
        const wrapper = installmentField.closest("p");

        function toggleInstallment() {
            if (paymentType.value === "installment") {
                wrapper.style.display = "block";
                installmentField.setAttribute("required", "required");
            } else {
                wrapper.style.display = "none";
                installmentField.value = "";
                installmentField.removeAttribute("required");
            }
        }

        toggleInstallment();
        paymentType.addEventListener("change", toggleInstallment);
    }

    /* =====================================================
       CUSTOMER SEARCH (AJAX)
    ===================================================== */
    const searchInput = document.getElementById("customer_search");
    const searchResults = document.getElementById("search_results");
    const selectedCustomer = document.getElementById("selected_customer");
    const customerField = document.getElementById("id_customer");

    let searchTimeout;

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const query = this.value.trim();
            console.log("🔍 Search query:", query); // ✅ Debug

            clearTimeout(searchTimeout);

            if (query.length < 2) {
                console.log("❌ Query too short"); // ✅ Debug
                searchResults.style.display = "none";
                return;
            }

            searchTimeout = setTimeout(() => {
                console.log("📡 Fetching..."); // ✅ Debug

                fetch(`/api/search-customer/?q=${encodeURIComponent(query)}`)
                    .then(res => {
                        console.log("📥 Response:", res); // ✅ Debug
                        return res.json();
                    })
                    .then(data => {
                        console.log("📊 Data received:", data); // ✅ Debug
                        renderSearchResults(data);
                    })
                    .catch((error) => {
                        console.error("❌ Search error:", error);
                        searchResults.innerHTML =
                            "<div class='error'>❌ Lỗi tìm kiếm</div>";
                        searchResults.style.display = "block";
                    });
            }, 300);
        });

        // Ẩn kết quả khi click bên ngoài
        document.addEventListener("click", function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = "none";
            }
        });
    }

    function renderSearchResults(customers) {
        console.log("🎨 Rendering results:", customers); // ✅ Debug

        if (!customers.length) {
            searchResults.innerHTML =
                "<div class='no-results'>Không tìm thấy khách hàng</div>";
            searchResults.style.display = "block";
            return;
        }

        searchResults.innerHTML = customers.map(c => `
            <div class="search-result-item"
                 data-id="${c.id}"
                 data-code="${c.code}"
                 data-name="${c.name}">
                <strong>${c.code}</strong> – ${c.name}
            </div>
        `).join("");

        searchResults.style.display = "block";

        document.querySelectorAll(".search-result-item").forEach(item => {
            item.addEventListener("click", function () {
                selectCustomer(this.dataset.id, this.dataset.code, this.dataset.name);
            });
        });
    }

    function selectCustomer(id, code, name) {
        selectedCustomer.innerHTML = `
            <div class="selected-customer-card">
                <strong>${code}</strong> – ${name}
                <button type="button" class="btn-remove-customer">❌</button>
            </div>
        `;
        selectedCustomer.style.display = "block";
        customerField.value = id;
        searchResults.style.display = "none";
        searchInput.value = "";

        selectedCustomer
            .querySelector(".btn-remove-customer")
            .addEventListener("click", removeCustomer);
    }

    function removeCustomer() {
        selectedCustomer.innerHTML = "";
        selectedCustomer.style.display = "none";
        customerField.value = "";
    }

    /* =====================================================
       FORM VALIDATION BEFORE SUBMIT
    ===================================================== */
    const contractForm = document.querySelector(".contract-form");

    if (contractForm) {
        contractForm.addEventListener("submit", function (e) {
            console.log("\n🔍 Form validation started...");

            // Kiểm tra khách hàng
            if (!customerField || !customerField.value) {
                e.preventDefault();
                alert("⚠️ Vui lòng chọn khách hàng!");
                console.error("❌ Validation failed: No customer selected");
                return false;
            }
            console.log("✅ Customer selected:", customerField.value);

            // Kiểm tra loại dịch vụ
            if (serviceTypeSelect && !serviceTypeSelect.value) {
                e.preventDefault();
                alert("⚠️ Vui lòng chọn loại dịch vụ!");
                console.error("❌ Validation failed: No service type selected");
                return false;
            }
            console.log("✅ Service type:", serviceTypeSelect.value);

            // 🔥 DEBUG: Log form data trước khi submit
            const formData = new FormData(contractForm);
            console.log("\n📋 Form data being submitted:");
            console.log("=".repeat(50));

            let hasServiceData = false;
            for (let [key, value] of formData.entries()) {
                // Log tất cả các field của service đang được chọn
                if (key.includes('company_name') || key.includes('business_type') ||
                    key.includes('address') || key.includes('email') ||
                    key.includes('phone') || key.includes('legal_representative') ||
                    key.includes('position') || key.includes('charter_capital') ||
                    key.includes('tax_code') || key.includes('project_code') ||
                    key.includes('investor') || key.includes('project_name') ||
                    key.includes('objective') || key.includes('total_capital') ||
                    key.includes('description')) {
                    console.log(`  ${key}: ${value || '(empty)'}`);
                    if (value) hasServiceData = true;
                }
            }
            console.log("=".repeat(50));

            if (!hasServiceData && serviceTypeSelect.value !== 'nhanhieu' && serviceTypeSelect.value !== 'banquyen') {
                console.warn("⚠️ Warning: No service data found!");
            } else {
                console.log("✅ Service data found");
            }

            console.log("✅ Form validation passed – submitting...\n");

            // ✅ Đánh dấu form đang submit
            formSubmitting = true;
            return true;
        });

        // ✅ Theo dõi thay đổi form
        contractForm.addEventListener('input', function(e) {
            formChanged = true;
            console.log('📝 Form changed (input):', e.target.name);
        });

        contractForm.addEventListener('change', function(e) {
            formChanged = true;
            console.log('📝 Form changed (change):', e.target.name);
        });
    }

    /* =====================================================
       MODAL CONFIRMATION (XỬ LÝ RỜI TRANG)
    ===================================================== */
    const cancelBtn = document.getElementById('cancelBtn');
    const stayBtn = document.getElementById('stayBtn');
    const leaveBtn = document.getElementById('leaveBtn');
    const modal = document.getElementById('confirmModal');

    console.log('🔍 Modal elements found:', {
        cancelBtn: !!cancelBtn,
        stayBtn: !!stayBtn,
        leaveBtn: !!leaveBtn,
        modal: !!modal
    });

    // Xử lý nút Hủy
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🔴 Cancel button clicked');
            showConfirmModal(this.getAttribute('data-home-url') || '/');
        });
    }

    // Xử lý nút "Không, ở lại"
    if (stayBtn) {
        stayBtn.addEventListener('click', function() {
            console.log('🟢 Stay button clicked');
            closeConfirmModal();
        });
    }

    // Xử lý nút "Có, rời trang"
    if (leaveBtn) {
        leaveBtn.addEventListener('click', function() {
            console.log('🔴 Leave button clicked');
            confirmLeave();
        });
    }

    // Đóng modal khi click overlay
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target.id === 'confirmModal') {
                console.log('🖱️ Clicked overlay');
                closeConfirmModal();
            }
        });
    }

    // Đóng modal khi nhấn ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            console.log('⌨️ ESC pressed');
            closeConfirmModal();
        }
    });

    // Cảnh báo khi rời trang (Back/Refresh/Close)
    window.addEventListener('beforeunload', function(e) {
        if (formChanged && !formSubmitting) {
            console.log('⚠️ beforeunload triggered');
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });

    // Xử lý tất cả links
    const links = document.querySelectorAll('a:not(#cancelBtn)');
    console.log('🔗 Found', links.length, 'links to monitor');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href !== '#' && !href.startsWith('javascript:')) {
                if (formChanged && !formSubmitting) {
                    e.preventDefault();
                    console.log('🔗 Link clicked, showing modal');
                    showConfirmModal(href);
                }
            }
        });
    });

    console.log('✅ All event listeners attached');
});

/* =====================================================
   FORMSET ADD (NHÃN HIỆU & BẢN QUYỀN)
===================================================== */
window.addForm = function (prefix) {
    console.log(`➕ Adding new ${prefix} form...`);

    const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    const formset = document.getElementById(`${prefix}-formset`);
    const emptyForm = document.getElementById(`${prefix}-empty-form`);

    if (!totalForms || !formset || !emptyForm) {
        console.error(`❌ Cannot find formset elements for ${prefix}`);
        return;
    }

    const index = parseInt(totalForms.value, 10);
    const template = emptyForm.querySelector(".formset-item");

    if (!template) {
        console.error(`❌ Cannot find template for ${prefix}`);
        return;
    }

    const newForm = template.cloneNode(true);

    // Replace __prefix__ with actual index
    newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, index);

    // Clear all input values (except hidden)
    newForm.querySelectorAll("input, select, textarea").forEach(field => {
        if (field.type !== "hidden") {
            field.value = "";
        }
    });

    // Append to formset
    formset.appendChild(newForm);

    // Update total forms count
    totalForms.value = index + 1;

    console.log(`✅ Added ${prefix} form #${index}`);
};

/* =====================================================
   FORMSET REMOVE (NHÃN HIỆU & BẢN QUYỀN)
===================================================== */
window.removeItem = function (btn) {
    const item = btn.closest(".formset-item");
    if (!item) {
        console.error("❌ Cannot find formset item to remove");
        return;
    }

    const delInput = item.querySelector('input[name$="DELETE"]');

    if (delInput) {
        // Mark for deletion (for existing records)
        delInput.checked = true;
        item.style.display = "none";
        console.log("✅ Marked item for deletion");
    } else {
        // Remove completely (for new records not yet saved)
        item.remove();
        console.log("✅ Removed item from DOM");
    }
};

/* =====================================================
   MODAL FUNCTIONS
===================================================== */
// Hàm hiển thị modal
function showConfirmModal(url) {
    console.log('📢 showConfirmModal called with URL:', url);
    console.log('📊 formChanged:', formChanged, '| formSubmitting:', formSubmitting);

    if (!formChanged || formSubmitting) {
        console.log('✅ No changes, redirecting directly...');
        window.location.href = url;
        return;
    }

    pendingUrl = url;
    const modal = document.getElementById('confirmModal');
    if (modal) {
        console.log('✅ Modal found, showing...');
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    } else {
        console.error('❌ Modal not found!');
    }
}

// Hàm đóng modal
function closeConfirmModal() {
    console.log('🚪 Closing modal...');
    const modal = document.getElementById('confirmModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
    pendingUrl = null;
}

// Hàm xác nhận rời trang
function confirmLeave() {
    console.log('✅ Confirmed leave, redirecting to:', pendingUrl);
    if (pendingUrl) {
        formSubmitting = true;
        window.location.href = pendingUrl;
    }
}

console.log('✅ add_contract.js (COMPLETE FIXED VERSION) loaded successfully');