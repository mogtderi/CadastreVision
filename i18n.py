"""
Internationalization (English / Persian) + Persian text shaping (Lite Edition).
"""

import sys
from typing import Dict
import arabic_reshaper
from bidi.algorithm import get_display

SUPPORTED = ("fa", "en")

_REORDER_ON_WINDOWS = False
_SHOULD_REORDER = _REORDER_ON_WINDOWS or not sys.platform.startswith("win")


def _shape_one_line(line: str) -> str:
    reshaped = arabic_reshaper.reshape(line)
    if _SHOULD_REORDER:
        return get_display(reshaped)
    return reshaped


def shape_fa(text: str) -> str:
    if "\n" in text:
        return "\n".join(_shape_one_line(line) for line in text.split("\n"))
    return _shape_one_line(text)


STRINGS: Dict[str, Dict[str, str]] = {
    "app.title": {
        "fa": "سامانه جامع کاداستر و تحلیل مزارع (نسخه دمو / Lite)",
        "en": "Cadastre & Field Analysis Suite (Lite / Demo Edition)"
    },
    "sidebar.header": {
        "fa": "🛠️ سامانه کاداستر اراضی (Lite)",
        "en": "🛠️ Land Cadastre Suite (Lite)"
    },
    "btn.load_image": {"fa": "📁 انتخاب عکس هوایی", "en": "📁 Load Aerial Image"},

    "geo.header": {
        "fa": "🔒 ژئورفرنس تصویر (ویژه نسخه Pro)",
        "en": "🔒 Georeference (Pro Feature)"
    },
    "geo.help": {
        "fa": "ثبت مختصات جهانی و تبدیل واحد به هکتار/متر\nدر نسخه تجاری (Pro) فعال است.",
        "en": "Real-world coordinates & hectare/meter units\nare available in the Pro Edition."
    },
    "geo.top_left": {"fa": "بالا-چپ:", "en": "Top-left:"},
    "geo.bottom_right": {"fa": "پایین-راست:", "en": "Bottom-right:"},
    "geo.set_button": {
        "fa": "🔒 ثبت مختصات مرجع (Pro)",
        "en": "🔒 Set Reference Coordinates (Pro)"
    },
    "geo.status_unset": {
        "fa": "🔒 محاسبه بر حسب پیکسل (ژئورفرنس در نسخه Pro)",
        "en": "🔒 Pixel units only (Georeference in Pro)"
    },

    "opt.exg": {
        "fa": "🔒 اعمال شاخص گیاهی ExG (Pro)",
        "en": "🔒 Apply vegetation index ExG (Pro)"
    },
    "opt.show_id": {
        "fa": "نمایش شماره شناسایی (ID) روی تصویر",
        "en": "Show parcel ID on image"
    },
    "opt.save_attrs": {
        "fa": "🔒 ذخیره جدول مساحت در خروجی GIS (Pro)",
        "en": "🔒 Include attribute table in GIS (Pro)"
    },
    "opt.suppress_builtup": {
        "fa": "🔒 حذف خودکار مناطق مسکونی (Pro)",
        "en": "🔒 Auto-suppress built-up areas (Pro)"
    },
    "opt.suppress_builtup_help": {
        "fa": "⚡ نسخه Lite از لبه‌یابی پایه استفاده می‌کند.\nموتور هوش مصنوعی و فیلتر باغات در نسخه Pro فعال است.",
        "en": "⚡ Lite Edition uses basic edge detection.\nMean-Shift orchard filter & AI engine are in Pro."
    },

    "sam.toggle": {
        "fa": "🔒 برش هوشمند با مدل هوش مصنوعی SAM (Pro)",
        "en": "🔒 Smart-click AI Segmentation SAM (Pro)"
    },
    "draw.toggle_off": {
        "fa": "🔒 حالت ترسیم و اصلاح دستی (Pro)",
        "en": "🔒 Manual Polygon Drawing (Pro)"
    },
    "draw.finish": {
        "fa": "🔒 پایان ترسیم و ثبت قطعه (Pro)",
        "en": "🔒 Finish & Save Parcel (Pro)"
    },

    "color.label": {"fa": "رنگ ترسیم مرزها:", "en": "Boundary line color:"},
    "color.red": {"fa": "قرمز (Red)", "en": "Red"},
    "color.green": {"fa": "سبز (Green)", "en": "Green"},
    "color.blue": {"fa": "آبی (Blue)", "en": "Blue"},
    "color.yellow": {"fa": "زرد (Yellow)", "en": "Yellow"},

    "slider.canny": {"fa": "حساسیت لبه‌یابی پایه (Canny): {val}", "en": "Basic Edge Sensitivity (Canny): {val}"},
    "slider.area": {"fa": "حداقل مساحت قطعه: {val:.2f}% از عکس", "en": "Minimum parcel size: {val:.2f}% of image"},
    "slider.smooth": {"fa": "ضریب صاف‌سازی خطوط: {val}", "en": "Line-smoothing factor: {val}"},

    "btn.process": {"fa": "⚡ اجرای تحلیل پایه (نسخه دمو)", "en": "⚡ Run Basic Analysis (Demo)"},
    "btn.process.working": {"fa": "⏳ در حال پردازش...", "en": "⏳ Processing..."},

    "out.crs_wgs84": {"fa": "WGS 84 (EPSG:4326) [Pro]", "en": "WGS 84 (EPSG:4326) [Pro]"},
    "out.crs_utm_auto": {"fa": "UTM (پیشنهاد خودکار) [Pro]", "en": "UTM (auto-suggested) [Pro]"},
    "btn.save_gis": {
        "fa": "🔒 ذخیره لایه مکانی GIS / KML (Pro)",
        "en": "🔒 Save GIS Layer / KML (Pro)"
    },
    "btn.save_excel": {
        "fa": "🔒 خروجی گزارش اکسل جامع (.xlsx) (Pro)",
        "en": "🔒 Export Full Excel Report (.xlsx) (Pro)"
    },
    "btn.save_pdf": {
        "fa": "🔒 تولید گزارش نقشه PDF (Pro)",
        "en": "🔒 Generate PDF Map Report (Pro)"
    },
    "btn.save_img": {
        "fa": "🖼️ ذخیره عکس مرزبندی‌شده (فعال در دمو)",
        "en": "🖼️ Save Annotated Image (Active in Demo)"
    },
    "btn.contact": {
        "fa": "💎 خرید نسخه Pro / ارتباط با طراح",
        "en": "💎 Upgrade to Pro / Contact Developer"
    },
    "btn.lang": {"fa": "EN", "en": "FA"},

    "status.ready": {
        "fa": "آماده (نسخه نمایشی Lite — موتور پردازش پایه).",
        "en": "Ready (Lite Demo Edition — Basic Processing Engine)."
    },
    "status.no_image": {
        "fa": "تصویری انتخاب نشده است\nلطفاً یک عکس هوایی بارگذاری کرده و پردازش را اجرا کنید.\n\n"
              "💡 توجه: این نسخه دمو (Lite) است و از الگوریتم لبه‌یابی پایه استفاده می‌کند.\n"
              "برای دسترسی به موتور تشخیص پیشرفته (مخصوص باغات و مزارع پیچیده)، مدل SAM و خروجی‌های GIS، نسخه Pro را تهیه نمایید.",
        "en": "No image selected\nPlease load an aerial image and run the analysis.\n\n"
              "💡 Note: This is the Lite Demo Edition using basic edge detection.\n"
              "Upgrade to Pro for the advanced Mean-Shift/ExG engine, SAM AI segmentation, and GIS/Excel/PDF exports."
    },
    "status.image_loaded": {
        "fa": "تصویر بارگذاری شد: {name} ({w}×{h} پیکسل)",
        "en": "Image loaded: {name} ({w}×{h} px)"
    },
    "status.processing": {
        "fa": "در حال تحلیل تصویر با الگوریتم پایه...",
        "en": "Analyzing image with basic pipeline..."
    },
    "status.error": {"fa": "خطا در پردازش.", "en": "Processing error."},
    "status.done": {
        "fa": "{n} قطعه با الگوریتم پایه شناسایی شد. (برای دقت بالاتر و حذف نویز باغات از نسخه Pro استفاده کنید)",
        "en": "{n} parcels detected (Basic Engine). Upgrade to Pro for high-precision orchard/field detection."
    },

    "msg.error": {"fa": "خطا", "en": "Error"},
    "msg.warning": {"fa": "هشدار", "en": "Warning"},
    "msg.success": {"fa": "نتیجه تحلیل (نسخه Lite)", "en": "Analysis Result (Lite Edition)"},
    "msg.saved": {"fa": "ذخیره شد", "en": "Saved"},
    "msg.no_image_selected": {"fa": "لطفاً ابتدا یک تصویر هوایی انتخاب کنید!", "en": "Please select an aerial image first!"},
    "msg.file_not_readable": {"fa": "این فایل به‌عنوان تصویر خوانده نشد. فرمت را بررسی کنید.", "en": "This file could not be read as an image. Check the format."},
    "msg.process_error": {"fa": "پردازش تصویر با خطا متوقف شد:\n{error}", "en": "Image processing stopped with an error:\n{error}"},
    "msg.detected_n": {
        "fa": "تعداد {n} قطعه با الگوریتم پایه استخراج شد!\n\n"
              "💡 نکته: در نسخه Lite از لبه‌یابی ساده استفاده شده است که ممکن است در بافت‌های پیچیده (مثل باغات یا سقف خانه‌ها) خطا یا خطوط شکسته ایجاد کند.\n\n"
              "در نسخه Pro با بهره‌گیری از فیلتر Mean-Shift، شاخص گیاهی ExG، حذف خودکار مناطق مسکونی و هوش مصنوعی SAM، مرزها با دقت مهندسی استخراج می‌شوند.",
        "en": "{n} parcels extracted using the basic pipeline!\n\n"
              "💡 Note: The Lite Edition uses basic Canny edge detection, which may produce noisy edges inside orchards or built-up areas.\n\n"
              "The Pro Edition uses Mean-Shift filtering, ExG vegetation indices, built-up cluster suppression, and Meta's SAM AI for survey-grade boundaries."
    },
    "msg.need_process_first": {"fa": "ابتدا باید تصویری را پردازش کنید!", "en": "You need to process an image first!"},
    "msg.image_saved": {
        "fa": "تصویر مرزبندی‌شده (همراه با واترمارک نسخه دمو) ذخیره شد:\n{path}",
        "en": "Annotated image (with Demo watermark) saved:\n{path}"
    },

    "pro.title": {
        "fa": "🔒 قابلیت ویژه نسخه تجاری (Pro Edition)",
        "en": "🔒 Pro Edition Feature"
    },
    "pro.body": {
        "fa": "قابلیت «{feature}» در نسخه نمایشی (Lite) قفل است.\n\n"
              "✨ امکانات نسخه کامل (Pro Edition):\n"
              "• موتور پردازش تصویر پیشرفته (Mean-Shift + ExG) بدون نویز در باغات\n"
              "• برش هوشمند تک‌کلیکی با مدل هوش مصنوعی SAM\n"
              "• ترسیم و ویرایش دستی چندضلعی‌ها بدون محدودیت\n"
              "• ژئورفرنس دقیق و محاسبه مساحت واقعی (هکتار و مترمربع)\n"
              "• خروجی مستقیم Shapefile, GeoJSON, GeoPackage, KML/KMZ\n"
              "• گزارش‌های مهندسی Excel و نقشه PDF بدون واترمارک\n\n"
              "📞 برای تهیه نسخه کامل (Pro) با توسعه‌دهنده در ارتباط باشید:\n"
              "👨‍💻 طراح: مهندس مقتدری (Moghtaderi)\n"
              "💬 تلگرام: @mogtdri\n"
              "📧 ایمیل: Mogtdri@Gmail.com\n"
              "🌐 گیت‌هاب: github.com/mogtderi",
        "en": "The feature \"{feature}\" is locked in the Lite / Demo Edition.\n\n"
              "✨ Unlock the full power in Pro Edition:\n"
              "• Advanced Detection Engine (Mean-Shift + ExG + Built-up Suppression)\n"
              "• One-click AI Parcel Segmentation (Meta SAM)\n"
              "• Interactive Manual Polygon Drawing & Editing\n"
              "• Two-corner Georeferencing & Real UTM Area/Perimeter (ha / m)\n"
              "• Full GIS Exports (Shapefile, GeoJSON, GeoPackage, KML, KMZ)\n"
              "• Comprehensive Excel (.xlsx) & PDF Map Reports (No Watermark)\n\n"
              "📞 Contact the developer to get the Pro Edition:\n"
              "👨‍💻 Developer: Moghtaderi\n"
              "💬 Telegram: @mogtdri\n"
              "📧 Email: Mogtdri@Gmail.com\n"
              "🌐 GitHub: github.com/mogtderi"
    },

    "contact.body": {
        "fa": "👨‍💻 Coded By Moghtaderi\n"
              "📧 ایمیل: Mogtdri@Gmail.com\n"
              "💬 تلگرام: @mogtdri\n"
              "🌐 گیت‌هاب: github.com/mogtderi\n\n"
              "برای سفارش نسخه کامل (Pro) یا پروژه‌های اختصاصی GIS و هوش مصنوعی پیام دهید.",
        "en": "👨‍💻 Coded By Moghtaderi\n"
              "📧 Email: Mogtdri@Gmail.com\n"
              "💬 Telegram: @mogtdri\n"
              "🌐 GitHub: github.com/mogtderi\n\n"
              "Contact for the Pro Edition or custom GIS & Computer Vision solutions."
    },
    "contact.title": {"fa": "ارتباط با طراح و سفارش نسخه Pro", "en": "Contact & Upgrade to Pro"},

    "table.header": {
        "fa": "📋 جدول ویژگی‌ها (در نسخه Lite بر حسب پیکسل — در نسخه Pro بر حسب هکتار)",
        "en": "📋 Parcel Attributes (Pixel units in Lite — Hectares/Meters in Pro)"
    },
    "table.col_id": {"fa": "شناسه قطعه", "en": "Parcel ID"},
    "table.col_area": {"fa": "مساحت (پیکسل مربع)", "en": "Area (px²)"},
    "table.col_perimeter": {"fa": "محیط (پیکسل)", "en": "Perimeter (px)"},

    "unit.px2": {"fa": "px²", "en": "px²"},
    "unit.px": {"fa": "px", "en": "px"},
}


class Translator:
    def __init__(self, lang: str = "fa"):
        self.lang = lang if lang in SUPPORTED else "fa"

    def set_lang(self, lang: str) -> None:
        if lang in SUPPORTED:
            self.lang = lang

    def t(self, key: str, **kwargs) -> str:
        entry = STRINGS.get(key)
        if entry is None:
            return key
        text = entry.get(self.lang, entry.get("fa", key))
        if kwargs:
            text = text.format(**kwargs)
        if self.lang == "fa":
            text = shape_fa(text)
        return text