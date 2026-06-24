"""
RK Store — Notifications (Stage 6)
Sends order confirmation Email and SMS via Azure Communication Services.

Flow:
    Order placed → send_order_notifications() called
                        ↓
                 ├── send_order_email()  → ACS Email
                 └── send_order_sms()   → ACS SMS
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# EMAIL NOTIFICATION
# ════════════════════════════════════════════════════════════════════════════

def send_order_email(order, customer):
    """
    Send order confirmation email via Azure Communication Services.

    Returns True if sent successfully, False otherwise.
    Never raises an exception — failures are logged and order still completes.
    """

    # Skip if ACS email is not configured yet (safe fallback)
    if not settings.ACS_EMAIL_CONNECTION_STRING:
        logger.warning("[ACS Email] Not configured — skipping email notification.")
        return False

    try:
        from azure.communication.email import EmailClient

        client = EmailClient.from_connection_string(
            settings.ACS_EMAIL_CONNECTION_STRING
        )

        # Build the email items list for order
        items_text = ""
        items_html = ""
        for item in order.items.all():
            items_text += f"  - {item.product.name} x{item.quantity} @ CAD ${item.unit_price} = CAD ${item.line_total}\n"
            items_html += f"""
                <tr>
                    <td style="padding:8px;border-bottom:1px solid #1E3A5F">{item.product.name}</td>
                    <td style="padding:8px;border-bottom:1px solid #1E3A5F;text-align:center">{item.quantity}</td>
                    <td style="padding:8px;border-bottom:1px solid #1E3A5F;text-align:right">CAD ${item.unit_price}</td>
                    <td style="padding:8px;border-bottom:1px solid #1E3A5F;text-align:right">CAD ${item.line_total}</td>
                </tr>"""

        message = {
            "senderAddress": settings.ACS_SENDER_EMAIL,
            "recipients": {
                "to": [{
                    "address":     customer.email,
                    "displayName": customer.name,
                }]
            },
            "content": {
                "subject": f"Order Confirmed — {order.order_number} | RK Store",

                # Plain text version (for email clients that don't render HTML)
                "plainText": f"""
Hi {customer.name},

Your order has been confirmed!

Order Number : {order.order_number}
Total Amount : CAD ${order.total_amount}
Status       : {order.get_status_display()}

Items Ordered:
{items_text}

Shipping To  : {customer.address}

Thank you for shopping with RK Store — Canada's Premier iPhone Destination.
Powered by Azure App Service + Azure SQL Database.

RK Store Team
""",
                # HTML version (rendered in most modern email clients)
                "html": f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#050B18;font-family:Arial,sans-serif">
  <div style="max-width:560px;margin:40px auto;background:#0D1528;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.07)">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1E3A5F,#0D1528);padding:32px 40px;border-bottom:1px solid rgba(255,255,255,0.07)">
      <h1 style="margin:0;font-size:24px;font-weight:900;color:#3B82F6;letter-spacing:-0.04em">RK Store</h1>
      <p style="margin:4px 0 0;font-size:12px;color:#64748B">Canada's Premier iPhone Destination</p>
    </div>

    <!-- Body -->
    <div style="padding:32px 40px">
      <div style="text-align:center;margin-bottom:24px">
        <div style="width:60px;height:60px;background:rgba(16,185,129,0.1);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;border:2px solid rgba(16,185,129,0.3);font-size:28px">✅</div>
        <h2 style="color:#F1F5F9;margin:16px 0 4px">Order Confirmed!</h2>
        <p style="color:#94A3B8;margin:0">Hi {customer.name}, your order is on its way.</p>
      </div>

      <!-- Order Number -->
      <div style="background:#111E35;border-radius:10px;padding:14px;text-align:center;margin-bottom:24px;border:1px solid rgba(37,99,235,0.3)">
        <div style="font-size:11px;color:#64748B;margin-bottom:4px">ORDER NUMBER</div>
        <div style="font-size:20px;font-weight:800;color:#3B82F6;letter-spacing:0.06em">{order.order_number}</div>
      </div>

      <!-- Order Items Table -->
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
        <thead>
          <tr style="background:#111E35">
            <th style="padding:10px 8px;text-align:left;font-size:11px;color:#64748B;font-weight:600">PRODUCT</th>
            <th style="padding:10px 8px;text-align:center;font-size:11px;color:#64748B;font-weight:600">QTY</th>
            <th style="padding:10px 8px;text-align:right;font-size:11px;color:#64748B;font-weight:600">PRICE</th>
            <th style="padding:10px 8px;text-align:right;font-size:11px;color:#64748B;font-weight:600">TOTAL</th>
          </tr>
        </thead>
        <tbody style="color:#F1F5F9;font-size:14px">
          {items_html}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" style="padding:12px 8px;text-align:right;font-weight:700;color:#94A3B8">Order Total</td>
            <td style="padding:12px 8px;text-align:right;font-weight:800;font-size:16px;color:#3B82F6">CAD ${order.total_amount}</td>
          </tr>
        </tfoot>
      </table>

      <!-- Shipping Address -->
      <div style="background:#111E35;border-radius:10px;padding:14px;margin-bottom:24px">
        <div style="font-size:11px;color:#64748B;margin-bottom:6px;font-weight:600">SHIPPING TO</div>
        <div style="color:#F1F5F9;font-size:14px">{customer.address}</div>
      </div>

      <!-- Azure Note -->
      <div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);border-radius:9px;padding:12px;text-align:center;font-size:12px;color:#10B981">
        ⚡ Powered by Azure App Service · Azure SQL Database · Azure Communication Services
      </div>
    </div>

    <!-- Footer -->
    <div style="padding:20px 40px;border-top:1px solid rgba(255,255,255,0.07);text-align:center">
      <p style="margin:0;font-size:12px;color:#64748B">© 2025 RK Store · Mississauga, Ontario, Canada</p>
    </div>
  </div>
</body>
</html>
"""
            }
        }

        poller = client.begin_send(message)
        result  = poller.result()

        logger.info(
            f"[ACS Email] ✅ Sent to {customer.email} "
            f"for order {order.order_number} — ID: {result.id}"
        )
        return True

    except Exception as exc:
        logger.error(f"[ACS Email] ❌ Failed for order {order.order_number}: {exc}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# SMS NOTIFICATION
# ════════════════════════════════════════════════════════════════════════════

def send_order_sms(order, customer):
    """
    Send order confirmation SMS via Azure Communication Services.

    Returns True if sent successfully, False otherwise.
    Never raises an exception — failures are logged and order still completes.
    """

    # Skip if ACS SMS is not configured yet
    if not settings.ACS_SMS_CONNECTION_STRING:
        logger.warning("[ACS SMS] Not configured — skipping SMS notification.")
        return False

    # Skip if customer has no phone number
    if not customer.phone:
        logger.warning(f"[ACS SMS] No phone number for {customer.email} — skipping.")
        return False

    try:
        from azure.communication.sms import SmsClient

        client = SmsClient.from_connection_string(
            settings.ACS_SMS_CONNECTION_STRING
        )

        sms_message = (
            f"RK Store: Hi {customer.name}! "
            f"Order {order.order_number} confirmed. "
            f"Total: CAD ${order.total_amount}. "
            f"Thank you for your purchase!"
        )

        response = client.send(
            from_=settings.ACS_SENDER_PHONE,
            to=[customer.phone],
            message=sms_message,
            enable_delivery_report=True,
        )

        result = response[0]
        if result.successful:
            logger.info(
                f"[ACS SMS] ✅ Sent to {customer.phone} "
                f"for order {order.order_number}"
            )
            return True
        else:
            logger.error(
                f"[ACS SMS] ❌ Failed for {customer.phone}: "
                f"{result.error_message}"
            )
            return False

    except Exception as exc:
        logger.error(f"[ACS SMS] ❌ Exception for order {order.order_number}: {exc}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# MAIN NOTIFICATION HANDLER
# Called from views.py after order is successfully created
# ════════════════════════════════════════════════════════════════════════════

def send_order_notifications(order, customer):
    """
    Send both email and SMS notifications for a confirmed order.
    Updates the order record with notification status.

    Called from OrderCreateView after successful order creation.
    Runs after the database transaction is committed so a notification
    failure never rolls back a valid order.
    """

    logger.info(f"[Notifications] Sending for order {order.order_number}...")

    email_sent = send_order_email(order, customer)
    sms_sent   = send_order_sms(order, customer)

    # Save notification status to database
    order.email_sent = email_sent
    order.sms_sent   = sms_sent
    order.save(update_fields=['email_sent', 'sms_sent'])

    logger.info(
        f"[Notifications] Order {order.order_number} — "
        f"Email: {'✅' if email_sent else '❌'} "
        f"SMS: {'✅' if sms_sent else '❌'}"
    )

    return {
        'email_sent': email_sent,
        'sms_sent':   sms_sent,
    }
