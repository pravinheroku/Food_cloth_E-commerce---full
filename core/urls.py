from django.urls import path
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
]
