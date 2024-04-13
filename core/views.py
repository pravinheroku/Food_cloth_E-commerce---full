from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
from taggit.models import Tag
from core.models import (
    Product,
    Category,
    Vendor,
    CartOrder,
    CartOrderItems,
    ProductImages,
    ProductReview,
    Wishlist,
    Address,
)
from userauths.models import ContactUs, Profile
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages

import calendar
from django.db.models.functions import ExtractMonth
from django.core import serializers
from django.contrib.auth.decorators import login_required

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm

# Create your views here.


def index(request):
    products = Product.objects.filter(product_status="published", featured=True)

    context = {"products": products}

    return render(request, "core/index.html", context)


def product_list_view(request):
    products = Product.objects.filter(product_status="published")

    context = {"products": products}

    return render(request, "core/product-list.html", context)


def category_list_view(request):
    categories = Category.objects.all()

    context = {"categories": categories}

    return render(request, "core/category-list.html", context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {"category": category, "products": products}

    return render(request, "core/category-product-list.html", context)


def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {"vendors": vendors}

    return render(request, "core/vendor-list.html", context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    context = {"vendor": vendor, "products": products}

    return render(request, "core/vendor-detail.html", context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # Getting all Reviews
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    # Getting average reviews
    average_rating = ProductReview.objects.filter(product=product).aggregate(
        rating=Avg("rating")
    )

    p_image = product.p_images.all()

    # Product Review form
    review_form = ProductReviewForm

    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(
            user=request.user, product=product
        ).count()

        if user_review_count > 0:
            make_review = False

    context = {
        "p": product,
        "products": products,
        "average_rating": average_rating,
        "make_review": make_review,
        "p_image": p_image,
        "review_form": review_form,
        "reviews": reviews,
    }

    return render(request, "core/product-detail.html", context)


def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")

    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag,
    }

    return render(request, "core/tag.html", context)


def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST["review"],
        rating=request.POST["rating"],
    )

    context = {
        "user": user.username,
        "review": request.POST["review"],
        "rating": request.POST["rating"],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(
        rating=Avg("rating")
    )

    return JsonResponse(
        {"bool": True, "context": context, "average_reviews": average_reviews}
    )


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(
        title__icontains=query, description__icontains=query
    ).order_by("-date")

    context = {"products": products, "query": query}

    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")

    min_price = request.GET["min_price"]
    max_price = request.GET["max_price"]

    products = (
        Product.objects.filter(product_status="published").order_by("-id").distinct()
    )

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET["id"])] = {
        "title": request.GET["title"],
        "qty": request.GET["qty"],
        "price": request.GET["price"],
        "image": request.GET["image"],
        "pid": request.GET["pid"],
        "price": request.GET["price"],
    }

    if "cart_data_obj" in request.session:
        if str(request.GET["id"]) in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            cart_data[str(request.GET["id"])]["qty"] = int(
                cart_product[str(request.GET["id"])]["qty"]
            )
            cart_data.update(cart_data)
            request.session["cart_data_obj"] = cart_data
        else:
            cart_data = request.session["cart_data_obj"]
            cart_data.update(cart_product)
            request.session["cart_data_obj"] = cart_data

    else:
        request.session["cart_data_obj"] = cart_product
    return JsonResponse(
        {
            "data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
        }
    )


# def cart_view(request):
#     cart_total_amount = 0
#     if "cart_data_obj" in request.session:
#         for p_id, item in request.session["cart_data_obj"].items():
#             cart_total_amount += int(item["qty"]) * float(item["price"])
#         return render(
#             request,
#             "core/cart.html",
#             {
#                 "cart_data": request.session[
#                     "cart_data_obj"
#                 ],  # Corrected variable name
#                 "totalcartitems": len(request.session["cart_data_obj"]),
#                 "cart_total_amount": cart_total_amount,
#             },
#         )
#     else:
#         messages.warning(request, "Your cart is empty")
#         return redirect("core:index")


def cart_view(request):
    cart_total_amount = 0
    currency_symbol = "₹"  # Define the currency symbol used in your application
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            # Extract numeric part of the price string and remove currency symbol
            price = item["price"].replace(currency_symbol, "").strip()
            # Convert cleaned price string to float
            try:
                cart_total_amount += int(item["qty"]) * float(price)
            except ValueError:
                # Handle cases where the price string cannot be converted to float
                # You may want to log or handle this error appropriately
                pass
        return render(
            request,
            "core/cart.html",
            {
                "cart_data": request.session[
                    "cart_data_obj"
                ],  # Corrected variable name
                "totalcartitems": len(request.session["cart_data_obj"]),
                "cart_total_amount": cart_total_amount,
            },
        )
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")


def delete_item_from_cart(request):
    product_id = str(request.GET["id"])
    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            del request.session["cart_data_obj"][product_id]
            request.session["cart_data_obj"] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            cart_total_amount += int(item["qty"]) * float(item["price"])

    context = render_to_string(
        "core/async/cart-list.html",
        {
            "cart_data": request.session["cart_data_obj"],  # Corrected variable name
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )
    return JsonResponse(
        {"data": context, "totalcartitems": len(request.session["cart_data_obj"])}
    )


def update_cart(request):
    product_id = str(request.GET["id"])
    product_qty = request.GET["qty"]

    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            cart_data[str(request.GET["id"])]["qty"] = product_qty
            request.session["cart_data_obj"] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            cart_total_amount += int(item["qty"]) * float(item["price"])

    context = render_to_string(
        "core/async/cart-list.html",
        {
            "cart_data": request.session["cart_data_obj"],  # Corrected variable name
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )
    return JsonResponse(
        {"data": context, "totalcartitems": len(request.session["cart_data_obj"])}
    )


# @login_required
# def checkout_view(request):

#     cart_total_amount = 0
#     total_amount = 0

#     # Checking if "cart_data_obj" session is still exists
#     if "cart_data_obj" in request.session:
#         # Getting total amount for paypal
#         for p_id, item in request.session["cart_data_obj"].items():
#             total_amount += int(item["qty"]) * float(item["price"])

#             # Create order object
#             order = CartOrder.objects.create(
#                 user=request.user,
#                 price=total_amount,
#             )

#         # Getting total amount for the cart
#         for p_id, item in request.session["cart_data_obj"].items():
#             cart_total_amount += int(item["qty"]) * float(item["price"])

#             cart_order_products = CartOrderItems.objects.create(
#                 order=order,
#                 invoice_no="INVOICE_NO-" + str(order.id),
#                 item=item["title"],
#                 image=item["image"],
#                 qty=item["qty"],
#                 price=item["price"],
#                 total=float(item["qty"]) * float(item["price"]),
#             )

#     host = request.get_host()
#     paypal_dict = {
#         "business": settings.PAYPAL_RECEIVER_EMAIL,
#         "amount": cart_total_amount,
#         "item-name": "Order-Item-No-" + str(order.id),
#         "invoice": "INV_NO-" + str(order.id),
#         "currency_code": "USD",
#         "notify_url": "http://{}{}".format(host, reverse("core:paypal-ipn")),
#         "return_url": "http://{}{}".format(host, reverse("core:payment-completed")),
#         "cancel_url": "http://{}{}".format(host, reverse("core:payment-failed")),
#     }

#     paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

#     # cart_total_amount = 0
#     # if "cart_data_obj" in request.session:
#     #     for p_id, item in request.session["cart_data_obj"].items():
#     #         cart_total_amount += int(item["qty"]) * float(item["price"])

#     try:
#         active_address = Address.objects.get(user=request.user, status=True)
#     except:
#         messages.warning(
#             request, "There are multiple addresses are selected, select only one!"
#         )
#         active_address = None

#     return render(
#         request,
#         "core/checkout.html",
#         {
#             "cart_data": request.session["cart_data_obj"],  # Corrected variable name
#             "totalcartitems": len(request.session["cart_data_obj"]),
#             "cart_total_amount": cart_total_amount,
#             "paypal_payment_button": paypal_payment_button,
#             "active_address": active_address,
#         },
#     )

@login_required
def checkout_view(request):
    cart_total_amount = 0
    order = None  # Initialize order outside the loop

    # Checking if "cart_data_obj" session exists
    if "cart_data_obj" in request.session:
        # Create order object only if there are items in the cart
        if request.session["cart_data_obj"]:
            # Calculating total amount
            for p_id, item in request.session["cart_data_obj"].items():
                # Remove currency symbol and whitespace from the price string
                price_str = item["price"].replace('₹', '').strip()
                cart_total_amount += int(item["qty"]) * float(price_str)

            order = CartOrder.objects.create(
                user=request.user,
                price=cart_total_amount,
            )

            # Creating order items
            for p_id, item in request.session["cart_data_obj"].items():
                # Remove currency symbol and whitespace from the price string
                price_str = item["price"].replace('₹', '').strip()
                cart_order_products = CartOrderItems.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO-" + str(order.id),
                    item=item["title"],
                    image=item["image"],
                    qty=item["qty"],
                    price=price_str,
                    total=float(item["qty"]) * float(price_str),
                )

    if order is None:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")

    host = request.get_host()
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": cart_total_amount,
        "item-name": "Order-Item-No-" + str(order.id),
        "invoice": "INV_NO-" + str(order.id),
        "currency_code": "USD",
        "notify_url": "http://{}{}".format(host, reverse("core:paypal-ipn")),
        "return_url": "http://{}{}".format(host, reverse("core:payment-completed")),
        "cancel_url": "http://{}{}".format(host, reverse("core:payment-failed")),
    }

    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

    try:
        active_address = Address.objects.get(user=request.user, status=True)
    except Address.DoesNotExist:
        messages.warning(
            request, "There are multiple addresses are selected, select only one!"
        )
        active_address = None

    return render(
        request,
        "core/checkout.html",
        {
            "cart_data": request.session.get("cart_data_obj", {}),
            "totalcartitems": len(request.session.get("cart_data_obj", {})),
            "cart_total_amount": cart_total_amount,
            "paypal_payment_button": paypal_payment_button,
            "active_address": active_address,
        },
    )


@login_required
def payment_completed_view(request):
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for p_id, item in request.session["cart_data_obj"].items():
            cart_total_amount += int(item["qty"]) * float(item["price"])

    return render(
        request,
        "core/payment-completed.html",
        {
            "cart_data": request.session["cart_data_obj"],  # Corrected variable name
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )


@login_required
def payment_failed_view(request):
    return render(request, "core/payment-failed.html")


@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    orders = (
        CartOrder.objects.annotate(month=ExtractMonth("order_date"))
        .values("month")
        .annotate(count=Count("id"))
        .values("month", "count")
    )
    month = []
    total_orders = []

    for o in orders:
        month.append(calendar.month_name[o["month"]])
        total_orders.append(o["count"])

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            address=address,
            mobile=mobile,
            user=request.user,
        )
        messages.success(request, "Address added successfully!")
        return redirect("core:dashboard")

    user_profile = Profile.objects.get(user=request.user)

    context = {
        "orders_list": orders_list,
        "address": address,
        "user_profile": user_profile,
        "month": month,
        "total_orders": total_orders,
        "orders": orders,
    }
    return render(request, "core/dashboard.html", context)


def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)
    context = {
        "order_items": order_items,
    }
    return render(request, "core/order-detail.html", context)


def make_default_address(request):
    id = request.GET["id"]
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


@login_required
def wishlist_view(request):

    wishlist = Wishlist.objects.all()

    context = {"w": wishlist}

    return render(request, "core/wishlist.html", context)


def add_to_wishlist(request):
    product_id = request.GET["id"]
    product = Product.objects.get(id=product_id)

    context = {}

    wishlist_count = Wishlist.objects.filter(product=product, user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {"bool": True}
    else:
        new_wishlist = Wishlist.objects.create(product=product, user=request.user)

        context = {"bool": True}

    return JsonResponse(context)


def remove_wishlist(request):
    pid = request.GET["id"]
    wishlist = Wishlist.objects.filter(user=request.user)

    product = Wishlist.objects.filter(id=pid)
    product.delete()

    context = {"bool": True, "wishlist": wishlist}
    wishlist_json = serializers.serialize("json", wishlist)
    data = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data": data, "w": wishlist_json})


def contact(request):
    return render(request, "core/contact.html")


def ajax_contact(request):
    full_name = request.GET["full_name"]
    email = request.GET["email"]
    phone = request.GET["phone"]
    subject = request.GET["subject"]
    message = request.GET["message"]

    contact = ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    data = {"bool": True, "message": "Message sent successfully!"}

    return JsonResponse({"data": data})


def about_us(request):
    return render(request, "core/about_us.html")


def purchase_guide(request):
    return render(request, "core/purchase_guide.html")


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def term_of_service(request):
    return render(request, "core/terms_of_privacy.html")



