"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Order
from api.users.models import User
from api.activities.models import OfferActivity, Activity
from api.orders.models import Offer, OrderPayment
from api.chats.models import Message, Chat, SeenBy
from djmoney.models.fields import Money

# Serializers
from api.users.serializers import UserModelSerializer

# Utils
from api.utils import helpers


class OrderModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    seller = UserModelSerializer()
    buyer = UserModelSerializer()

    class Meta:
        """Meta class."""

        model = Order
        fields = (
            "__all__"
        )

        read_only_fields = ("id",)


class AcceptOrderSerializer(serializers.Serializer):
    """Acount verification serializer."""
    payment_method_id = serializers.CharField()
    order = OrderModelSerializer(read_only=True)

    def validate(self, data):
        """Update user's verified status."""

        payment_method_id = data['payment_method_id']
        offer = self.context['offer']
        stripe = self.context['stripe']
        request = self.context['request']
        user = request.user

        offer_object = get_object_or_404(Offer, id=offer['id'])
        self.context['offer_object'] = offer_object
        if offer_object.accepted:
            raise serializers.ValidationError(
                "This offer already has been accepted")
        # Check if offer is not accepted
        try:

            if not user.stripe_customer_id:

                new_customer = stripe.Customer.create(
                    description="claCustomer_"+user.first_name+'_'+user.last_name,
                    name=user.first_name+' '+user.last_name,
                    email=user.email,
                )
                user.stripe_customer_id = new_customer['id']
                user.save()

            product = stripe.Product.create(name=offer['title'] + '_' + user.username)

            if not 'type' in offer:
                raise serializers.ValidationError(
                    "Not a valid order type")
            if not 'seller' in offer:
                raise serializers.ValidationError(
                    "Not seller in offer")
            seller = get_object_or_404(User, id=offer['seller'])
            if not 'unit_amount' in offer:
                raise serializers.ValidationError(
                    "Not unit amount in offer")
            unit_amount = float(offer['unit_amount'])
            if not 'service_fee' in offer:
                raise serializers.ValidationError(
                    "There is not service fee in this offer")
            service_fee = float(offer['service_fee'])

            price = None
            if offer['type'] == Order.NORMAL_ORDER:
                price = stripe.Price.create(
                    unit_amount=int(unit_amount * 100),
                    currency=user.currency,
                    product=product['id']
                )
                invoice_item = stripe.InvoiceItem.create(
                    customer=user.stripe_customer_id,
                    price=price['id'],
                )
                invoice = stripe.Invoice.create(
                    customer=user.stripe_customer_id,
                    # transfer_data={
                    #     "destination": serialised_course.get('instructor').get('profile').get('stripe_account_id'),
                    # },
                    default_payment_method=payment_method_id
                )
                user.default_payment_method = payment_method_id
                user.save()
                invoice_paid = stripe.Invoice.pay(invoice['id'])

                # Invoice paid succesfully, do actions
                self.context['price'] = price
                self.context['invoice_paid'] = invoice_paid

            elif offer['type'] == Order.TWO_PAYMENTS_ORDER:

                price = stripe.Price.create(
                    unit_amount=int(unit_amount * 100),
                    currency=user.currency,
                    product=product['id']
                )
                invoice_item = stripe.InvoiceItem.create(
                    customer=user.stripe_customer_id,
                    price=price['id'],
                )
                invoice = stripe.Invoice.create(
                    customer=user.stripe_customer_id,
                    transfer_data={
                        "destination": seller.stripe_account_id,
                    },
                    application_fee_amount=int(service_fee * 100),
                    # application_fee=5,
                    default_payment_method=payment_method_id
                )
                user.default_payment_method = payment_method_id
                user.save()
                invoice_paid = stripe.Invoice.pay(invoice['id'])
                self.context['price'] = price
                self.context['invoice_paid'] = invoice_paid
            elif offer['type'] == Order.RECURRENT_ORDER:
                if not 'interval_subscription' in offer:
                    raise serializers.ValidationError(
                        "Not interval subscription in offer")
                switcher = {
                    Order.MONTH: "month",
                    Order.YEAR: "year"
                }
                interval = switcher.get(offer['interval_subscription'], None)
                if not interval:
                    raise serializers.ValidationError(
                        "Interval not valid")
                price = stripe.Price.create(
                    unit_amount=int(unit_amount * 100),
                    currency=user.currency,
                    recurring={"interval": interval},
                    product=product['id']
                )

                self.context['price'] = price

            else:
                raise serializers.ValidationError(
                    "Not a valid order type")

        except stripe.error.StripeError as e:

            raise serializers.ValidationError(
                'Something went wrong with stripe')
        except Exception as e:

            raise serializers.ValidationError(
                'Something went wrong')

        return data

    def create(self, validated_data):
        offer = self.context['offer']
        request = self.context['request']
        user = request.user
        stripe = self.context['stripe']

        offer_object = self.context['offer_object']

        service_fee, _ = helpers.convert_currency('USD', user.currency, offer['service_fee'], offer_object.rate_date)
        unit_amount, _ = helpers.convert_currency('USD', user.currency, offer['unit_amount'], offer_object.rate_date)

        new_order = Order.objects.create(
            buyer=offer_object.buyer,
            seller=offer_object.seller,
            title=offer_object.title,
            description=offer_object.description,
            unit_amount=unit_amount,
            service_fee=service_fee,
            first_payment=offer_object.first_payment,
            payment_at_delivery=offer_object.payment_at_delivery,
            delivery_date=offer_object.delivery_date,
            delivery_time=offer_object.delivery_time,
            interval_subscription=offer_object.interval_subscription,
            type=offer_object.type,
            rate_date=offer_object.rate_date
        )

        offer_activity_queryset = OfferActivity.objects.filter(offer=offer_object, status=OfferActivity.PENDENDT)
        offer_activity = None
        if offer_activity_queryset.exists():
            offer_activity = offer_activity_queryset.first()
        activity = offer_activity.activity
        activity.closed = True
        activity.active = False
        activity = Activity.objects.create(
            type=Activity.OFFER,
            closed=True,
            active=False
        )
        OfferActivity.objects.create(
            activity=activity,
            offer=offer_object,
            status=OfferActivity.ACCEPTED
        )

        chats = Chat.objects.filter(participants=new_order.seller)
        chats = chats.filter(participants=new_order.buyer)
        chat_instance = None
        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    chat_instance = chat

        if not chat_instance:

            chat_instance = Chat.objects.create()

            chat_instance.participants.add(new_order.buyer)
            chat_instance.participants.add(new_order.seller)
            chat_instance.save()

        # Create the message

        message = Message.objects.create(chat=chat_instance, activity=activity, sent_by=new_order.buyer)
        chat_instance.last_message = message
        chat_instance.save()

        # Set message seen
        seen_by, created = SeenBy.objects.get_or_create(chat=chat_instance, user=new_order.buyer)
        if seen_by.message != chat_instance.last_message:

            seen_by.message = chat_instance.last_message
            seen_by.save()

        if offer['type'] == Order.NORMAL_ORDER:
            price = self.context['price']
            invoice_paid = self.context['invoice_paid']
            invoice_id = invoice_paid['id']
            currency = invoice_paid['currency']
            charge_id = invoice_paid['charge']
            amount_paid = invoice_paid['amount_paid']
            status = invoice_paid['status']
            invoice_pdf = invoice_paid['invoice_pdf']

            new_order.price_id = price['id']
            new_order.due_to_seller = offer_object.unit_amount
            new_order.save()
            OrderPayment.objects.create(
                order=new_order,
                invoice_id=invoice_id,
                invoice_pdf=invoice_pdf,
                charge_id=charge_id,
                amount_paid=float(amount_paid) / 100,
                currency=currency,
                status=status,
            )
        elif offer['type'] == Order.TWO_PAYMENTS_ORDER:
            price = self.context['price']
            invoice_paid = self.context['invoice_paid']
            invoice_id = invoice_paid['id']
            currency = invoice_paid['currency']
            charge_id = invoice_paid['charge']
            amount_paid = invoice_paid['amount_paid']
            status = invoice_paid['status']
            invoice_pdf = invoice_paid['invoice_pdf']

            new_order.price_id = price['id']
            new_order.payment_at_delivery = offer_object['payment_at_delivery']
            new_order.save()
            OrderPayment.objects.create(
                order=new_order,
                invoice_id=invoice_id,
                invoice_pdf=invoice_pdf,
                charge_id=charge_id,
                amount_paid=float(amount_paid) / 100,
                currency=currency,
                status=status,
            )
        elif offer['type'] == Order.RECURRENT_ORDER:
            price = self.context['price']
            try:
                subscription = stripe.Subscription.create(
                    customer=user.stripe_customer_id,
                    items=[
                        {"price": price['id']}
                    ],
                    expand=["latest_invoice.payment_intent"],
                    application_fee_percent=5,
                    transfer_data={
                        "destination": offer_object.seller.stripe_account_id,
                    },
                    default_payment_method=validated_data['payment_method_id']
                )
                subscription_id = subscription['id']

                new_order.price_id = price['id']
                new_order.subscription_id = subscription_id
                new_order.save()

            except Exception as e:
                new_order.delete()
                offer_object.save()
                print(e)
                raise serializers.ValidationError(
                    'Something went wrong')
        offer_object.accepted = True
        offer_object.save()
        return new_order


# Invoice example
    # {
        #     "account_country": "ES",
        #     "account_name": "FullOrderTracker",
        #     "account_tax_ids": null,
        #     "amount_due": 2039,
        #     "amount_paid": 2039,
        #     "amount_remaining": 0,
        #     "application_fee_amount": null,
        #     "attempt_count": 1,
        #     "attempted": true,
        #     "auto_advance": false,
        #     "billing_reason": "manual",
        #     "charge": "ch_1IIEmeCob7soW4zY8WFSM12C",
        #     "collection_method": "charge_automatically",
        #     "created": 1612710162,
        #     "currency": "eur",
        #     "custom_fields": null,
        #     "customer": "cus_IqgYqdbwbUskrM",
        #     "customer_address": {
        #         "city": "",
        #         "country": "ES",
        #         "line1": "",
        #         "line2": "",
        #         "postal_code": "08012",
        #         "state": "Alex"
        #     },
        #     "customer_email": "ahernandezprat4675@gmail.com",
        #     "customer_name": "Alex_Prat",
        #     "customer_phone": null,
        #     "customer_shipping": null,
        #     "customer_tax_exempt": "none",
        #     "customer_tax_ids": [],
        #     "default_payment_method": "pm_1IIEmaCob7soW4zY9PS6Vaji",
        #     "default_source": null,
        #     "default_tax_rates": [],
        #     "description": null,
        #     "discount": null,
        #     "discounts": [],
        #     "due_date": null,
        #     "ending_balance": 0,
        #     "footer": null,
        #     "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1I4AQuCob7soW4zY/invst_Iu2s3Mxh5n78KYB39UlqYRvw2cBO2k2",
        #     "id": "in_1IIEmcCob7soW4zY4TUb7YO0",
        #     "invoice_pdf": "https://pay.stripe.com/invoice/acct_1I4AQuCob7soW4zY/invst_Iu2s3Mxh5n78KYB39UlqYRvw2cBO2k2/pdf",
        #     "last_finalization_error": null,
        #     "lines": {
        #         "data": [
        #             {
        #                 "amount": 2039,
        #                 "currency": "eur",
        #                 "description": "Curso de finanzas avanzado_alexhernandez",
        #                 "discount_amounts": [],
        #                 "discountable": true,
        #                 "discounts": [],
        #                 "id": "il_1IIEmcCob7soW4zYIc6emWgq",
        #                 "invoice_item": "ii_1IIEmcCob7soW4zYrq6WQVay",
        #                 "livemode": false,
        #                 "metadata": {},
        #                 "object": "line_item",
        #                 "period": {
        #                     "end": 1612710162,
        #                     "start": 1612710162
        #                 },
        #                 "plan": null,
        #                 "price": {
        #                     "active": true,
        #                     "billing_scheme": "per_unit",
        #                     "created": 1612710162,
        #                     "currency": "eur",
        #                     "id": "price_1IIEmcCob7soW4zYVYCyRxOg",
        #                     "livemode": false,
        #                     "lookup_key": null,
        #                     "metadata": {},
        #                     "nickname": null,
        #                     "object": "price",
        #                     "product": "prod_Iu2sCCxXHwCosO",
        #                     "recurring": null,
        #                     "tiers_mode": null,
        #                     "transform_quantity": null,
        #                     "type": "one_time",
        #                     "unit_amount": 2039,
        #                     "unit_amount_decimal": "2039"
        #                 },
        #                 "proration": false,
        #                 "quantity": 1,
        #                 "subscription": null,
        #                 "tax_amounts": [],
        #                 "tax_rates": [],
        #                 "type": "invoiceitem"
        #             }
        #         ],
        #         "has_more": false,
        #         "object": "list",
        #         "total_count": 1,
        #         "url": "/v1/invoices/in_1IIEmcCob7soW4zY4TUb7YO0/lines"
        #     },
        #     "livemode": false,
        #     "metadata": {},
        #     "next_payment_attempt": null,
        #     "number": "3024D4B5-0151",
        #     "object": "invoice",
        #     "paid": true,
        #     "payment_intent": "pi_1IIEmdCob7soW4zY5TgR2zMP",
        #     "period_end": 1613144816,
        #     "period_start": 1611935216,
        #     "post_payment_credit_notes_amount": 0,
        #     "pre_payment_credit_notes_amount": 0,
        #     "receipt_number": null,
        #     "starting_balance": 0,
        #     "statement_descriptor": null,
        #     "status": "paid",
        #     "status_transitions": {
        #         "finalized_at": 1612710163,
        #         "marked_uncollectible_at": null,
        #         "paid_at": 1612710163,
        #         "voided_at": null
        #     },
        #     "subscription": null,
        #     "subtotal": 2039,
        #     "tax": null,
        #     "total": 2039,
        #     "total_discount_amounts": [],
        #     "total_tax_amounts": [],
        #     "transfer_data": null,
        #     "webhooks_delivered_at": null
        # }
