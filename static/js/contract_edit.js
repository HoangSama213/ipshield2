// ===============================
// TAB SWITCHING
// ===============================
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            this.classList.add('active');
            document
                .querySelector(`[data-content="${targetTab}"]`)
                .classList.add('active');
        });
    });
});

// ===============================
// FORMSET ADD / REMOVE (CHUẨN)
// ===============================
document.addEventListener('click', function(e) {

    // ➕ ADD FORM
    if (e.target.closest('.btn-add[data-prefix]')) {
        const btn = e.target.closest('.btn-add[data-prefix]');
        const prefix = btn.dataset.prefix;

        const formset = document.getElementById(`${prefix}-formset`);
        const template = document.getElementById(`${prefix}-empty-template`);
        const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);

        if (!formset || !template || !totalForms) return;

        const index = parseInt(totalForms.value);
        let html = template.innerHTML.replace(/__prefix__/g, index);

        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;

        formset.appendChild(wrapper.firstElementChild);
        totalForms.value = index + 1;
    }

    // ❌ REMOVE FORM
    if (e.target.closest('.btn-remove')) {
        const item = e.target.closest('.formset-item');
        if (!item) return;

        const deleteInput = item.querySelector(
            'input[type="checkbox"][name$="-DELETE"]'
        );

        if (deleteInput) {
            deleteInput.checked = true;
            item.style.display = 'none';
        } else {
            item.remove();
        }
    }
});
// ===============================
// ADD SERVICE DROPDOWN
// ===============================
document.addEventListener('DOMContentLoaded', function() {
    const addServiceBtn = document.getElementById('add-service-btn');
    const addServiceDropdown = document.getElementById('add-service-dropdown');

    if (!addServiceBtn || !addServiceDropdown) return;

    addServiceBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        addServiceDropdown.style.display =
            addServiceDropdown.style.display === 'none' ? 'block' : 'none';
    });

    document.addEventListener('click', function() {
        addServiceDropdown.style.display = 'none';
    });

    addServiceDropdown.addEventListener('click', function(e) {
        const option = e.target.closest('.add-service-option');
        if (!option) return;

        const service = option.dataset.service;
        const block = document.querySelector(`.service-block[data-service="${service}"]`);

        if (block) {
            block.style.display = '';
            // Tự động thêm 1 form trống để điền ngay
            const addBtn = block.querySelector('.btn-add[data-prefix]');
            if (addBtn) addBtn.click();
        }

        option.style.display = 'none';
        addServiceDropdown.style.display = 'none';
    });
});