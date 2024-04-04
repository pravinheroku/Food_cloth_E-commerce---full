from django.urls import path, include
from core import views

app_name = "core"

urlpatterns = [
    # HomePage
    path("", views.index, name="index"),
    path("products/", views.product_list_view, name="product-list"),
    path("product/<pid>/", views.product_detail_view, name="product-detail"),
    # Category
    path("category/", views.category_list_view, name="category-list"),
    path(
        "category/<cid>/",
        views.category_product_list_view,
        name="category-product-list",
    ),
    # vendor
    path("vendors/", views.vendor_list_view, name="vendor-list"),
    path("vendor/<vid>/", views.vendor_detail_view, name="vendor-detail"),
    # Tags
    path("products/tag/<slug:tag_slug>", views.tag_list, name="tags"),
    # Add Review
    path("ajax-add-review/<int:pid>/", views.ajax_add_review, name="ajax-add-review"),
    # Search Functionality
    path("search/", views.search_view, name="search"),
    # for Filter
    path("filter-products/", views.filter_product, name="filter-product"),
    # Add to cart
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    # Cart page url
    path("cart/", views.cart_view, name="cart"),
    # Delete item from cart
    path("delete-from-cart/", views.delete_item_from_cart, name="delete-from-cart"),
    # Update cart
    path("update-cart/", views.update_cart, name="update-cart"),
    # checkout url
    path("checkout/", views.checkout_view, name="checkout"),
    # Paypal url
    path("paypal/", include("paypal.standard.ipn.urls")),
    # Payment success
    path("payment-completed/", views.payment_completed_view, name="payment-completed"),
    # Payment failed
    path("payment-failed/", views.payment_failed_view, name="payment-failed"),
    # Customer dashboard
    path("dashboard/", views.customer_dashboard, name="dashboard"),
    # Order detail
    path("dashboard/order/<int:id>/", views.order_detail, name="order-detail"),
    # Address Defaul maker
    path(
        "make-default-address/", views.make_default_address, name="make-default-address"
    ),
    # Wishlist url
    path("wishlist/", views.wishlist_view, name="wishlist"),
    # Adding to wishlist
    path("add-to-wishlist/", views.add_to_wishlist, name="add-to-wishlist"),
    # Deleting product from wihslist
    path("remove-from-wishlist/", views.remove_wishlist, name="remove-from-wishlist"),
    # contact-page
    path("contact/", views.contact, name="contact"),
    # contact-form ajax
    path("ajax-contact-form/", views.ajax_contact, name="ajax-contact-form"),
]
