# django-chelseru

بستهٔ جنگویی برای **گپ‌زنی همزمان (WebSocket)**، **راستی‌آزمایی پیامکی (OTP)** و **فرستادن پیامک** با یاری‌دهنده‌های ایرانی.

**نویسنده:** Sobhan Bahman Rashnu

---

## فهرست مطالب

- [ویژگی‌ها](#ویژگیها)
- [نصب](#نصب)
- [پیش‌نیازها و افزودن به تنظیمات](#پیشنیازها-و-افزودن-به-تنظیمات)
- [پیکربندی](#پیکربندی)
- [تعریف آدرس‌ها (URLs)](#تعریف-آدرسها-urls)
- [نقطه‌های پایانی API](#نقطههای-پایانی-api)
  - [/api/otp/send/ — فرستادن رمز یک‌بارمصرف](#apiotpsend--فرستادن-رمز-یکبارمصرف)
  - [/api/authenticate/ — راستی‌آزمایی با OTP و دریافت JWT](#apiauthenticate--راستیآزمایی-با-otp-و-دریافت-jwt)
  - [/api/message/send/ — فرستادن پیامک](#apimessagesend--فرستادن-پیامک)
  - [/api/sessions/ — فهرست نشست‌های فعال](#apisessions--فهرست-نشستهای-فعال)
- [مدل‌ها](#مدلها)

---

## ویژگی‌ها

- 📱 **راستی‌آزمایی پیامکی (OTP):** تولید و فرستادن رمز یک‌بارمصرف و اعتبارسنجی امن.
- 💬 **گپ‌زنی همزمان:** پیام‌رسانی همزمان بر پایهٔ **WebSocket/Channels**.
- ✉️ **فرستادن پیامک:** پشتیبانی از یاری‌دهنده‌های نام‌آشنای ایرانی.

---

## نصب

```bash
pip install django-chelseru
```

---

## پیش‌نیازها و افزودن به تنظیمات

`INSTALLED_APPS` را در `settings.py` به‌روز کنید:

```python
INSTALLED_APPS = [
    # ...
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'drfchelseru',
    # ...
]
```

> نکته: برای قابلیت‌های همزمان (WebSocket) پروژهٔ شما باید با **ASGI** اجرا شود (مانند `daphne` یا `uvicorn`).

---

## پیکربندی

واژه‌نامهٔ `DJANGO_CHELSERU` را در `settings.py` بیفزایید و بر اساس نیاز خود سفارشی‌سازی کنید:

```python
DJANGO_CHELSERU = {
    'AUTH': {
        'AUTH_METHOD': 'OTP',  # روش‌های پشتیبانی‌شده: OTP, PASSWD
        'AUTH_SERVICE': 'rest_framework_simplejwt',  # فعلاً: rest_framework_simplejwt
        'OPTIONS': {
            'OTP_LENGTH': 8,                 # پیش‌فرض: 8
            'OTP_EXPIRE_PER_MINUTES': 4,     # پیش‌فرض: 4
            'OTP_SMS_TEMPLATE_ID': 1,        # شناسهٔ قالب پیامکی OTP
        },
    },
    'SMS': {
        'SMS_SERVICE': 'PARSIAN_WEBCO_IR',  # PARSIAN_WEBCO_IR, MELI_PAYAMAK_COM, KAVENEGAR_COM
        'SETTINGS': {
            'PARSIAN_WEBCO_IR_API_KEY': '',
            'MELI_PAYAMAK_COM_USERNAME': '',
            'MELI_PAYAMAK_COM_PASSWORD': '',
            'MELI_PAYAMAK_COM_FROM': '',
            'KAVENEGAR_COM_API_KEY': 'YOUR_KAVENEGAR_API_KEY',
            'KAVENEGAR_COM_FROM': 'YOUR_KAVENEGAR_FROM_NUMBER',
        },
        'TEMPLATES': {
            'T1': 1,
            'T2': 2,
            # ...
        },
    },
}
```

**راهنما:**

- `AUTH_METHOD`: روش راستی‌آزمایی (برای پیامکی از `'OTP'` استفاده کنید).
- `OTP_LENGTH`: طول رمز یک‌بارمصرف.
- `OTP_EXPIRE_PER_MINUTES`: مدت اعتبار رمز (به دقیقه).
- `OTP_SMS_TEMPLATE_ID`: شناسهٔ قالب پیامکی که برای OTP بهره‌گیری می‌شود.
- `SMS_SERVICE`: انتخاب یاری‌دهندهٔ پیامکی.
- `SETTINGS`: مقادیر دسترسی یاری‌دهندهٔ انتخاب‌شده.
- `TEMPLATES`: نگاشت کلیدهای دلخواه به شناسهٔ قالب‌ها.

---

## تعریف آدرس‌ها (URLs)

در `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('api/', include('drfchelseru.urls')),
    # ...
]
```

---

## نقطه‌های پایانی API

| مسیر                 | شرح                                                | روش  |
| -------------------- | -------------------------------------------------- | ---- |
| `/api/otp/send/`     | فرستادن رمز یک‌بارمصرف به شمارهٔ همراه             | POST |
| `/api/authenticate/` | راستی‌آزمایی کاربر با OTP و دریافت توکن‌های JWT    | POST |
| `/api/sessions/`     | فهرست و مدیریت نشست‌های فعال کاربر (نیازمند احراز) | GET  |
| `/api/message/send/` | فرستادن پیامک با یاری‌دهندهٔ پیکربندی‌شده          | POST |

---

### `/api/otp/send/` — فرستادن رمز یک‌بارمصرف

**روش:** `POST`\
**شرح:** یک OTP به شمارهٔ همراه کاربر فرستاده می‌شود.

**بدنهٔ درخواست:**

| فیلد            | نوع   | شرح                | نمونه         |
| --------------- | ----- | ------------------ | ------------- |
| `mobile_number` | `str` | شمارهٔ همراه کاربر | `09121234567` |

**نمونهٔ درخواست:**

```http
POST /api/otp/send/ HTTP/1.1
Content-Type: application/json

{
  "mobile_number": "09121234567"
}
```

**پاسخ‌های ممکن:**

- `200 OK`
  ```json
  { "details": "The OTP code was sent correctly." }
  ```
- `400 Bad Request` — ساختار نادرست `mobile_number`
- `409 Conflict`
  ```json
  { "details": "An OTP code has already been sent. Please wait X seconds before trying again." }
  ```
- `500 Internal Server Error` — خطا در کارگذار

---

### `/api/authenticate/` — راستی‌آزمایی با OTP و دریافت JWT

**روش:** `POST`\
**شرح:** اعتبارسنجی کاربر با OTP؛ در صورت موفقیت، توکن‌های `access` و `refresh` بازگردانده می‌شود.

**بدنهٔ درخواست:**

| فیلد            | نوع   | شرح                         | نمونه         |
| --------------- | ----- | --------------------------- | ------------- |
| `mobile_number` | `str` | شمارهٔ همراه کاربر          | `09121234567` |
| `code`          | `str` | رمز یک‌بارمصرف دریافت‌شده   | `12345678`    |
| `group`         | `int` | (اختیاری) شناسهٔ گروه کاربر | `1`           |

**نمونهٔ درخواست:**

```http
POST /api/authenticate/ HTTP/1.1
Content-Type: application/json

{
  "mobile_number": "09121234567",
  "code": "12345678",
  "group": 1
}
```

**پاسخ‌های ممکن:**

- `200 OK`
  ```json
  { "access": "...", "refresh": "..." }
  ```
- `401 Unauthorized`
  ```json
  { "error": "The code sent to this mobile number was not found." }
  ```
- `400 Bad Request` — فیلدهای الزامی ناپیدا/نامعتبر
- `500 Internal Server Error` — خطا در کارگذار

---

### `/api/message/send/` — فرستادن پیامک

**روش:** `POST`\
**شرح:** فرستادن پیامک سفارشی با یاری‌دهندهٔ پیکربندی‌شده.

**بدنهٔ درخواست:**

| فیلد            | نوع   | شرح                                            | نمونه           |
| --------------- | ----- | ---------------------------------------------- | --------------- |
| `mobile_number` | `str` | شمارهٔ همراه گیرنده                            | `09121234567`   |
| `message_text`  | `str` | متن پیام (حداکثر ۲۹۰ نویسه)                    | `Hello, World!` |
| `template_id`   | `int` | (برای برخی یاری‌دهنده‌ها مانند پارسیان الزامی) | `1`             |

**نمونهٔ درخواست:**

```http
POST /api/message/send/ HTTP/1.1
Content-Type: application/json

{
  "mobile_number": "09121234567",
  "message_text": "Hello, World!",
  "template_id": 1
}
```

**پاسخ‌های ممکن:**

- `200 OK`
  ```json
  { "details": "The Message was sent correctly." }
  ```
- `400 Bad Request` — خطاهای اعتبارسنجی فیلدها
- `401 Unauthorized` — احراز انجام نشده
- `500 Internal Server Error` — خطا در کارگذار
- `502 Bad Gateway` — خطای بازگشتی از یاری‌دهندهٔ پیامکی

---

### `/api/sessions/` — فهرست نشست‌های فعال

**روش:** `GET`\
**شرح:** همهٔ نشست‌های فعال کاربر را برمی‌گرداند. نیازمند **احراز هویت** (`IsAuthenticated`).

**سربرگ‌های لازم:**

| سربرگ           | مقدار                        |
| --------------- | ---------------------------- |
| `Authorization` | `Bearer <your_access_token>` |

**نمونهٔ درخواست:**

```http
GET /api/sessions/ HTTP/1.1
Authorization: Bearer <your_access_token>
```

---

## مدل‌ها

این بسته یک مدل **Session** برای مدیریت نشست‌های فعال کاربران فراهم می‌کند.\
از طریق نقطهٔ پایانی `/api/sessions/` می‌توانید نشست‌ها را مشاهده/مدیریت کنید.