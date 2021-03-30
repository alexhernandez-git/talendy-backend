"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django


# Models
from api.orders.models import Delivery, Order, OrderTip
from api.activities.models import Activity, DeliveryActivity
from api.users.models import User, Earning
from api.chats.models import Message, Chat, SeenBy
from djmoney.models.fields import Money

# Serializers
from api.orders.serializers import OrderModelSerializer

# Utils
from datetime import datetime, timedelta
from django.utils import timezone
from api.utils import helpers


class DeliveryModelSerializer(serializers.ModelSerializer):
    """Delivery model serializer."""
    order = OrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Delivery
        fields = (
            "id",
            "order",
            "response",
            "source_file"
        )
        extra_kwargs = {"source_file": {"required": False, "allow_null": True}}

    def validate(self, data):
        order = self.context['order']
        request = self.context['request']
        user = request.user
        if user != order.seller:
            raise serializers.ValidationError('You are not allowed to do this action')
        if order.status == Order.DELIVERED:
            raise serializers.ValidationError('This order is already delivered')
        if order.status == Order.CANCELLED:
            raise serializers.ValidationError('This order is cancelled')
        if order.type == Order.RECURRENT_ORDER:
            raise serializers.ValidationError('A recurrent order can\'t be delivered')

        return data

    def create(self, validated_data):

        order = self.context['order']
        validated_data['order'] = order
        delivery = Delivery.objects.create(**validated_data)
        activity = Activity.objects.create(
            type=Activity.DELIVERY,
            order=order
        )
        DeliveryActivity.objects.create(
            activity=activity,
            delivery=delivery
        )

        seller = order.seller
        buyer = order.buyer

        chats = Chat.objects.filter(participants=seller)
        chats = chats.filter(participants=buyer)

        chat_instance = None
        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    chat_instance = chat

        if not chat_instance:

            chat_instance = Chat.objects.create()

            chat_instance.participants.add(buyer)
            chat_instance.participants.add(seller)
            chat_instance.save()

        # Create the message

        message = Message.objects.create(chat=chat_instance, activity=activity, sent_by=seller)
        chat_instance.last_message = message
        chat_instance.save()
        # Set message seen
        seen_by, created = SeenBy.objects.get_or_create(chat=chat_instance, user=seller)
        if seen_by.message != chat_instance.last_message:

            seen_by.message = chat_instance.last_message
            seen_by.save()

        return delivery


class AcceptDeliveryModelSerializer(serializers.ModelSerializer):
    """Delivery model serializer."""
    order = OrderModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Delivery
        fields = (
            "id",
            "order",
            "response",
            "source_file"
        )
        read_only_fields = (
            "id",
            "order",
            "response",
            "source_file"
        )
        extra_kwargs = {"source_file": {"required": False, "allow_null": True}}

    def validate(self, data):
        delivery = self.instance
        order = delivery.order
        request = self.context['request']
        user = request.user

        if user != order.buyer:
            raise serializers.ValidationError('You are not allowed to do this action')
        if order.status == Order.DELIVERED:
            raise serializers.ValidationError('This delivery is already accepted')
        if order.status == Order.CANCELLED:
            raise serializers.ValidationError('This order is cancelled')

        payment_method_id = self.context['payment_method_id']
        order_checkout = self.context['order_checkout']

        if 'tip' in order_checkout:
            if not payment_method_id:
                raise serializers.ValidationError('There is no payment method')

        return data

    def update(self, instance, validated_data):
        order = instance.order
        stripe = self.context['stripe']
        request = self.context['request']
        user = request.user
        payment_method_id = self.context['payment_method_id']
        order_checkout = self.context['order_checkout']

        seller = order.seller
        if 'tip' in order_checkout:

            if not user.stripe_customer_id:

                new_customer = stripe.Customer.create(
                    description="talCustomer_"+user.first_name+'_'+user.last_name,
                    name=user.first_name+' '+user.last_name,
                    email=user.email,
                )
                user.stripe_customer_id = new_customer['id']
                user.save()

            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            product = stripe.Product.create(name='Tip of ' + order.oportunity.title + '_' + user.username)
            unit_amount = float(order_checkout['tip'])

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
            )
            user.default_payment_method = payment_method_id
            user.save()
            invoice_paid = stripe.Invoice.pay(invoice['id'])
            invoice_id = invoice_paid['id']
            currency = invoice_paid['currency']
            charge_id = invoice_paid['charge']
            amount_paid = invoice_paid['amount_paid']
            status = invoice_paid['status']
            invoice_pdf = invoice_paid['invoice_pdf']
            # If used credits pay with credits

            tip_usd_amount, _ = helpers.convert_currency(
                "USD", user.currency, order_checkout['tip'], order.rate_date)

            order_tip = OrderTip.objects.create(
                order=order,
                invoice_id=invoice_id,
                invoice_pdf=invoice_pdf,
                charge_id=charge_id,
                amount_paid=float(amount_paid) / 100,
                currency=currency,
                status=status,
                amount_usd=tip_usd_amount
            )
            Earning.objects.create(
                user=seller,
                type=Earning.TIP_REVENUE,
                order_tip=order_tip,
                amount=tip_usd_amount,
                available_for_withdrawn_date=timezone.now() + timedelta(days=14)
            )

        seller.karmas_amount += order.karmas_amount

        order.payment_at_delivery_price_id = price['id']
        seller.save()

        order.status = Order.DELIVERED
        order.save()
        issued_to = order.seller
        issued_by = order.buyer

        chats = Chat.objects.filter(participants=issued_by)
        chats = chats.filter(participants=issued_to)
        activity = Activity.objects.create(
            type=Activity.DELIVERY,
            order=order
        )
        DeliveryActivity.objects.create(
            activity=activity,
            delivery=instance,
            status=DeliveryActivity.ACCEPTED
        )

        chat_instance = None
        if chats.exists():
            for chat in chats:
                if chat.participants.all().count() == 2:
                    chat_instance = chat

            if not chat_instance:

                chat_instance = Chat.objects.create()

                chat_instance.participants.add(issued_to)
                chat_instance.participants.add(issued_by)
                chat_instance.save()

            # Create the message

            message = Message.objects.create(chat=chat_instance, activity=activity, sent_by=issued_by)
            chat_instance.last_message = message
            chat_instance.save()
            # Set message seen
            seen_by, created = SeenBy.objects.get_or_create(chat=chat_instance, user=issued_by)
            if seen_by.message != chat_instance.last_message:

                seen_by.message = chat_instance.last_message
                seen_by.save()
        return instance
