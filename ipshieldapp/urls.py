from django.urls import path
from . import views

urlpatterns = [


    path('', views.home, name='home'),

    # Đầu tư search & detail
    path('investment/search/', views.investment_search, name='investment_search'),
    path('investment/<int:investment_id>/', views.investment_detail, name='investment_detail'),
    # Đăng ký kinh doanh search & detail
    path('business/search/', views.business_search, name='business_search'),
    path('business/<int:business_id>/', views.business_detail, name='business_detail'),
    # Bản quyền search & detail
    path('copyright/search/', views.copyright_search, name='copyright_search'),
    path('copyright/<int:copyright_id>/', views.copyright_detail, name='copyright_detail'),

    path('trademark/search/', views.trademark_search, name='trademark_search'),
    path('trademark/<int:trademark_id>/', views.trademark_detail, name='trademark_detail'),

    path("contracts/search/", views.contract_search, name="contract_search"),
    path('contracts/copyright/search/',views.contract_copyright_search,name='contract_copyright_search'),
    path('hop-dong/dang-ky-kinh-doanh/', views.contract_business_search, name='contract_business_search'),
    path('hop-dong/dang-ky-dau-tu/',views.contract_investment_search,name='contract_investment_search'),
    path('hop-dong/dich-vu-khac/',views.contract_other_service_search,name='contract_other_service_search'),

    # CUSTOMER
    path('customer-add/', views.add_customer, name='add_customer'),
    path('customer/<int:id>/', views.customer_detail, name='customer_detail'),
    path('customer/<int:id>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/<int:id>/delete/', views.customer_delete, name='customer_delete'),

    # CONTRACT
path('contracts/images/upload/', views.upload_contract_image, name='upload_contract_image'),
path('contracts/images/delete/<int:pk>/', views.delete_contract_image, name='delete_contract_image'),
    path("contracts/add/", views.add_contract, name="add_contract"),
    path('contracts/delete/<int:pk>/', views.contract_delete, name='contract_delete'),
    path("contracts/", views.contract_list, name="contract_list"),
    path("contracts/<int:id>/", views.contract_detail, name="contract_detail"),
    path('<int:pk>/change-status/', views.customer_change_status, name='customer_change_status'),
    path("contracts/edit/<int:id>", views.contract_edit, name="contract_edit"),
    path('api/search-customer/', views.search_customer, name='search_customer'),
# Thêm vào urls.py
path('contract/<int:contract_id>/edit-installments/', views.edit_installment_amounts, name='edit_installment_amounts'),
    # CERTIFICATE (GIẤY CHỨNG NHẬN)
    path(
        'certificate/download/<int:id>/',
        views.download_certificate,
        name='download_certificate'
    ),
    path(
        'business/<int:business_id>/download-registration/',
        views.register_certificate,
        name='register_certificate'
    ),
    path(
     "certificate/delete/<int:pk>/",
     views.delete_certificate,
     name="delete_certificate"
     ),
    path(
    'certificates/upload/',
    views.upload_certificate,
    name='upload_certificate'
    ),
    
    #login.css
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #ho so
    path('profile/', views.profile_view, name='profile'),
    #dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('dashboard-customer-stats/', views.dashboard_customer_stats_api, name='dashboard_customer_stats_api'),
    path('dashboard-trademark-stats/', views.dashboard_trademark_stats_api, name='dashboard_trademark_stats_api'),
    

# 🆕 PORTAL KHÁCH HÀNG
path('portal/profile/', views.portal_customer_profile, name='portal_customer_profile'),

    path('khach-hang/dang-xuat/',  views.customer_logout,          name='customer_logout'),
    path('portal/', views.portal_dashboard, name='portal_dashboard'),
    path('portal/hop-dong/<int:contract_id>/',
                                   views.portal_contract_detail,   name='portal_contract_detail'),
    path('portal/hop-dong/<int:contract_id>/ho-tro/', views.portal_support_request, name='portal_support_request'),
]



