/* =====================================================
   1. TOGGLE FIELD THEO LOẠI KHÁCH HÀNG
===================================================== */

document.addEventListener('DOMContentLoaded', function () {
    const typeField = document.getElementById("id_customer_type");
    const cccdField = document.getElementById("cccd_field");
    const taxField = document.getElementById("tax_field");

    const cccdInput = document.getElementById("id_cccd");
    const taxInput = document.getElementById("id_tax_code");

    function toggleFields() {
        if (typeField.value === "personal") {
            // HIỆN CCCD
            cccdField.style.display = "block";
            taxField.style.display = "none";

            // BẮT BUỘC CCCD
            cccdInput.required = true;
            taxInput.required = false;
            taxInput.value = "";

        } else {
            // HIỆN MST
            cccdField.style.display = "none";
            taxField.style.display = "block";

            // BẮT BUỘC MST
            cccdInput.required = false;
            taxInput.required = true;
            cccdInput.value = "";
        }
    }

    typeField.addEventListener("change", toggleFields);
    toggleFields(); // chạy ngay khi load
});


/* =====================================================
   2. AUTO HIDE ALERT
===================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    document.querySelectorAll('.btn-close').forEach(btn => {
        btn.addEventListener('click', function () {
            const alert = this.closest('.alert');
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    });
});

/* =====================================================
   3. MODAL CONFIRM
===================================================== */
let isNavigatingAway = false;
let pendingNavigation = null;

function showConfirmModal() {
    const modal = document.getElementById('confirmModal');
    if (!modal) return;
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeConfirmModal() {
    const modal = document.getElementById('confirmModal');
    if (!modal) return;
    modal.classList.remove('show');
    document.body.style.overflow = '';
    pendingNavigation = null;
}

function closeModalOnOverlay(e) {
    if (e.target.id === 'confirmModal') {
        closeConfirmModal();
    }
}

/* =====================================================
   4. KIỂM TRA FORM CÓ DỮ LIỆU HAY KHÔNG
===================================================== */
function hasFormData() {
    const form = document.querySelector('form');
    if (!form) return false;

    const formData = new FormData(form);

    for (let [key, value] of formData.entries()) {
        if (key === 'csrfmiddlewaretoken') continue;

        const v = String(value).trim();
        if (v && v !== 'active' && v !== 'personal') {
            return true;
        }
    }
    return false;
}

/* =====================================================
   5. NÚT TRỞ VỀ TRONG GIAO DIỆN
===================================================== */
function showConfirmModalIfNeeded() {
    if (hasFormData()) {
        pendingNavigation = "{% url 'home' %}";
        showConfirmModal();
    } else {
        window.location.href = "{% url 'home' %}";
    }
}

/* =====================================================
   6. BACK TRÌNH DUYỆT (CHUẨN – KHÔNG DOUBLE BACK)
===================================================== */
document.addEventListener('DOMContentLoaded', function () {
    // pushState DUY NHẤT 1 LẦN
    history.pushState({ confirmLeave: true }, '', location.href);
});

window.addEventListener('popstate', function () {

    if (isNavigatingAway) {
        return; // cho back thật
    }

    if (hasFormData()) {
        pendingNavigation = 'back';
        showConfirmModal();
    } else {
        isNavigatingAway = true;
        history.back();
    }
});

/* =====================================================
   7. BẮT TẤT CẢ LINK
===================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const links = document.querySelectorAll(
        'a:not(.btn-confirm):not(.btn-cancel):not([href^="#"])'
    );

    links.forEach(link => {
        link.addEventListener('click', function (e) {
            if (hasFormData() && !isNavigatingAway) {
                e.preventDefault();
                pendingNavigation = this.href;
                showConfirmModal();
            }
        });
    });
});

/* =====================================================
   8. NÚT XÁC NHẬN RỜI TRANG
===================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const confirmButton = document.getElementById('confirmButton');
    if (!confirmButton) return;

    confirmButton.addEventListener('click', function (e) {
        e.preventDefault();
        isNavigatingAway = true;

        if (pendingNavigation === 'back') {
            history.back();
        } else if (pendingNavigation) {
            window.location.href = pendingNavigation;
        } else {
            window.location.href = "{% url 'home' %}";
        }
    });
});

/* =====================================================
   9. FORM SUBMIT – KHÔNG CONFIRM
===================================================== */
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', function () {
        isNavigatingAway = true;
    });
});

/* =====================================================
   10. ESC ĐÓNG MODAL
===================================================== */
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeConfirmModal();
    }
});