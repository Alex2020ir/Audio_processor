# این برنامه یک فایل صوتی می‌گیرد و نسخه‌ای با نویز افزوده یا با نویز کمتر ذخیره می‌کند.
# برای ساخت مسیرها، خواندن پوشه‌ها و پیدا کردن محل ذخیره از امکانات سیستم‌عامل استفاده می‌کنیم.
import os
# با عبارت‌های منظم، حروف راست‌به‌چپ و جداکننده‌های مسیر را پیدا می‌کنیم.
import re
# فایل‌های قلم و تنظیمات آن‌ها را بر اساس الگوی نامشان پیدا می‌کنیم.
import glob
# برای خواندن و نوشتن فایل صوتی با قالب WAV از این کتابخانه استفاده می‌کنیم.
# WAV = Waveform Audio File Format
import wave
# جست‌وجو و پردازش صدا را در رشته‌ای جدا اجرا می‌کنیم تا کاربر بتواند با صفحه کار کند.
import threading
# نمونه‌های صوتی را در آرایه نگه می‌داریم تا بتوانیم دامنه و فرکانس آن‌ها را پردازش کنیم.
import numpy as np
# هنگام خطا، مسیر فراخوانی توابع را برای پیدا کردن علت خطا چاپ می‌کنیم.
import traceback
# از زمان برای نام‌گذاری خروجی و تخمین موقعیت پخش استفاده می‌کنیم.
import time
# برای رسم موج‌ها و حلقه‌ها به سینوس، کسینوس و عدد پی نیاز داریم.
import math

# با چند رشته، پوشه‌ها را هم‌زمان می‌خوانیم و نتیجهٔ هرکدام را به‌محض آماده شدن تحویل می‌گیریم.
from concurrent.futures import ThreadPoolExecutor, as_completed

# کلاس پایهٔ برنامهٔ کیوی است و چرخهٔ اجرای پنجره را مدیریت می‌کند.
from kivy.app import App
# اجزای صفحه را در یک ردیف یا ستون می‌چینیم.
from kivy.uix.boxlayout import BoxLayout
# برای فرمان‌هایی مانند انتخاب فایل، دکمه می‌سازیم.
from kivy.uix.button import Button
# دکمهٔ انتخابی، حالت پردازش را پس از لمس کاربر نشان می‌دهد.
from kivy.uix.togglebutton import ToggleButton
# عنوان‌ها، نام فایل‌ها و پیام‌های برنامه را نمایش می‌دهیم.
from kivy.uix.label import Label
# از این کلاس برای ساخت اجزایی مانند لغزنده و نمایشگر صدا استفاده می‌کنیم.
from kivy.uix.widget import Widget
# راهنما و پنجرهٔ انتخاب فایل را روی صفحهٔ اصلی باز می‌کنیم.
from kivy.uix.modalview import ModalView
# کاربر عبارت جست‌وجو را در یک کادر متنی وارد می‌کند.
from kivy.uix.textinput import TextInput
# با پیمایش می‌توان فایل‌ها یا متن‌هایی را دید که در صفحه جا نمی‌شوند.
from kivy.uix.scrollview import ScrollView
# اجزایی مانند نماد دکمه را در جای معینی از کادر قرار می‌دهیم.
from kivy.uix.anchorlayout import AnchorLayout
# رفتار فشردن و رها کردن دکمه را به ردیف‌های فهرست هم می‌دهیم.
from kivy.uix.behaviors import ButtonBehavior
# تغییرات صفحه و اجرای دوره‌ای پویانمایی را با ساعت کیوی زمان‌بندی می‌کنیم.
from kivy.clock import Clock
# تشخیص سیستم‌عامل مشخص می‌کند کدام روش دسترسی به فایل اجرا شود.
from kivy.utils import platform
# واحد dp اندازهٔ اجزای صفحه را با تراکم پیکسل‌های نمایشگر سازگار می‌کند.
# dp = Density-independent Pixel
from kivy.metrics import dp
# با شکل‌ها و خط‌ها، نمادها، دکمه‌ها و موج صدا را می‌کشیم.
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse, Triangle
# با تغییر این ویژگی‌ها، کیوی توابع وابسته به آن‌ها را فراخوانی می‌کند.
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, StringProperty
# فایل صوتی پردازش‌شده را برای پخش در برنامه بارگذاری می‌کنیم.
from kivy.core.audio import SoundLoader
# حرکت کلید و ظاهر شدن کارت تنظیمات را به‌تدریج نمایش می‌دهیم.
from kivy.animation import Animation
# قلم همراه کیوی را در میان منابع برنامه پیدا می‌کنیم.
from kivy.resources import resource_find

# برای ذخیرهٔ تصویر شکل موج، ابزار رسم نمودار را بارگذاری می‌کنیم.
import matplotlib
# روش رسم Agg نمودار را در حافظه رسم می‌کند تا بتوانیم آن را بدون باز کردن پنجره ذخیره کنیم.
# Agg = Anti-Grain Geometry
matplotlib.use('Agg')
# با این بخش، محورهای نمودار را می‌سازیم و تصویر نهایی را ذخیره می‌کنیم.
import matplotlib.pyplot as plt

# نتیجهٔ تشخیص اندروید را نگه می‌داریم تا در بخش‌های بعدی از آن استفاده کنیم.
IS_ANDROID = (platform == 'android')

if IS_ANDROID:
    try:
        # ابزار درخواست مجوز را فقط هنگام اجرا روی اندروید بارگذاری می‌کنیم.
        from android.permissions import request_permissions, Permission
    except Exception as e:
        print("Android import error:", e)

# مرورگر داخلی فقط فایل‌های صوتی با این پسوندها را برای پردازش می‌پذیرد.
# MP3 = MPEG-1 Audio Layer III
# MPEG = Moving Picture Experts Group
# M4A = MPEG-4 Audio
# FLAC = Free Lossless Audio Codec
# AAC = Advanced Audio Coding
# WMA = Windows Media Audio
AUDIO_EXT = ('.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aac', '.wma')

# برای هر گروه از فایل‌ها، شکل نماد، رنگ و پسوندها را کنار هم نگه می‌داریم.
FILE_TYPES = (
    ('audio', None, AUDIO_EXT + ('.opus', '.amr', '.mid', '.midi', '.aiff', '.aif', '.3ga')),
    ('video', (0.93, 0.36, 0.40, 1), ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.3gp', '.flv', '.wmv', '.m4v')),
    ('image', (0.72, 0.45, 0.95, 1), ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.svg', '.tif', '.tiff')),
    ('pdf', (0.90, 0.22, 0.21, 1), ('.pdf',)),
    ('doc', (0.25, 0.52, 0.96, 1), ('.doc', '.docx', '.odt', '.rtf', '.epub')),
    ('sheet', (0.13, 0.65, 0.35, 1), ('.xls', '.xlsx', '.ods', '.csv', '.tsv')),
    ('slides', (0.96, 0.49, 0.13, 1), ('.ppt', '.pptx', '.odp')),
    ('text', (0.52, 0.60, 0.72, 1), ('.txt', '.md', '.log', '.ini', '.cfg', '.srt', '.lrc')),
    ('code', (0.05, 0.65, 0.75, 1), ('.py', '.java', '.kt', '.c', '.cpp', '.h', '.js', '.ts', '.html',
                                     '.css', '.json', '.xml', '.yml', '.yaml', '.sh', '.bat', '.kv', '.spec')),
    ('archive', (0.80, 0.58, 0.20, 1), ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso')),
    ('apk', (0.40, 0.74, 0.22, 1), ('.apk', '.apks', '.xapk', '.aab', '.exe', '.msi')),
)
# جدول را بر اساس پسوند فهرست می‌کنیم تا برای هر فایل مستقیماً به نماد و رنگ آن برسیم.
_EXT_MAP = {ext: (kind, tint) for kind, tint, exts in FILE_TYPES for ext in exts}


def file_style(name):
    """نماد و رنگ فایل را از روی پسوند آن پیدا می‌کند."""
    # پسوند را با حروف کوچک بررسی می‌کنیم و برای پسوند ناشناس نماد عمومی برمی‌گردانیم.
    return _EXT_MAP.get(os.path.splitext(name)[1].lower(), ('file', (0.55, 0.58, 0.66, 1)))


def has_all_files_access():
    """وضعیت مجوز دسترسی به همهٔ فایل‌ها را در اندروید بررسی می‌کند."""
    # این بررسی ویژهٔ اندروید است و در سیستم‌های دیگر نتیجهٔ مثبت برمی‌گرداند.
    if platform != 'android':
        return True
    try:
        from jnius import autoclass
        # سطح SDK دستگاه را می‌خوانیم. بررسی مجوز ویژه از سطح ۳۰، یعنی اندروید ۱۱، شروع می‌شود.
        # SDK = Software Development Kit
        if autoclass('android.os.Build$VERSION').SDK_INT < 30:
            return True
        # از خود اندروید می‌پرسیم که آیا برنامه مجوز مدیریت همهٔ فایل‌ها را دارد.
        return bool(autoclass('android.os.Environment').isExternalStorageManager())
    # در صورت خطای بررسی، خطا را چاپ می‌کنیم و مانند حالت داشتن مجوز ادامه می‌دهیم.
    except Exception as e:
        print("All-files access check error:", e)
        return True


def open_all_files_settings():
    """صفحهٔ تنظیمات دسترسی به همهٔ فایل‌ها را باز می‌کند."""
    try:
        from jnius import autoclass
        # پنجرهٔ فعال برنامه را می‌گیریم تا بتواند تنظیمات اندروید را باز کند.
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        # اندروید از یک URI برای مشخص کردن بستهٔ همین برنامه استفاده می‌کند.
        # URI = Uniform Resource Identifier
        Uri = autoclass('android.net.Uri')
        try:
            # ابتدا صفحهٔ مجوز همین برنامه را باز می‌کنیم.
            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            intent.setData(Uri.parse('package:' + activity.getPackageName()))
            activity.startActivity(intent)
        except Exception:
            # اگر صفحهٔ اختصاصی باز نشد، به صفحهٔ عمومی مدیریت این مجوز می‌رویم.
            activity.startActivity(Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION))
    except Exception as e:
        print("All-files settings error:", e)

# الگوی RTL بازه‌هایی از یونیکد را برای تشخیص نوشته‌های راست‌به‌چپ پوشش می‌دهد.
# RTL = Right-to-Left
_RTL_RE = re.compile('[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]')
# پس از شکل‌دهی حروف، نشانه‌های نامرئی جهت متن و نیم‌فاصله (ZWNJ) را از نسخهٔ نمایشی حذف می‌کنیم.
# ZWNJ = Zero Width Non-Joiner
_INVISIBLE_RE = re.compile('[\u200b-\u200f\u202a-\u202e\u2060-\u2069\ufeff]')
# نتیجهٔ جست‌وجوی قلم فارسی و لاتین را جداگانه نگه می‌داریم.
_FONT_CACHE = []
_LATIN_CACHE = []


# بررسی می‌کنیم که متن دست‌کم یک نویسه در بازه‌های راست‌به‌چپ داشته باشد.
def has_rtl(text):
    return bool(text) and bool(_RTL_RE.search(text))


def _font_from_android_xml(etc_dirs=('/system/etc',),
                           font_dirs=('/system/fonts/', '/system/product/fonts/',
                                      '/product/fonts/', '/system_ext/fonts/')):
    """مسیر قلم خط عربی و فارسی را از تنظیمات قلم اندروید پیدا می‌کند."""
    # فهرست قلم‌های اندروید را از فایل‌های XML می‌خوانیم.
    # XML = Extensible Markup Language
    import xml.etree.ElementTree as ET
    found = []
    for etc in etc_dirs:
        # هم فایل تنظیمات اصلی قلم‌ها و هم فایل‌های قلم جایگزین را بررسی می‌کنیم.
        for xml_path in sorted(glob.glob(os.path.join(etc, 'fonts*.xml'))) + \
                        sorted(glob.glob(os.path.join(etc, 'font_fallback*.xml'))):
            try:
                root = ET.parse(xml_path).getroot()
            # فایل تنظیماتی را که خوانده نمی‌شود کنار می‌گذاریم و سراغ فایل بعدی می‌رویم.
            except Exception:
                continue
            for fam in root.iter('family'):
                # فقط خانواده‌هایی را بررسی می‌کنیم که برچسب خط عربی دارند.
                if 'Arab' not in (fam.get('lang') or ''):
                    continue
                for f in fam.iter('font'):
                    name = (f.text or '').strip()
                    # دو پسوند TTF و OTF را برای فایل‌های قلم می‌پذیریم.
                    # TTF = TrueType Font
                    # OTF = OpenType Font
                    if not name.lower().endswith(('.ttf', '.otf')):
                        continue
                    # قلم معمولی با وزن ۴۰۰ اولویت دارد. در یک اولویت یکسان، نام‌های بدون کروشه زودتر بررسی می‌شوند.
                    regular = (f.get('weight', '400') == '400' and f.get('style', 'normal') == 'normal')
                    found.append((0 if regular else 1, '[' in name, name))
    # اولین قلمی را برمی‌گردانیم که واقعاً در یکی از پوشه‌های دستگاه وجود دارد.
    for _, _, name in sorted(found):
        for d in font_dirs:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None


def get_rtl_font():
    """مسیر یک قلم مناسب برای نمایش فارسی را در دستگاه پیدا می‌کند."""
    # اگر قبلاً جست‌وجو کرده‌ایم، همان نتیجه را برمی‌گردانیم.
    if _FONT_CACHE:
        return _FONT_CACHE[0]
    found = None
    try:
        # ابتدا قلمی را می‌خواهیم که خود اندروید برای این خط معرفی کرده است.
        found = _font_from_android_xml()
    except Exception as e:
        print("fonts.xml error:", e)
    try:
        # اگر قلمی پیدا نشد، مسیرهای شناخته‌شدهٔ اندروید، ویندوز، لینوکس و مک را امتحان می‌کنیم.
        candidates = [
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoNaskhArabicUI-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/NotoSansArabicUI-Regular.ttf',
            '/system/fonts/DroidSansArabic.ttf',
            'C:\\Windows\\Fonts\\tahoma.ttf',
            'C:\\Windows\\Fonts\\segoeui.ttf',
            'C:\\Windows\\Fonts\\arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
        for p in candidates:
            if found is None and os.path.exists(p):
                found = p
        if found is None:
            # در آخر، نام فایل‌های قلم دستگاه را با چند الگوی رایج جست‌وجو می‌کنیم.
            for folder in ('/system/fonts/', '/system/product/fonts/', '/product/fonts/'):
                for pat in ('*Arabic*.ttf', '*Naskh*.ttf', '*Farsi*.ttf', '*Persian*.ttf',
                            '*Vazir*.ttf', '*Arabic*.otf'):
                    hits = sorted(glob.glob(folder + pat))
                    if hits:
                        found = hits[0]
                        break
                if found:
                    break
    except Exception as e:
        print("Font search error:", e)
    print('Persian font:', found)
    # نتیجه را حتی اگر قلمی پیدا نشده باشد ذخیره می‌کنیم تا جست‌وجو تکرار نشود.
    _FONT_CACHE.append(found)
    return found


def get_latin_font():
    """ابتدا قلم لاتین همراه کیوی و سپس قلم‌های موجود در دستگاه را بررسی می‌کند."""
    if _LATIN_CACHE:
        return _LATIN_CACHE[0]
    found = None
    try:
        # ابتدا مسیر قلم لاتین همراه کیوی را می‌گیریم.
        p = resource_find('data/fonts/Roboto-Regular.ttf')
        if p and os.path.exists(p):
            found = p
    except Exception as e:
        print("Latin font (kivy) error:", e)
    if found is None:
        # اگر قلم همراه برنامه پیدا نشد، مسیرهای رایج قلم لاتین دستگاه را بررسی می‌کنیم.
        for p in ('/system/fonts/Roboto-Regular.ttf',
                  '/system/fonts/RobotoStatic-Regular.ttf',
                  '/system/fonts/SECRobotoLight-Regular.ttf',
                  '/system/fonts/DroidSans.ttf',
                  'C:\\Windows\\Fonts\\arial.ttf',
                  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
            if os.path.exists(p):
                found = p
                break
    print('Latin font:', found)
    _LATIN_CACHE.append(found)
    return found


# برای متن دارای حروف راست‌به‌چپ، در صورت دسترسی قلم مناسب آن خط را برمی‌گردانیم.
def fa_font(text, default='Roboto'):
    if not has_rtl(text):
        return default
    return get_rtl_font() or default


_FORMS_CACHE = []


def _get_forms():
    """از داده‌های یونیکد، جدول شکل‌های مختلف حروف و ترکیب‌های لام و الف را می‌سازد."""
    # جدول شکل‌های حروف را یک بار می‌سازیم و در فراخوانی‌های بعدی دوباره به کار می‌بریم.
    if _FORMS_CACHE:
        return _FORMS_CACHE[0]
    forms, lig = {}, {}
    try:
        import unicodedata
        # شکل‌های نمایشی را از جدول یونیکد می‌خوانیم تا شکل هر حرف را در جایگاه‌های مختلف بشناسیم.
        for cp in list(range(0xFB50, 0xFDFF)) + list(range(0xFE70, 0xFF00)):
            ch = chr(cp)
            dec = unicodedata.decomposition(ch)
            if not dec.startswith('<'):
                continue
            # برچسبی مانند شکل آغازین یا پایانی را از شمارهٔ نویسه‌های پایه جدا می‌کنیم.
            tag, _, rest = dec.partition('> ')
            tag = tag[1:]
            if tag not in ('isolated', 'final', 'initial', 'medial'):
                continue
            # شماره‌های شانزده‌مبنایی را به حروف اصلی تبدیل می‌کنیم.
            base = ''.join(chr(int(h, 16)) for h in rest.split())
            if len(base) == 1:
                forms.setdefault(base, {})[tag] = ch
            # شکل‌های ترکیبی «لا» را جدا نگه می‌داریم، چون دو حرف در یک شکل نوشته می‌شوند.
            elif len(base) == 2 and base[0] == '\u0644' and base[1] in '\u0622\u0623\u0625\u0627':
                lig.setdefault(base, {})[tag] = ch
    except Exception as e:
        print("Arabic forms error:", e)
    _FORMS_CACHE.append((forms, lig))
    return _FORMS_CACHE[0]


# بررسی می‌کنیم که نویسه از نشانه‌های اعراب یا از علامت‌های تکمیلی این خط باشد.
def _is_mark(ch):
    return '\u064B' <= ch <= '\u065F' or ch == '\u0670' or '\u06D6' <= ch <= '\u06ED'


def _reshape(text):
    """شکل نوشتاری هر حرف را با توجه به اتصال به حروف مجاور انتخاب می‌کند."""
    # جدول شکل‌های حرف و ترکیب‌های لام و الف را برای شکل‌دهی متن می‌گیریم.
    forms, ligs = _get_forms()
    if not forms:
        return text
    chars = list(text)
    n = len(chars)

    # داشتن شکل آغازین یا میانی یعنی حرف می‌تواند به حرف بعدی وصل شود.
    def can_join_next(c):
        f = forms.get(c)
        return bool(f) and ('initial' in f or 'medial' in f)

    # داشتن شکل پایانی یا میانی یعنی حرف می‌تواند به حرف قبلی وصل شود.
    def can_join_prev(c):
        f = forms.get(c)
        return bool(f) and ('final' in f or 'medial' in f)

    items = []
    i = 0
    # متن را از ابتدا می‌خوانیم و هر ترکیب شناخته‌شدهٔ لام و الف را یک واحد در نظر می‌گیریم.
    while i < n:
        c = chars[i]
        if c == '\u0644' and i + 1 < n and (c + chars[i + 1]) in ligs:
            items.append(('lig', c + chars[i + 1]))
            i += 2
        else:
            items.append(('ch', c))
            i += 1

    # هنگام پیدا کردن حرف مجاور، از روی نشانه‌های اعراب عبور می‌کنیم.
    def letter_at(k, step):
        k += step
        while 0 <= k < len(items):
            kind, v = items[k]
            if kind == 'ch' and _is_mark(v):
                k += step
                continue
            return k
        return None

    out = []
    for k, (kind, v) in enumerate(items):
        # همسایهٔ قبلی را بررسی می‌کنیم تا شکل جدا یا پایانی لام و الف را تشخیص دهیم.
        pk = letter_at(k, -1)
        prev_joins = pk is not None and items[pk][0] == 'ch' and can_join_next(items[pk][1])
        if kind == 'lig':
            out.append(ligs[v].get('final' if prev_joins else 'isolated', v[0]))
            continue
        if v not in forms:
            out.append(v)
            continue
        # برای حروف معمولی، امکان اتصال را از هر دو طرف می‌سنجیم.
        prev_joins = prev_joins and can_join_prev(v)
        nk = letter_at(k, +1)
        next_joins = False
        if nk is not None and can_join_next(v):
            nkind, nv = items[nk]
            next_joins = (nkind == 'lig' and 'final' in ligs[nv]) or \
                         (nkind == 'ch' and can_join_prev(nv))
        # با توجه به اتصال‌ها، شکل میانی، آغازین، پایانی یا جدا را برمی‌گزینیم.
        if next_joins and prev_joins:
            form = 'medial'
        elif next_joins:
            form = 'initial'
        elif prev_joins:
            form = 'final'
        else:
            form = 'isolated'
        out.append(forms[v].get(form) or forms[v].get('isolated') or v)
    return ''.join(out)


# هنگام نمایش متن راست‌به‌چپ، جهت جفت‌نشانه‌هایی مانند پرانتز را قرینه می‌کنیم.
_MIRROR = {'(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{', '<': '>', '>': '<'}


# برای تعیین ترتیب نمایش، حروف، اعداد، اعراب، پرانتزها و نشانه‌های خنثی را تشخیص می‌دهیم.
def _char_class(ch):
    if _is_mark(ch):
        return 'M'
    if ch.isdigit():
        return 'D'
    if _RTL_RE.search(ch):
        return 'R'
    if ch.isalpha():
        return 'L'
    if ch in _MIRROR:
        return 'B'
    return 'N'


def _bidi(text):
    """ترتیب نمایشی متن دوجهته را با روشی ساده‌شده تعیین می‌کند."""
    # هر حرف و اعراب پس از آن را کنار هم نگه می‌داریم تا با تغییر ترتیب، از هم جدا نشوند.
    units = []
    for ch in text:
        if _is_mark(ch) and units:
            units[-1].append(ch)
        else:
            units.append([ch])
    if not units:
        return text

    # نوع هر گروه را از اولین نویسهٔ آن تعیین می‌کنیم.
    types = []
    for u in units:
        t = _char_class(u[0])
        types.append('N' if t == 'M' else t)

    # اولین حرف دارای جهت، جهت پایهٔ سطر را تعیین می‌کند. مقدار آغازین برای متن چپ‌به‌راست است.
    base = 0
    for t in types:
        if t == 'R':
            base = 1
            break
        if t == 'L':
            base = 0
            break
    base_dir = 'R' if base else 'L'

    # در متن راست‌به‌چپ به پرانتز جهت می‌دهیم تا در مرحلهٔ نمایش درست قرینه شود.
    types = [('R' if (t == 'B' and base) else ('N' if t == 'B' else t)) for t in types]

    # برای تعیین جهت نشانه‌های خنثی، عدد و حرف راست‌به‌چپ را در یک گروه می‌گذاریم.
    def strong(t):
        return 'R' if t in ('R', 'D') else 'L'

    n = len(types)
    resolved = list(types)
    i = 0
    # فاصله‌ها و نشانه‌های خنثی پیاپی را یک‌جا پیدا می‌کنیم.
    while i < n:
        if types[i] != 'N':
            i += 1
            continue
        j = i
        while j < n and types[j] == 'N':
            j += 1
        # اگر دو طرف جهت یکسانی دارند، همان جهت را می‌گیریم. در غیر این صورت، جهت پایه را به کار می‌بریم.
        left = strong(types[i - 1]) if i > 0 else base_dir
        right = strong(types[j]) if j < n else base_dir
        d = left if left == right else base_dir
        for k in range(i, j):
            resolved[k] = d
        i = j

    # سطح نمایش تعیین می‌کند کدام بخش‌ها برعکس و کدام بخش‌ها به ترتیب قبلی خوانده شوند.
    levels = []
    for t in resolved:
        if t == 'R':
            levels.append(1)
        else:
            levels.append(2 if base else 0)

    # گروه‌های پشت سر هم با سطح یکسان را در یک بخش قرار می‌دهیم.
    runs = []
    for u, lv in zip(units, levels):
        if runs and runs[-1][0] == lv:
            runs[-1][1].append(u)
        else:
            runs.append([lv, [u]])

    pieces = []
    for lv, us in runs:
        # در بخش راست‌به‌چپ، ترتیب گروه‌ها را برعکس می‌کنیم و پرانتزهای تکی را قرینه می‌کشیم.
        if lv == 1:
            res = []
            for u in reversed(us):
                if len(u) == 1:
                    u = [_MIRROR.get(u[0], u[0])]
                res.extend(u)
            pieces.append(''.join(res))
        else:
            pieces.append(''.join(''.join(u) for u in us))

    # اگر جهت پایه راست‌به‌چپ باشد، ترتیب خود بخش‌ها را هم برمی‌گردانیم.
    if base:
        pieces.reverse()
    return ''.join(pieces)


# ابتدا از کتابخانه‌های شکل‌دهی و نمایش متن استفاده می‌کنیم و در صورت خطا روش داخلی را به کار می‌گیریم.
def _fa_core(text):
    try:
        try:
            import arabic_reshaper
            # تابع نمایش را از یکی از دو مسیر سازگار با نسخه‌های مختلف کتابخانه می‌خوانیم.
            try:
                from bidi import get_display
            except Exception:
                from bidi.algorithm import get_display
            reshaped = arabic_reshaper.reshape(text)
            # جهت متن را از اولین حرف منطبق با الگوی راست‌به‌چپ یا اولین حرف لاتین مشخص می‌کنیم.
            first = next((c for c in text if _RTL_RE.search(c) or (c.isalpha() and c.isascii())), 'a')
            direction = 'R' if _RTL_RE.search(first) else 'L'
            try:
                return get_display(reshaped, base_dir=direction)
            # اگر نسخهٔ نصب‌شده جهت پایه را نپذیرد، همان تابع را با تنظیمات پیش‌فرض اجرا می‌کنیم.
            except TypeError:
                return get_display(reshaped)
        except Exception:
            pass
        # در نبود کتابخانه‌ها، حروف را با توابع همین فایل به هم وصل و برای نمایش مرتب می‌کنیم.
        return _bidi(_reshape(text))
    except Exception:
        return text


def fa(text):
    """حروف فارسی را برای نمایش به هم وصل و مرتب می‌کند و نشانه‌های نامرئی را از متن نمایشی برمی‌دارد."""
    # متنی که نویسهٔ راست‌به‌چپ ندارد به شکل اولیه برمی‌گردد.
    if not has_rtl(text):
        return text
    return _INVISIBLE_RE.sub('', _fa_core(text))


# هر بخش از مسیر فایل را جداگانه برای نمایش آماده می‌کنیم تا جای جداکننده‌ها حفظ شود.
def fa_path(path):
    try:
        return ''.join(fa(p) for p in re.split(r'([/\\])', path))
    except Exception:
        return path


def _esc(s):
    """نویسه‌های ویژه را برای نمایش به‌صورت متن عادی در کیوی آماده می‌کند."""
    # علامت‌های ویژه را طوری می‌نویسیم که کیوی آن‌ها را جزئی از نام فایل نمایش دهد.
    return s.replace('&', '&amp;').replace('[', '&bl;').replace(']', '&br;')


def fa_markup(text):
    """متن حاوی حروف فارسی و لاتین را با نشانه‌گذاری قلم مناسب هر بخش آماده می‌کند."""
    if not text:
        return text
    if not has_rtl(text):
        return _esc(text)
    shown = fa(text)
    # مسیر هر دو قلم را پیدا می‌کنیم تا پسوند لاتین در کنار نام فارسی خوانا بماند.
    fa_f, lat_f = get_rtl_font(), get_latin_font()
    if not fa_f or not lat_f:
        return _esc(shown)
    runs = []
    # نویسه‌های کنار هم را که به یک قلم نیاز دارند در یک گروه قرار می‌دهیم.
    for ch in shown:
        is_fa = bool(_RTL_RE.search(ch))
        if runs and runs[-1][0] == is_fa:
            runs[-1][1].append(ch)
        else:
            runs.append([is_fa, [ch]])
    out = []
    # برای هر گروه، برچسب قلم همان گروه را می‌سازیم.
    for is_fa, chs in runs:
        out.append('[font=%s]%s[/font]' % (fa_f if is_fa else lat_f, _esc(''.join(chs))))
    return ''.join(out)


# هر پوشه و نام فایل را با قلم مناسب خودش نمایش می‌دهیم و جداکننده‌ها را نگه می‌داریم.
def fa_markup_path(path):
    try:
        return ''.join(fa_markup(p) for p in re.split(r'([/\\])', path))
    except Exception:
        return _esc(path)


# حجم فایل را از بایت به واحد مناسب برای نمایش تبدیل می‌کنیم.
def fmt_size(b):
    if b < 1024:
        return '%d B' % b
    # در هر مرحله مقدار را بر ۱۰۲۴ تقسیم می‌کنیم و واحد نمایش را یک پله بزرگ‌تر می‌گیریم.
    # B = Byte
    # KB = Kilobyte
    # MB = Megabyte
    # GB = Gigabyte
    b = b / 1024.0
    for unit in ('KB', 'MB', 'GB'):
        if b < 1024 or unit == 'GB':
            return '%.1f %s' % (b, unit)
        b /= 1024.0


# رنگ‌های رابط کاربری را برای دو حالت تیره و روشن یک‌جا نگه می‌داریم.
THEMES = {
    'dark': {
        # هر رنگ RGBA چهار مؤلفه از صفر تا یک دارد. مؤلفهٔ آخر میزان کدر بودن رنگ را تعیین می‌کند.
        # RGBA = Red, Green, Blue, Alpha
        'bg':                    (0.055, 0.06, 0.08, 1),
        'card_bg':               (0.10, 0.11, 0.14, 1),
        'card_border':           (0.18, 0.20, 0.25, 1),
        'text_primary':          (1.0, 1.0, 1.0, 1.0),
        'text_secondary':        (0.55, 0.58, 0.65, 1),
        'input_bg':              (0.09, 0.10, 0.13, 1),
        'input_border':          (0.18, 0.20, 0.25, 1),
        'mode_card_bg':          (0.09, 0.10, 0.13, 1),
        'mode_card_border':      (0.15, 0.17, 0.22, 1),
        'segmented_inactive':    (0.62, 0.65, 0.72, 1),
        'button_disabled':       (0.22, 0.23, 0.28, 1),
        'ring_color1':           (0.25, 0.25, 0.30, 0.8),
        'ring_color2':           (0.25, 0.25, 0.30, 0.5),
        'play_icon':             (1, 1, 1, 0.85),
        'accent':                (0.55, 0.56, 1.0, 1),
        'slider_track':          (0.20, 0.22, 0.28, 1),
        'slider_ring':           (0.92, 0.92, 1.0, 1),
        'row_bg':                (0.135, 0.145, 0.185, 1),
        'row_press':             (0.18, 0.19, 0.25, 1),
        'row_sel':               (0.19, 0.20, 0.38, 1),
        'folder':                (1.00, 0.76, 0.28, 1),
        'audio':                 (0.20, 0.82, 0.60, 1),
        'good':                  (0.06, 0.72, 0.51, 1),
    },
    # در حالت روشن، پس‌زمینه روشن و متن اصلی تیره است.
    'light': {
        'bg':                    (0.96, 0.96, 0.97, 1),
        'card_bg':               (1.00, 1.00, 1.00, 1),
        'card_border':           (0.88, 0.89, 0.92, 1),
        'text_primary':          (0.0, 0.0, 0.0, 1.0),
        'text_secondary':        (0.42, 0.45, 0.52, 1),
        'input_bg':              (0.97, 0.97, 0.98, 1),
        'input_border':          (0.85, 0.86, 0.88, 1),
        'mode_card_bg':          (0.94, 0.94, 0.95, 1),
        'mode_card_border':      (0.85, 0.86, 0.88, 1),
        'segmented_inactive':    (0.35, 0.38, 0.45, 1),
        'button_disabled':       (0.75, 0.76, 0.80, 1),
        'ring_color1':           (0.55, 0.58, 0.65, 0.9),
        'ring_color2':           (0.55, 0.58, 0.65, 0.6),
        'play_icon':             (0.15, 0.18, 0.25, 0.85),
        'accent':                (0.31, 0.32, 0.82, 1),
        'slider_track':          (0.89, 0.89, 0.96, 1),
        'slider_ring':           (1.0, 1.0, 1.0, 1),
        'row_bg':                (0.955, 0.955, 0.97, 1),
        'row_press':             (0.90, 0.90, 0.94, 1),
        'row_sel':               (0.87, 0.88, 1.0, 1),
        'folder':                (0.95, 0.62, 0.05, 1),
        'audio':                 (0.04, 0.62, 0.43, 1),
        'good':                  (0.06, 0.72, 0.51, 1),
    }
}


# این کلید بین ظاهر تیره و روشن جابه‌جا می‌شود.
class ThemeSwitch(Widget):
    is_dark = BooleanProperty(True)
    knob_pos = NumericProperty(0.0)

    # مسیر حرکت، دستهٔ دایره‌ای و سایهٔ زیر دسته را می‌سازیم.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            self._track_color = Color(0.18, 0.22, 0.32, 1)
            self._track = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height / 2])
            self._shadow_color = Color(0, 0, 0, 0.30)
            self._shadow = Ellipse()
            self._knob_color = Color(0.95, 0.95, 1.0, 1)
            self._knob = Ellipse()

        # تغییر اندازهٔ کلید یا موقعیت دسته، بخش مربوط به همان تغییر را دوباره رسم می‌کند.
        self.bind(
            pos=self._update, size=self._update,
            knob_pos=self._update_knob, is_dark=self._update_colors
        )
        self._update()
        self._update_knob()
        self._update_colors()

    # با تغییر اندازهٔ کلید، گوشه‌های مسیر را به اندازهٔ نصف ارتفاع گرد می‌کنیم.
    def _update(self, *args):
        self._track.pos = self.pos
        self._track.size = self.size
        self._track.radius = [self.height / 2]
        self._update_knob()

    # دسته را با فاصله‌ای یکسان از لبه‌های بالا و پایین قرار می‌دهیم.
    def _update_knob(self, *args):
        pad = dp(4)
        knob_size = self.height - pad * 2
        left_x = self.x + pad
        right_x = self.right - pad - knob_size
        # جای دسته بین دو انتهای مسیر به‌تدریج تغییر می‌کند.
        # x = left_x + (right_x - left_x) × knob_pos
        knob_x = left_x + (right_x - left_x) * self.knob_pos

        self._knob.pos = (knob_x, self.y + pad)
        self._knob.size = (knob_size, knob_size)
        self._shadow.pos = (knob_x, self.y + pad - dp(1.5))
        self._shadow.size = (knob_size, knob_size)

    # برای هر حالت، رنگ مسیر، دسته و سایه را با هم تنظیم می‌کنیم.
    def _update_colors(self, *args):
        if self.is_dark:
            self._track_color.rgba = (0.18, 0.22, 0.32, 1)
            self._knob_color.rgba = (0.95, 0.95, 1.00, 1)
            self._shadow_color.rgba = (0, 0, 0, 0.30)
        else:
            self._track_color.rgba = (0.55, 0.75, 1.00, 1)
            self._knob_color.rgba = (1.00, 0.85, 0.20, 1)
            self._shadow_color.rgba = (0, 0, 0, 0.15)

    # اگر کاربر خود کلید را لمس کند، حالت را عوض می‌کنیم و دسته را در یک‌چهارم ثانیه حرکت می‌دهیم.
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            target = 1.0 if self.is_dark else 0.0
            self.is_dark = not self.is_dark
            Animation(knob_pos=target, d=0.25, t='out_cubic').start(self)
            return True
        return super().on_touch_down(touch)


# کارت، اجزای مرتبط را داخل یک کادر با گوشه‌های گرد قرار می‌دهد.
class Card(BoxLayout):
    bg_color = ListProperty([0.10, 0.11, 0.14, 1])
    border_color = ListProperty([0.18, 0.20, 0.25, 1])
    radius = NumericProperty(dp(20))

    # ابتدا زمینه و حاشیه را می‌کشیم تا محتوای کارت روی آن‌ها دیده شود.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_color = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color = Color(*self.border_color)
            self._border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1)
        self.bind(pos=self._update, size=self._update, bg_color=self._update, border_color=self._update,
                  radius=self._update)

    # با حرکت یا تغییر اندازهٔ کارت، زمینه و خط دور آن را هم تنظیم می‌کنیم.
    def _update(self, *args):
        self._bg_color.rgba = self.bg_color
        self._border_color.rgba = self.border_color
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]
        self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


# این دکمه برای حالت‌های عادی، فشرده و غیرفعال رنگ جداگانه دارد.
class ModernButton(Button):
    bg_color = ListProperty([0.39, 0.40, 0.95, 1])
    pressed_color = ListProperty([0.30, 0.31, 0.80, 1])
    disabled_color = ListProperty([0.22, 0.23, 0.28, 1])
    radius = NumericProperty(dp(16))

    # رنگ عادی متن را نگه می‌داریم تا پس از فعال شدن دوبارهٔ دکمه برگردد.
    def __init__(self, **kwargs):
        if 'color' not in kwargs:
            kwargs['color'] = (1, 1, 1, 1)
        self._normal_text_color = kwargs['color']
        super().__init__(**kwargs)

        # تصویر پیش‌فرض دکمه را کنار می‌گذاریم تا زمینهٔ گردی که می‌کشیم دیده شود.
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            self._color_instr = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        self.bind(pos=self._update, size=self._update, bg_color=self._update_color,
                  pressed_color=self._update_color, state=self._update_color,
                  disabled=self._update_color, disabled_color=self._update_color)
        self._update_color()

    # اندازه و موقعیت زمینه را با خود دکمه هماهنگ می‌کنیم.
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]

    # هنگام غیرفعال شدن، متن کم‌رنگ می‌شود. هنگام فشردن، رنگ زمینه تغییر می‌کند.
    def _update_color(self, *args):
        if self.disabled:
            self._color_instr.rgba = self.disabled_color
            self.color = (self._normal_text_color[0], self._normal_text_color[1], self._normal_text_color[2], 0.4)
        elif self.state == 'down':
            self._color_instr.rgba = self.pressed_color
            self.color = self._normal_text_color
        else:
            self._color_instr.rgba = self.bg_color
            self.color = self._normal_text_color


# این دکمه در ردیف انتخاب حالت نشان می‌دهد کدام روش پردازش انتخاب شده است.
class SegmentedToggleButton(ToggleButton):
    active_color = ListProperty([0.39, 0.40, 0.95, 1])
    inactive_text_color = ListProperty([0.62, 0.65, 0.72, 1])
    radius = NumericProperty(dp(14))

    # زمینهٔ سفارشی را می‌سازیم و رنگ آن را به وضعیت انتخاب متصل می‌کنیم.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._color_instr = Color(0, 0, 0, 0)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update, size=self._update, state=self._update_color,
                  active_color=self._update_color, inactive_text_color=self._update_color)
        self._update_color()

    # زمینه را روی مستطیل دکمه تنظیم می‌کنیم.
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]

    # گزینهٔ انتخاب‌شده زمینهٔ رنگی دارد و گزینهٔ دیگر فقط با رنگ متن مشخص می‌شود.
    def _update_color(self, *args):
        if self.state == 'down':
            self._color_instr.rgba = self.active_color
            self.color = (1, 1, 1, 1)
        else:
            self._color_instr.rgba = (0, 0, 0, 0)
            self.color = self.inactive_text_color


# کادر ورود متن را با زمینه، حاشیه و رنگ انتخاب سفارشی تعریف می‌کنیم.
class ModernTextInput(TextInput):
    radius = NumericProperty(dp(14))
    bg_color = ListProperty([0.09, 0.10, 0.13, 1])
    border_color = ListProperty([0.18, 0.20, 0.25, 1])

    # اگر رنگی از بیرون داده نشده باشد، برای متن، راهنما و نشانگر رنگ سفید می‌گذاریم.
    def __init__(self, **kwargs):
        if 'foreground_color' not in kwargs:
            kwargs['foreground_color'] = (1, 1, 1, 1)
        if 'hint_text_color' not in kwargs:
            kwargs['hint_text_color'] = (1, 1, 1, 1)
        if 'cursor_color' not in kwargs:
            kwargs['cursor_color'] = (1, 1, 1, 1)

        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        self.selection_color = (0.39, 0.40, 0.95, 0.5)

        # حاشیه را جدا از زمینه می‌کشیم تا رنگ هرکدام به‌تنهایی قابل تغییر باشد.
        with self.canvas.before:
            self._bg_color = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color = Color(*self.border_color)
            self._border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.2)

        self.bind(pos=self._update, size=self._update,
                  bg_color=self._update, border_color=self._update)

    # پس از جابه‌جایی کادر، جای زمینه و چهار ضلع حاشیه را به‌روز می‌کنیم.
    def _update(self, *args):
        self._bg_color.rgba = self.bg_color
        self._border_color.rgba = self.border_color
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


class IconView(Widget):
    """نمادها را با خط‌ها و شکل‌های سادهٔ کیوی رسم می‌کند."""
    kind = StringProperty('folder')
    color = ListProperty([1, 1, 1, 1])

    # تغییر اندازه یا نوع نماد باعث می‌شود طرح آن دوباره رسم شود.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, kind=self._draw, color=self._draw)
        self._draw()

    # طرح قبلی را پاک می‌کنیم و نماد موردنیاز را در مرکز فضای موجود می‌کشیم.
    def _draw(self, *args):
        self.canvas.clear()
        s = min(self.width, self.height)
        if s <= 0:
            return
        # طرح پایه ۲۴ واحد دارد. هر واحد برابر ضلع کوتاه‌تر کادر تقسیم بر ۲۴ است.
        u = s / 24.0
        cx, cy = self.center
        lw = max(dp(1.3), u * 2.0)
        k = self.kind
        with self.canvas:
            Color(*self.color)
            # بدنه و زبانهٔ پوشه را با دو مستطیل گرد می‌کشیم.
            if k == 'folder':
                RoundedRectangle(pos=(cx - 10 * u, cy - 7 * u), size=(20 * u, 13 * u), radius=[2.5 * u])
                RoundedRectangle(pos=(cx - 10 * u, cy + 3 * u), size=(9 * u, 5 * u), radius=[1.8 * u])
            # برای نماد صدا، پنج میله با ارتفاع‌های مختلف را در کنار هم قرار می‌دهیم.
            elif k == 'audio':
                heights = (8, 15, 11, 18, 7)
                bw, gap = 2.8 * u, 1.6 * u
                x = cx - (5 * bw + 4 * gap) / 2
                for h in heights:
                    RoundedRectangle(pos=(x, cy - h * u / 2), size=(bw, h * u), radius=[bw / 2])
                    x += bw + gap
            # برای نماد موج، ارتفاع هر نقطه را از یک تابع سینوسی می‌گیریم.
            elif k == 'wave':
                pts = []
                for i in range(25):
                    t = i / 24.0
                    pts.extend([cx - 10 * u + 20 * u * t, cy + math.sin(t * math.pi * 3) * 5.5 * u])
                Line(points=pts, width=lw, cap='round', joint='round')
            # ذره‌بین از یک دایره برای عدسی و یک خط مورب برای دسته ساخته می‌شود.
            elif k == 'search':
                Line(circle=(cx - 2 * u, cy + 2 * u, 6.5 * u), width=lw)
                Line(points=[cx + 2.8 * u, cy - 2.8 * u, cx + 8.5 * u, cy - 8.5 * u], width=lw, cap='round')
            elif k == 'close':
                Line(points=[cx - 6 * u, cy - 6 * u, cx + 6 * u, cy + 6 * u], width=lw, cap='round')
                Line(points=[cx - 6 * u, cy + 6 * u, cx + 6 * u, cy - 6 * u], width=lw, cap='round')
            # پیکان رو به بالا مسیر رفتن به پوشهٔ بالاتر را نشان می‌دهد.
            elif k == 'up':
                Line(points=[cx, cy - 7 * u, cx, cy + 7 * u], width=lw, cap='round')
                Line(points=[cx - 6 * u, cy + 1 * u, cx, cy + 7 * u, cx + 6 * u, cy + 1 * u],
                     width=lw, cap='round', joint='round')
            elif k == 'check':
                Line(points=[cx - 7 * u, cy, cx - 2.5 * u, cy - 5 * u, cx + 7 * u, cy + 6 * u],
                     width=lw * 1.1, cap='round', joint='round')
            elif k == 'chevron':
                Line(points=[cx - 3 * u, cy + 6 * u, cx + 3 * u, cy, cx - 3 * u, cy - 6 * u],
                     width=lw, cap='round', joint='round')
            # برای فایل ویدئویی، یک مثلث پخش داخل قاب قرار می‌دهیم.
            elif k == 'video':
                Line(rounded_rectangle=(cx - 10 * u, cy - 8 * u, 20 * u, 16 * u, 3 * u), width=lw)
                Triangle(points=[cx - 3 * u, cy - 4.5 * u, cx - 3 * u, cy + 4.5 * u, cx + 5 * u, cy])
            elif k == 'image':
                Line(rounded_rectangle=(cx - 10 * u, cy - 9 * u, 20 * u, 18 * u, 3 * u), width=lw)
                Ellipse(pos=(cx - 6 * u, cy + 1.5 * u), size=(4.5 * u, 4.5 * u))
                Line(points=[cx - 7 * u, cy - 6 * u, cx - 2 * u, cy - 1 * u, cx + 1 * u, cy - 4 * u,
                             cx + 4 * u, cy, cx + 8 * u, cy - 5 * u], width=lw * 0.8, cap='round', joint='round')
            # برای چند نوع سند، ابتدا شکل مشترک یک برگه با گوشهٔ تاخورده را می‌کشیم.
            elif k in ('file', 'pdf', 'doc', 'sheet', 'slides', 'text'):
                Line(points=[cx + 2 * u, cy + 11 * u, cx - 8 * u, cy + 11 * u, cx - 8 * u, cy - 11 * u,
                             cx + 8 * u, cy - 11 * u, cx + 8 * u, cy + 5 * u],
                     close=False, width=lw * 0.85, cap='round', joint='round')
                Line(points=[cx + 2 * u, cy + 11 * u, cx + 8 * u, cy + 5 * u, cx + 2 * u, cy + 5 * u],
                     close=True, width=lw * 0.85, joint='round')
                thin = lw * 0.65
                # نشانهٔ داخل برگه مشخص می‌کند فایل چه نوع سندی است.
                if k == 'pdf':
                    RoundedRectangle(pos=(cx - 5 * u, cy - 7 * u), size=(10 * u, 7 * u), radius=[1.5 * u])
                elif k == 'doc':
                    for dy in (0.5, -3.5, -7):
                        Line(points=[cx - 4.5 * u, cy + dy * u, cx + 4.5 * u, cy + dy * u], width=thin, cap='round')
                elif k == 'text':
                    for dy, end in ((-1, 4.5), (-6, 1)):
                        Line(points=[cx - 4.5 * u, cy + dy * u, cx + end * u, cy + dy * u], width=thin, cap='round')
                elif k == 'sheet':
                    Line(rectangle=(cx - 5 * u, cy - 7.5 * u, 10 * u, 9 * u), width=thin)
                    Line(points=[cx - 5 * u, cy - 3 * u, cx + 5 * u, cy - 3 * u], width=thin)
                    Line(points=[cx, cy - 7.5 * u, cx, cy + 1.5 * u], width=thin)
                elif k == 'slides':
                    for dx, h in ((-4.5, 4), (-1.2, 8), (2.1, 6)):
                        Rectangle(pos=(cx + dx * u, cy - 7.5 * u), size=(2.4 * u, h * u))
            # برای فایل کد، دو نشانهٔ زاویه‌دار و یک خط مورب می‌کشیم.
            elif k == 'code':
                Line(points=[cx - 4 * u, cy + 6 * u, cx - 10 * u, cy, cx - 4 * u, cy - 6 * u],
                     width=lw, cap='round', joint='round')
                Line(points=[cx + 4 * u, cy + 6 * u, cx + 10 * u, cy, cx + 4 * u, cy - 6 * u],
                     width=lw, cap='round', joint='round')
                Line(points=[cx - 1.8 * u, cy - 7 * u, cx + 1.8 * u, cy + 7 * u], width=lw * 0.8, cap='round')
            # دندانه‌های زیپ را یکی در میان در دو طرف قرار می‌دهیم تا فایل فشرده مشخص باشد.
            elif k == 'archive':
                Line(rounded_rectangle=(cx - 9 * u, cy - 10 * u, 18 * u, 20 * u, 3 * u), width=lw)
                for i in range(4):
                    Rectangle(pos=(cx - (2.4 if i % 2 == 0 else 0) * u, cy + (7 - 3 * i) * u),
                              size=(2.4 * u, 2.4 * u))
                Line(rounded_rectangle=(cx - 2.4 * u, cy - 7 * u, 4.8 * u, 5 * u, 1.2 * u), width=lw * 0.65)
            # بستهٔ برنامه را با چهار کاشی و حالت خالی را با خطی داخل یک قاب نمایش می‌دهیم.
            elif k == 'apk':
                for dx, dy in ((-9, 1), (1, 1), (-9, -9), (1, -9)):
                    RoundedRectangle(pos=(cx + dx * u, cy + dy * u), size=(8 * u, 8 * u), radius=[2 * u])
            elif k == 'empty':
                Line(rounded_rectangle=(cx - 9 * u, cy - 8 * u, 18 * u, 16 * u, 3 * u), width=lw)
                Line(points=[cx - 4 * u, cy, cx + 4 * u, cy], width=lw, cap='round')


class IconBadge(AnchorLayout):
    """نماد را درون زمینه‌ای کم‌رنگ با گوشه‌های گرد قرار می‌دهد."""
    kind = StringProperty('folder')
    tint = ListProperty([0.5, 0.5, 1, 1])

    # نماد را در مرکز زمینهٔ کم‌رنگی قرار می‌دهیم که از رنگ همان نماد گرفته شده است.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._c = Color(self.tint[0], self.tint[1], self.tint[2], 0.18)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self._ic = IconView(kind=self.kind, color=self.tint, size_hint=(None, None),
                            size=(dp(22), dp(22)))
        self.add_widget(self._ic)
        self.bind(pos=self._upd, size=self._upd)

    # با تغییر چیدمان، اندازه و موقعیت زمینهٔ نماد را تنظیم می‌کنیم.
    def _upd(self, *args):
        self._r.pos = self.pos
        self._r.size = self.size


# این دکمه فرمان خود را با یک نماد نشان می‌دهد.
class IconButton(ButtonBehavior, AnchorLayout):
    bg_color = ListProperty([0.1, 0.1, 0.1, 1])
    pressed_color = ListProperty([0.2, 0.2, 0.2, 1])
    icon_color = ListProperty([1, 1, 1, 1])
    icon = StringProperty('close')
    radius = NumericProperty(dp(14))
    icon_size = NumericProperty(dp(20))

    # زمینه و نماد را جدا می‌سازیم تا هنگام لمس بتوانیم رنگ هرکدام را تغییر دهیم.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._c = Color(*self.bg_color)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self._icon = IconView(kind=self.icon, color=self.icon_color, size_hint=(None, None),
                              size=(self.icon_size, self.icon_size))
        self.add_widget(self._icon)
        self.bind(pos=self._geo, size=self._geo, radius=self._geo,
                  bg_color=self._col, pressed_color=self._col, state=self._col,
                  disabled=self._col, icon=self._col, icon_color=self._col)
        self._col()

    # قاب گرد را با موقعیت و اندازهٔ دکمه هماهنگ می‌کنیم.
    def _geo(self, *args):
        self._r.pos = self.pos
        self._r.size = self.size
        self._r.radius = [self.radius]

    # در حالت فشرده رنگ زمینه و در حالت غیرفعال میزان کدر بودن کل دکمه تغییر می‌کند.
    def _col(self, *args):
        self._c.rgba = self.pressed_color if self.state == 'down' else self.bg_color
        self._icon.kind = self.icon
        self._icon.color = self.icon_color
        self.opacity = 0.35 if self.disabled else 1.0


class ListRow(ButtonBehavior, BoxLayout):
    """نام فایل یا پوشه را همراه نماد و توضیح اختیاری آن در یک ردیف نشان می‌دهد."""
    selected = BooleanProperty(False)

    # اگر ردیف توضیح تکمیلی داشته باشد، ارتفاع بیشتری برای آن در نظر می‌گیریم.
    def __init__(self, theme, title, subtitle=None, icon='folder', tint=(0.5, 0.5, 1, 1),
                 trailing=None, latin='Roboto', selected=False, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(66) if subtitle else dp(58))
        kwargs.setdefault('padding', [dp(12), dp(8), dp(14), dp(8)])
        kwargs.setdefault('spacing', dp(12))
        super().__init__(**kwargs)
        self.t = theme
        self._fixed_trailing = trailing
        rad = dp(16)
        with self.canvas.before:
            self._c = Color(*theme['row_bg'])
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[rad])
            self._bc = Color(0, 0, 0, 0)
            self._bl = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, rad), width=1.2)

        # نماد نوع فایل را در ابتدای ردیف می‌گذاریم.
        self.add_widget(IconBadge(kind=icon, tint=tint, size_hint=(None, None),
                                  size=(dp(42), dp(42)), pos_hint={'center_y': 0.5}))

        col = BoxLayout(orientation='vertical', spacing=dp(1))
        # اندازهٔ قلم با واحد sp تعیین می‌شود تا مقیاس متن دستگاه هم در نظر گرفته شود.
        # sp = Scale-independent Pixel
        tl = Label(text=title, markup=True, font_name=latin, font_size='15sp',
                   color=theme['text_primary'], halign='left', valign='middle',
                   shorten=True, shorten_from='right')
        tl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], v[1])))
        col.add_widget(tl)
        # توضیح تکمیلی فقط زمانی به زیر عنوان اضافه می‌شود که مقداری داشته باشد.
        if subtitle:
            sl = Label(text=subtitle, markup=True, font_name=latin, font_size='12sp',
                       color=theme['text_secondary'], halign='left', valign='middle',
                       shorten=True, shorten_from='left')
            sl.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], v[1])))
            col.add_widget(sl)
        self.add_widget(col)

        # نماد انتهای ردیف می‌تواند فلش ورود به پوشه یا علامت انتخاب فایل باشد.
        self._trail = IconView(kind=trailing or 'check', color=theme['text_secondary'],
                               size_hint=(None, None), size=(dp(18), dp(18)),
                               pos_hint={'center_y': 0.5})
        self.add_widget(self._trail)

        self.bind(pos=self._geo, size=self._geo, selected=self._apply, state=self._apply)
        self.selected = selected
        self._apply()

    # هنگام تغییر چیدمان، زمینه و حاشیهٔ ردیف را هم‌اندازه می‌کنیم.
    def _geo(self, *args):
        self._r.pos = self.pos
        self._r.size = self.size
        self._bl.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(16))

    # ردیف انتخاب‌شده را با رنگ و حاشیه‌ای مشخص از ردیف‌های دیگر متمایز می‌کنیم.
    def _apply(self, *args):
        t = self.t
        if self.selected:
            self._c.rgba = t['row_sel']
            self._bc.rgba = t['accent']
        elif self.state == 'down':
            self._c.rgba = t['row_press']
            self._bc.rgba = (0, 0, 0, 0)
        else:
            self._c.rgba = t['row_bg']
            self._bc.rgba = (0, 0, 0, 0)
        # نماد ثابت همیشه دیده می‌شود. علامت انتخاب فقط کنار فایل انتخاب‌شده ظاهر می‌شود.
        if self._fixed_trailing:
            self._trail.opacity = 1
        elif self.selected:
            self._trail.kind = 'check'
            self._trail.color = t['accent']
            self._trail.opacity = 1
        else:
            self._trail.opacity = 0


class Sheet(ModalView):
    """پنجره‌ای شناور می‌سازد که محتوا و دکمهٔ بستن را در یک کارت نمایش می‌دهد."""

    # پشت پنجره را تیره می‌کنیم و محتوای آن را داخل یک کارت می‌گذاریم.
    def __init__(self, theme, size_hint=(0.92, 0.8), anchor_y='center', **kwargs):
        super().__init__(size_hint=size_hint, anchor_y=anchor_y, background='',
                         background_color=(0, 0, 0, 0), overlay_color=(0, 0, 0, 0.62), **kwargs)
        self.t = theme
        self.card = Card(orientation='vertical', bg_color=theme['card_bg'],
                         border_color=theme['card_border'], radius=dp(28),
                         padding=[dp(18), dp(16), dp(18), dp(16)], spacing=dp(12))
        self.add_widget(self.card)

    # عنوان و دکمهٔ بستن را در بالای پنجره کنار هم قرار می‌دهیم.
    def add_header(self, title):
        theme = self.t
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))
        lb = Label(text="[b]%s[/b]" % title, markup=True, font_size='20sp',
                   color=theme['text_primary'], halign='left', valign='middle')
        lb.bind(size=lambda i, v: setattr(i, 'text_size', v))
        btn = IconButton(icon='close', size_hint=(None, None), size=(dp(40), dp(40)),
                         radius=dp(20), bg_color=theme['input_bg'],
                         pressed_color=theme['mode_card_border'],
                         icon_color=theme['text_primary'], icon_size=dp(15),
                         pos_hint={'center_y': 0.5})
        # رها کردن دکمهٔ بستن، کاربر را به صفحهٔ زیر پنجره برمی‌گرداند.
        btn.bind(on_release=lambda *a: self.dismiss())
        row.add_widget(lb)
        row.add_widget(btn)
        self.card.add_widget(row)


# مرورگر فایل، پوشه‌ها را نشان می‌دهد و مسیر فایل صوتی انتخاب‌شده را به برنامه می‌دهد.
class FileBrowser(Sheet):
    # پوشهٔ آغازین، محدودهٔ پیمایش و کاری را که پس از انتخاب باید انجام شود دریافت می‌کنیم.
    def __init__(self, theme, start_path, root_path, places, on_pick, **kwargs):
        super().__init__(theme, size_hint=(1, 0.94), anchor_y='bottom', auto_dismiss=False, **kwargs)
        t = self.t
        self.on_pick = on_pick
        self.root_path = root_path
        self.latin = get_latin_font() or 'Roboto'
        # مسیر پوشهٔ فعلی (CWD) را برای پیمایش و جست‌وجو نگه می‌داریم.
        # CWD = Current Working Directory
        self.cwd = start_path
        self.selected = None
        self._sel_row = None
        # با دو شمارهٔ جداگانه تشخیص می‌دهیم که فهرست یا نتایج جست‌وجو هنوز مربوط به درخواست فعلی هستند.
        self._gen = 0
        self._search_token = 0
        self._search_ev = None
        self._ignore_text = False

        card = self.card
        card.padding = [dp(16), dp(14), dp(16), dp(14)]
        card.spacing = dp(10)
        self.add_header("Select audio")

        # نماد ذره‌بین، کادر ورود عبارت و دکمهٔ پاک کردن را در یک ردیف می‌چینیم.
        pill = Card(orientation='horizontal', size_hint_y=None, height=dp(48),
                    padding=[dp(14), 0, dp(6), 0], spacing=dp(8),
                    bg_color=t['input_bg'], border_color=t['input_border'], radius=dp(24))
        s_holder = AnchorLayout(size_hint=(None, 1), width=dp(20))
        s_holder.add_widget(IconView(kind='search', color=t['text_secondary'],
                                     size_hint=(None, None), size=(dp(20), dp(20))))
        pill.add_widget(s_holder)
        self.search = TextInput(
            hint_text="Search files & folders", multiline=False, font_size='15sp',
            background_normal='', background_active='', background_color=(0, 0, 0, 0),
            foreground_color=t['text_primary'], hint_text_color=t['text_secondary'],
            cursor_color=t['accent'], selection_color=(t['accent'][0], t['accent'][1], t['accent'][2], 0.35),
            padding=[0, dp(14), 0, 0])
        pill.add_widget(self.search)
        # دکمهٔ پاک کردن را می‌سازیم و تا زمانی که عبارت جست‌وجو خالی است آن را پنهان می‌کنیم.
        self.btn_clear = IconButton(icon='close', size_hint=(None, None), size=(dp(34), dp(34)),
                                    radius=dp(17), bg_color=(0, 0, 0, 0), pressed_color=t['row_press'],
                                    icon_color=t['text_secondary'], icon_size=dp(13),
                                    pos_hint={'center_y': 0.5})
        self.btn_clear.opacity = 0
        self.btn_clear.disabled = True
        self.btn_clear.bind(on_release=lambda *a: self._set_search_text('', refresh=True))
        pill.add_widget(self.btn_clear)
        card.add_widget(pill)
        # با تغییر متن، زمان‌بندی جست‌وجوی تازه را بررسی می‌کنیم.
        self.search.bind(text=self._on_search_text)

        # میان‌برهای پوشه‌های پرکاربرد را در یک ردیف قابل پیمایش قرار می‌دهیم.
        if places:
            chips_scroll = ScrollView(size_hint_y=None, height=dp(38), do_scroll_y=False,
                                      bar_width=0, scroll_type=['content', 'bars'])
            chips = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=dp(8))
            chips.bind(minimum_width=chips.setter('width'))
            for label, path in places:
                chip = ModernButton(text=label, font_size='13sp', size_hint=(None, 1),
                                    bg_color=t['row_bg'], pressed_color=t['row_press'],
                                    color=t['text_primary'], radius=dp(19))
                chip.texture_update()
                # عرض دکمه را از عرض نوشته و فضای اضافهٔ دو طرف آن به دست می‌آوریم.
                chip.width = chip.texture_size[0] + dp(30)
                # مسیر همین دکمه را نگه می‌داریم تا هر میان‌بر پوشهٔ خودش را باز کند.
                chip.bind(on_release=lambda inst, p=path: self.open_dir(p))
                chips.add_widget(chip)
            chips_scroll.add_widget(chips)
            card.add_widget(chips_scroll)

        # مسیر فعلی را کنار دکمهٔ رفتن به پوشهٔ بالاتر نشان می‌دهیم.
        path_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=dp(10))
        self.btn_up = IconButton(icon='up', size_hint=(None, None), size=(dp(38), dp(38)),
                                 radius=dp(19), bg_color=t['row_bg'], pressed_color=t['row_press'],
                                 icon_color=t['text_primary'], icon_size=dp(16),
                                 pos_hint={'center_y': 0.5})
        self.btn_up.bind(on_release=lambda *a: self.go_up())
        self.path_label = Label(text='', markup=True, font_name=self.latin, font_size='13sp',
                                color=t['text_secondary'], halign='left', valign='middle',
                                shorten=True, shorten_from='left')
        self.path_label.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], v[1])))
        path_row.add_widget(self.btn_up)
        path_row.add_widget(self.path_label)
        card.add_widget(path_row)

        # اگر مجوز ویژهٔ اندروید داده نشده باشد، دکمهٔ رفتن به تنظیمات را نشان می‌دهیم.
        if not has_all_files_access():
            grant = ModernButton(text="Allow access to all files", font_size='13sp',
                                 size_hint_y=None, height=dp(42), bg_color=t['row_bg'],
                                 pressed_color=t['row_press'], color=t['accent'], radius=dp(19))

            # ابتدا مرورگر فایل را می‌بندیم و سپس صفحهٔ مجوزهای اندروید را باز می‌کنیم.
            def ask_access(*args):
                self.dismiss()
                open_all_files_settings()

            grant.bind(on_release=ask_access)
            card.add_widget(grant)

        # فهرست را داخل ناحیهٔ پیمایش می‌گذاریم تا پوشه‌های طولانی هم قابل مرور باشند.
        self.scroll = ScrollView(bar_width=dp(3), bar_color=(t['accent'][0], t['accent'][1], t['accent'][2], 0.8),
                                 bar_inactive_color=(0, 0, 0, 0), scroll_type=['bars', 'content'])
        self.items = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8),
                               padding=[0, 0, 0, dp(6)])
        self.items.bind(minimum_height=self.items.setter('height'))
        self.scroll.add_widget(self.items)
        card.add_widget(self.scroll)

        # نام فایل انتخاب‌شده و دکمهٔ تأیید آن در پایین پنجره قرار می‌گیرند.
        bottom = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(58), spacing=dp(12))
        self.sel_label = Label(text="No file selected", markup=True, font_name=self.latin,
                               font_size='14sp', color=t['text_secondary'], halign='left',
                               valign='middle', shorten=True, shorten_from='right')
        self.sel_label.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], v[1])))
        self.btn_select = ModernButton(text="[b]Select[/b]", markup=True, font_size='16sp',
                                       size_hint=(None, 1), width=dp(130),
                                       bg_color=t['good'], pressed_color=(0.04, 0.55, 0.38, 1),
                                       disabled_color=t['button_disabled'], radius=dp(18))
        # تا پیش از انتخاب یک فایل صوتی، دکمهٔ تأیید غیرفعال می‌ماند.
        self.btn_select.disabled = True
        self.btn_select.bind(on_release=self._confirm)
        bottom.add_widget(self.sel_label)
        bottom.add_widget(self.btn_select)
        card.add_widget(bottom)

        self.open_dir(start_path)

    # بررسی می‌کنیم که والد دیگری وجود داشته باشد و از ریشهٔ تعیین‌شده بالاتر نرویم.
    def _can_go_up(self):
        parent = os.path.dirname(self.cwd.rstrip('/\\')) or ''
        if not parent or os.path.normpath(parent) == os.path.normpath(self.cwd):
            return False
        if self.root_path and os.path.normpath(self.cwd) == os.path.normpath(self.root_path):
            return False
        return True

    # با لمس پیکان، در صورت امکان پوشهٔ بالاتر را باز می‌کنیم.
    def go_up(self):
        if self._can_go_up():
            self.open_dir(os.path.dirname(self.cwd.rstrip('/\\')))

    # هنگام ورود به پوشه، جست‌وجوی قبلی را لغو و مسیر نمایش‌داده‌شده را عوض می‌کنیم.
    def open_dir(self, path):
        self._cancel_search()
        self._set_search_text('')
        self.cwd = path
        self.path_label.text = fa_markup_path(path)
        self.btn_up.disabled = not self._can_go_up()
        entries = self._scan(path)
        # برای پوشهٔ خالی و پوشه‌ای که باز نمی‌شود، دو پیام جدا نشان می‌دهیم.
        if entries is None:
            self._message("Can't open this folder", 'empty')
        elif not entries:
            self._message("This folder is empty", 'empty')
        else:
            self._populate(entries)

    # نام، مسیر و اندازهٔ فایل‌ها را از پوشهٔ فعلی می‌خوانیم.
    def _scan(self, path):
        dirs, files = [], []
        try:
            with os.scandir(path) as it:
                for e in it:
                    # نام‌هایی را که با نقطه شروع می‌شوند از فهرست کنار می‌گذاریم.
                    if e.name.startswith('.'):
                        continue
                    try:
                        if e.is_dir():
                            dirs.append((e.path, e.name, True, 0, None))
                        else:
                            try:
                                # اگر خواندن اندازهٔ فایل ممکن نباشد، همچنان نام آن را با اندازهٔ صفر در فهرست می‌آوریم.
                                size = e.stat().st_size
                            except OSError:
                                size = 0
                            files.append((e.path, e.name, False, size, None))
                    except OSError:
                        continue
        except OSError:
            return None
        # پوشه‌ها و فایل‌ها را جداگانه بر اساس نام مرتب می‌کنیم و پوشه‌ها را اول می‌آوریم.
        dirs.sort(key=lambda x: x[1].lower())
        files.sort(key=lambda x: x[1].lower())
        return dirs + files

    # شمارهٔ فهرست را عوض می‌کنیم تا بارگذاری قدیمی متوقف شود و نمایش به بالای فهرست برگردد.
    def _clear(self):
        self._gen += 1
        self.items.clear_widgets()
        self.scroll.scroll_y = 1

    # برای پیام‌هایی مانند خالی بودن پوشه یا پیدا نشدن نتیجه، یک نماد و یک سطر متن می‌سازیم.
    def _message(self, text, icon='search', term=None):
        self._clear()
        t = self.t
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(170),
                        spacing=dp(10), padding=[0, dp(36), 0, 0])
        holder = AnchorLayout(size_hint_y=None, height=dp(40))
        holder.add_widget(IconView(kind=icon, color=t['text_secondary'],
                                   size_hint=(None, None), size=(dp(34), dp(34))))
        # عبارت جست‌وجو را برای نمایش فارسی و نشانه‌گذاری کیوی آماده می‌کنیم.
        shown = text if term is None else (text + " " + fa_markup(term))
        lb = Label(text=shown if term is not None else _esc(text), markup=True, font_name=self.latin,
                   font_size='14sp', color=t['text_secondary'], halign='center', valign='top')
        lb.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        box.add_widget(holder)
        box.add_widget(lb)
        self.items.add_widget(box)

    # برای اینکه صفحه هنگام ساخت یک فهرست بلند پاسخ‌گو بماند، ردیف‌ها را گروه‌گروه می‌سازیم.
    def _populate(self, entries):
        self._clear()
        gen = self._gen
        it = iter(entries)

        # در هر نوبت حداکثر ۲۰ ردیف می‌سازیم. با تغییر فهرست یا تمام شدن داده‌ها کار پایان می‌یابد.
        def step(dt):
            if gen != self._gen:
                return False
            for _ in range(20):
                try:
                    e = next(it)
                except StopIteration:
                    return False
                self.items.add_widget(self._make_row(e))
            return True

        Clock.schedule_interval(step, 0)

    # هر رکورد را به یک ردیف با نام، نماد و توضیح مناسب تبدیل می‌کنیم.
    def _make_row(self, entry):
        path, name, is_dir, size, parent = entry
        t = self.t
        if is_dir:
            kind, tint = 'folder', t['folder']
        else:
            kind, tint = file_style(name)
            tint = tint or t['audio']
        # در نتایج جست‌وجو مسیر پوشهٔ والد، و در فهرست عادی نوع یا اندازهٔ فایل را نشان می‌دهیم.
        if parent:
            sub = fa_markup_path(parent)
        elif is_dir:
            sub = "Folder"
        else:
            ext = os.path.splitext(name)[1][1:].upper()
            sub = "%s  ·  %s" % (ext, fmt_size(size)) if ext else fmt_size(size)
        row = ListRow(t, fa_markup(name), sub,
                      icon=kind,
                      tint=tint,
                      trailing='chevron' if is_dir else None,
                      latin=self.latin, selected=(path == self.selected))
        if path == self.selected:
            self._sel_row = row
        # هنگام لمس ردیف، مسیر و نوع همان مورد را به تابع انتخاب می‌دهیم.
        row.bind(on_release=lambda r, p=path, d=is_dir: self._tap(r, p, d))
        return row

    # لمس پوشه آن را باز می‌کند و لمس فایل، امکان انتخاب آن را بررسی می‌کند.
    def _tap(self, row, path, is_dir):
        if is_dir:
            self.open_dir(path)
            return
        # اگر پسوند پشتیبانی نشود، انتخاب قبلی و دکمهٔ تأیید را غیرفعال می‌کنیم.
        if not path.lower().endswith(AUDIO_EXT):
            if self._sel_row is not None:
                self._sel_row.selected = False
            self._sel_row = None
            self.selected = None
            self.sel_label.text = "Not a supported audio file"
            self.sel_label.color = self.t['text_secondary']
            self.btn_select.disabled = True
            return
        # علامت فایل قبلی را برمی‌داریم و مسیر فایل جدید را برای پردازش نگه می‌داریم.
        if self._sel_row is not None and self._sel_row is not row:
            self._sel_row.selected = False
        row.selected = True
        self._sel_row = row
        self.selected = path
        self.sel_label.text = fa_markup(os.path.basename(path))
        self.sel_label.color = self.t['text_primary']
        self.btn_select.disabled = False

    # پس از تأیید، پنجره را می‌بندیم و مسیر فایل را با کمی تأخیر به برنامه می‌دهیم.
    def _confirm(self, *args):
        if not self.selected:
            return
        p = self.selected
        self.dismiss()
        Clock.schedule_once(lambda dt: self.on_pick(p), 0.1)

    # هنگام تغییر متن از داخل برنامه، واکنش به تایپ را موقتاً متوقف می‌کنیم تا جست‌وجو تکرار نشود.
    def _set_search_text(self, text, refresh=False):
        self._ignore_text = True
        try:
            self.search.text = text
            self.search.font_name = fa_font(text)
        finally:
            self._ignore_text = False
        self.btn_clear.opacity = 1 if text else 0
        self.btn_clear.disabled = not text
        if refresh:
            self.open_dir(self.cwd)

    # شمارهٔ درخواست را تغییر می‌دهیم تا نتیجهٔ جست‌وجوی قبلی قابل نمایش نباشد.
    def _cancel_search(self):
        self._search_token += 1
        if self._search_ev is not None:
            self._search_ev.cancel()
            self._search_ev = None

    # هنگام تایپ، قلم و دکمهٔ پاک کردن را با متن تازه هماهنگ می‌کنیم.
    def _on_search_text(self, inst, text):
        if self._ignore_text:
            return
        try:
            inst.font_name = fa_font(text)
        except Exception:
            pass
        self.btn_clear.opacity = 1 if text else 0
        self.btn_clear.disabled = not text
        self._cancel_search()
        term = text.strip().lower()
        if not term:
            self.open_dir(self.cwd)
            return
        # از دو نویسه به بعد، ۰٫۳۵ ثانیه صبر می‌کنیم تا برای هر ضربهٔ پیاپی یک جست‌وجو شروع نشود.
        if len(term) >= 2:
            self._search_ev = Clock.schedule_once(lambda dt: self._run_search(term), 0.35)

    # جست‌وجو از پوشهٔ فعلی آغاز می‌شود و هر درخواست شمارهٔ مخصوص خودش را دارد.
    def _run_search(self, term):
        self._search_ev = None
        self._search_token += 1
        token = self._search_token
        self._message("Searching…", 'search')
        base = self.cwd

        # جست‌وجو در پس‌زمینه اجرا می‌شود تا پیمایش صفحه همچنان ممکن باشد.
        def worker():
            results = []
            lock = threading.Lock()
            SKIP_AT_ROOT = {'android', 'lost+found', '$recycle.bin', 'system volume information',
                            '.thumbnails', 'lazylist'}
            # عمق پوشهٔ آغازین صفر است. تا عمق سه را می‌خوانیم و حداکثر صد نتیجه نشان می‌دهیم.
            MAX_DEPTH = 3
            MAX_RESULTS = 100

            # در هر پوشه، نتیجه‌های منطبق و زیرپوشه‌های لازم برای مرحلهٔ بعد را جدا جمع می‌کنیم.
            def scan_directory(path, depth):
                local, subdirs = [], []
                if depth > MAX_DEPTH:
                    return local, subdirs
                try:
                    with os.scandir(path) as it:
                        for entry in it:
                            try:
                                nl = entry.name.lower()
                                # پیوندهای نمادین را دنبال نمی‌کنیم و برخی پوشه‌های سیستمی را در سطح آغازین کنار می‌گذاریم.
                                if entry.is_dir(follow_symlinks=False):
                                    if entry.name.startswith('.'):
                                        continue
                                    if depth == 0 and nl in SKIP_AT_ROOT:
                                        continue
                                    if term in nl:
                                        local.append((entry.path, entry.name, True, 0, path))
                                    subdirs.append((entry.path, depth + 1))
                                # نام فایل را بدون توجه به بزرگی و کوچکی حروف با عبارت جست‌وجو مقایسه می‌کنیم.
                                elif entry.is_file(follow_symlinks=False):
                                    if term in nl and not entry.name.startswith('.'):
                                        try:
                                            size = entry.stat().st_size
                                        except OSError:
                                            size = 0
                                        local.append((entry.path, entry.name, False, size, path))
                            except OSError:
                                continue
                except OSError:
                    pass
                return local, subdirs

            # پوشه‌های هر عمق را با حداکثر هشت رشته می‌خوانیم و سپس به عمق بعدی می‌رویم.
            with ThreadPoolExecutor(max_workers=8) as executor:
                level = [(base, 0)]
                while level and len(results) < MAX_RESULTS and self._search_token == token:
                    next_level = []
                    futures = [executor.submit(scan_directory, p, d) for p, d in level]
                    # هر کار که تمام شود، نتیجه‌های آن را برمی‌داریم و زیرپوشه‌هایش را در صف مرحلهٔ بعد می‌گذاریم.
                    for future in as_completed(futures):
                        try:
                            local, subs = future.result()
                            with lock:
                                results.extend(local)
                                next_level.extend(subs)
                            # وقتی نتیجه کافی داریم، درخواست لغو کارهای باقی‌مانده را می‌دهیم.
                            if len(results) >= MAX_RESULTS:
                                for f in futures:
                                    f.cancel()
                                break
                        except Exception:
                            pass
                    level = next_level
            # تا صد نتیجه را برای نمایش در رشتهٔ اصلی به ساعت کیوی می‌سپاریم.
            final = results[:MAX_RESULTS]
            Clock.schedule_once(lambda dt: self._show_results(term, token, final), 0)

        threading.Thread(target=worker, daemon=True).start()

    # فقط نتیجه‌ای را نمایش می‌دهیم که شمارهٔ آن با آخرین جست‌وجو یکی باشد.
    def _show_results(self, term, token, results):
        if token != self._search_token:
            return
        if not results:
            self._message("No results for", 'search', term=term)
        else:
            self._populate(results)


# نماد تنظیمات را با سه خط و یک دسته روی هر خط رسم می‌کنیم.
class SettingsIcon(Widget):
    icon_color = ListProperty([0.39, 0.40, 0.95, 1])

    # سه خط و سه دایره را یک بار می‌سازیم تا موقع تغییر اندازه فقط جابه‌جا شوند.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._c = Color(*self.icon_color)
            self._lines = [Line(width=dp(1.4), cap='round') for _ in range(3)]
            self._dots = [Ellipse() for _ in range(3)]
        self.bind(pos=self._update, size=self._update, icon_color=self._update)
        self._update()

    # جای هر خط و دسته را به نسبت عرض و ارتفاع نماد تعیین می‌کنیم.
    def _update(self, *args):
        self._c.rgba = self.icon_color
        d = dp(8)
        for line, dot, fy, fx in zip(self._lines, self._dots,
                                     (0.82, 0.50, 0.18), (0.68, 0.30, 0.62)):
            y = self.y + self.height * fy
            line.points = [self.x + dp(1), y, self.right - dp(1), y]
            dot.pos = (self.x + self.width * fx - d / 2, y - d / 2)
            dot.size = (d, d)


# با این لغزنده، کاربر شدت نویز یا قدرت کاهش آن را از صفر تا صد تنظیم می‌کند.
class NoiseSlider(Widget):
    value = NumericProperty(0)
    track_color = ListProperty([0.20, 0.22, 0.28, 1])
    fill_color = ListProperty([0.55, 0.56, 1.0, 1])
    ring_color = ListProperty([0.92, 0.92, 1.0, 1])

    # مقدار اولیه را برای بعد از ساخت مسیر، حلقه و دستهٔ لغزنده نگه می‌داریم.
    def __init__(self, **kwargs):
        initial = kwargs.pop('value', 0)
        super().__init__(**kwargs)
        with self.canvas:
            self._c_track = Color(*self.track_color)
            self._track = RoundedRectangle()
            self._c_fill = Color(*self.fill_color)
            self._fill = RoundedRectangle()
            self._c_shadow = Color(0, 0, 0, 0.18)
            self._shadow = Ellipse()
            self._c_ring = Color(*self.ring_color)
            self._ring = Ellipse()
            self._c_knob = Color(*self.fill_color)
            self._knob = Ellipse()
        # تغییر مقدار، اندازه یا رنگ به تابع رسم لغزنده خبر می‌دهد.
        self.bind(pos=self._redraw, size=self._redraw, value=self._redraw,
                  track_color=self._redraw, fill_color=self._redraw,
                  ring_color=self._redraw)
        self.value = initial
        self._redraw()
        # پس از چیدمان اولیه هم دسته را دوباره رسم می‌کنیم تا جای آن با عرض نهایی هماهنگ شود.
        Clock.schedule_once(self._redraw, 0)
        Clock.schedule_once(self._redraw, 0.1)

    # قطر دسته از ارتفاع کادر و اندازهٔ تعیین‌شده بیشتر نمی‌شود.
    def _knob_d(self):
        return min(self.height, dp(26))

    # برای هر بار رسم، رنگ‌ها و مختصات مسیر و دسته را از وضعیت فعلی می‌خوانیم.
    def _redraw(self, *args):
        self._c_track.rgba = self.track_color
        self._c_fill.rgba = self.fill_color
        self._c_knob.rgba = self.fill_color
        self._c_ring.rgba = self.ring_color

        kd = self._knob_d()
        r = kd / 2
        th = dp(8)
        cy = self.center_y
        x0 = self.x + r
        x1 = self.right - r
        # ابتدا درصد را به نسبت صفر تا یک تبدیل می‌کنیم. سپس به همان نسبت از ابتدای مسیر جلو می‌رویم.
        # frac = clamp(value / 100, 0, 1)
        # kx = x0 + (x1 - x0) × frac
        frac = max(0.0, min(1.0, self.value / 100.0))
        kx = x0 + (x1 - x0) * frac

        # مسیر کامل و بخش پرشده را جدا می‌کشیم تا مقدار انتخابی دیده شود.
        self._track.pos = (self.x, cy - th / 2)
        self._track.size = (self.width, th)
        self._track.radius = [th / 2]
        self._fill.pos = (self.x, cy - th / 2)
        self._fill.size = (max(th, kx - self.x), th)
        self._fill.radius = [th / 2]

        # سایه، حلقه و مرکز رنگی را دور همان نقطه قرار می‌دهیم.
        self._shadow.pos = (kx - r, cy - r - dp(1.5))
        self._shadow.size = (kd, kd)
        self._ring.pos = (kx - r, cy - r)
        self._ring.size = (kd, kd)
        inner = kd * 0.62
        self._knob.pos = (kx - inner / 2, cy - inner / 2)
        self._knob.size = (inner, inner)

    # فاصلهٔ افقی لمس از ابتدای مسیر را به درصد تبدیل می‌کنیم.
    # value = round(100 × clamp((touch.x - x0) / span, 0, 1))
    def _set_from_touch(self, touch):
        r = self._knob_d() / 2
        x0 = self.x + r
        span = max(1.0, self.width - 2 * r)
        self.value = int(round(max(0.0, min(1.0, (touch.x - x0) / span)) * 100))

    # لمس داخل لغزنده را می‌گیریم تا حرکت‌های بعدی همان انگشت را دنبال کنیم.
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._set_from_touch(touch)
            return True
        return super().on_touch_down(touch)

    # هنگام کشیدن دسته، مقدار را از موقعیت تازهٔ انگشت به‌روز می‌کنیم.
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._set_from_touch(touch)
            return True
        return super().on_touch_move(touch)

    # با برداشتن انگشت، پیگیری آن لمس پایان می‌یابد.
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


# دکمهٔ انتخاب نوع نویز را با یک فلش رو به پایین مشخص می‌کنیم.
class DropdownField(ModernButton):
    chevron_color = ListProperty([1, 1, 1, 1])
    border_color = ListProperty([0.18, 0.20, 0.25, 1])

    # حاشیه و فلش را روی زمینهٔ دکمه می‌کشیم و در کنار متن برای فلش جا می‌گذاریم.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'left'
        self.valign = 'middle'
        with self.canvas.after:
            self._b_color = Color(*self.border_color)
            self._b_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.2)
            self._chev_color = Color(*self.chevron_color)
            self._chev = Line(width=dp(1.6), cap='round', joint='round')
        self.bind(pos=self._update_deco, size=self._update_deco,
                  chevron_color=self._update_deco, border_color=self._update_deco)
        self.bind(size=lambda i, v: setattr(i, 'text_size', (v[0] - dp(56), v[1])))
        self._update_deco()

    # با تغییر اندازه، فلش را دوباره نزدیک لبهٔ راست دکمه قرار می‌دهیم.
    def _update_deco(self, *args):
        self._b_color.rgba = self.border_color
        self._b_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
        self._chev_color.rgba = self.chevron_color
        cx = self.right - dp(24)
        cy = self.center_y
        self._chev.points = [cx - dp(5), cy + dp(2.5), cx, cy - dp(2.5), cx + dp(5), cy + dp(2.5)]


# برای دکمهٔ راهنما یک حاشیهٔ دایره‌ای رسم می‌کنیم.
class HelpButton(ModernButton):
    border_color = ListProperty([0.18, 0.20, 0.25, 1])

    # خط دور دکمه را پس از زمینه رسم می‌کنیم تا دیده شود.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            self._hb_color = Color(*self.border_color)
            self._hb_line = Line(circle=(0, 0, 1), width=1.2)
        self.bind(pos=self._update_border, size=self._update_border,
                  border_color=self._update_border)
        self._update_border()

    # شعاع حاشیه برابر نصف ضلع کوتاه‌تر دکمه است.
    def _update_border(self, *args):
        self._hb_color.rgba = self.border_color
        self._hb_line.circle = (self.center_x, self.center_y, min(self.width, self.height) / 2)


# این نمایشگر، پخش فایل خروجی و حرکت موج و حلقه‌ها را در یک کادر نشان می‌دهد.
class AudioVisualizer(Widget):
    NOISE_COLOR   = (1.00, 0.32, 0.62)
    DENOISE_COLOR = (0.30, 0.55, 1.00)
    # برای هماهنگی موج با صدا، در هر ثانیه حدود ۵۰ مقدار از سطح صدا محاسبه می‌کنیم.
    ENV_RATE = 50

    # متغیرهای پخش، زمان حرکت و اجزای رسم را آماده می‌کنیم.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False
        self.mode = 'denoise'
        self.time = 0
        self.sound = None

        # سطح صدا را برای بخش‌های کوتاه فایل نگه می‌داریم تا هنگام پخش، مقدار مناسب را بخوانیم.
        self._env = None
        self._duration = 0.0
        self.sample_rate = 16000
        self._level = 0.0
        self._audio_phase = 0.0
        self._play_clock_start = 0.0

        self._arc_rotation = 0.0
        self._wave_time = 0.0
        self._current_color = list(self.DENOISE_COLOR)

        self.ring1 = None
        self.ring2 = None
        self.wave_shape = None
        self.glow_line = None
        self.core_line = None
        self.inner_line = None

        # دو حلقهٔ بیرونی و یک خط بسته برای موج میانی می‌سازیم.
        with self.canvas:
            self._ring_color1 = Color(1, 1, 1, 0.5)
            self.ring1 = Line(width=1.2)
            self._ring_color2 = Color(1, 1, 1, 0.25)
            self.ring2 = Line(width=1.0)

            self._wave_color = Color(1, 1, 1, 0.3)
            self.wave_shape = Line(close=True)

            # سه خط هم‌مسیر با ضخامت و شفافیت متفاوت، حاشیهٔ نورانی حلقه را می‌سازند.
            self._glow_color  = Color(0.30, 0.55, 1.00, 0.15)
            self.glow_line    = Line(width=10, close=True)

            self._core_color  = Color(0.30, 0.55, 1.00, 0.6)
            self.core_line    = Line(width=5, close=True)

            self._inner_color = Color(0.55, 0.75, 1.00, 1.00)
            self.inner_line   = Line(width=2, close=True)

            # مثلث برای پخش و دو مستطیل برای نشان دادن حالت در حال پخش هستند.
            self.icon_color = Color(1, 1, 1, 0.85)
            self.play_btn_rect1 = Rectangle()
            self.play_btn_rect2 = Rectangle()
            self.play_btn_tri = Line(close=True, joint='round')

        self.bind(pos=self.update_static_geometry, size=self.update_static_geometry)
        # فاصلهٔ هدف بین دو به‌روزرسانی یک‌سی‌ام ثانیه است.
        Clock.schedule_interval(self.update_anim, 1/30)

    # رنگ حلقه‌ها، موج و نشان پخش را با زمینهٔ تیره یا روشن هماهنگ می‌کنیم.
    def set_theme(self, is_dark):
        if is_dark:
            self._ring_color1.rgba = (1, 1, 1, 0.6)
            self._ring_color2.rgba = (1, 1, 1, 0.3)
            self._wave_color.rgba = (1, 1, 1, 0.4)
            self.icon_color.rgba = (1, 1, 1, 0.85)
        else:
            self._ring_color1.rgba = (0, 0, 0, 0.6)
            self._ring_color2.rgba = (0, 0, 0, 0.3)
            self._wave_color.rgba = (0, 0, 0, 0.85)
            self.icon_color.rgba = (0.15, 0.18, 0.25, 0.85)

    # پیش از بارگذاری نتیجهٔ تازه، پخش قبلی را متوقف و منبع صوتی آن را آزاد می‌کنیم.
    def set_sound(self, file_path):
        if self.sound:
            self.sound.stop()
            self.sound.unload()
            self.sound = None
        try:
            self.sound = SoundLoader.load(file_path)
            if self.sound:
                # پخش تکراری را فعال می‌کنیم تا پس از پایان فایل دوباره از ابتدا پخش شود.
                self.sound.loop = True
        except Exception as e:
            print("Sound load error:", e)
        self.is_playing = False
        self.time = 0
        self._level = 0.0
        self.update_static_geometry()

    def set_audio_data(self, samples, sample_rate):
        """تغییرات سطح مؤثر صدا را در طول فایل برای حرکت موج روی صفحه محاسبه می‌کند."""
        # با تقسیم بر ۳۲۷۶۸، دامنهٔ نمونه‌های ۱۶ بیتی را تقریباً به بازهٔ منفی یک تا یک می‌بریم.
        audio = samples.astype(np.float32) / 32768.0
        self.sample_rate = sample_rate
        # مدت فایل از تعداد نمونه‌ها و نرخ نمونه‌برداری آن به دست می‌آید.
        # duration = number_of_samples / sample_rate
        self._duration = len(audio) / float(sample_rate)
        hop = max(1, int(sample_rate / self.ENV_RATE))
        n = len(audio) // hop
        if n < 1:
            self._env = np.zeros(1, dtype=np.float32)
        else:
            # صدا را به قطعه‌های هم‌اندازه تقسیم می‌کنیم و سطح مؤثر هر قطعه را با RMS می‌سنجیم.
            # RMS = Root Mean Square
            # RMS = √(Σ xᵢ² / N)
            # در این فرمول، xᵢ مقدار یک نمونه و N تعداد نمونه‌های همان قطعه است.
            frames = audio[:n * hop].reshape(n, hop)
            rms = np.sqrt(np.mean(frames ** 2, axis=1))
            # صدک ۹۸ را مرجع دامنهٔ تصویر می‌گیریم و نسبت‌ها را بین صفر و یک محدود می‌کنیم.
            ref = max(float(np.percentile(rms, 98)), 1e-4)
            self._env = np.clip(rms / ref, 0, 1).astype(np.float32)
        self._level = 0.0
        self._audio_phase = 0.0

    # ابتدا موقعیت پخش را بر حسب ثانیه از پخش‌کننده می‌گیریم.
    def _get_play_pos(self):
        pos = 0
        try:
            pos = self.sound.get_pos() or 0
        except Exception:
            pass
        # اگر موقعیت مثبت در دسترس نباشد، زمان سپری‌شده را بر مدت فایل پیمانه می‌گیریم تا تکرار پخش هم لحاظ شود.
        if pos <= 0:
            pos = (time.time() - self._play_clock_start) % max(self._duration, 0.001)
        return pos

    # موج وسط را با بلندی بخش در حال پخش می‌کشیم.
    def _update_wave(self, dt):
        cx, cy = self.center
        r = min(self.width, self.height) * 0.25
        if r <= 0:
            return

        target = 0.0
        if self.is_playing and self._env is not None and len(self._env) > 0:
            # زمان پخش ضرب در تعداد اندازه‌گیری‌ها در ثانیه، شمارهٔ مقدار موردنیاز را می‌دهد.
            idx = int(self._get_play_pos() * self.ENV_RATE)
            target = float(self._env[min(idx, len(self._env) - 1)])
        # برای افزایش دامنه ضریب بزرگ‌تری می‌گیریم تا موج سریع‌تر بالا بیاید و آرام‌تر پایین برود.
        # level_new = level_old + k × (target - level_old)
        k = 0.6 if target > self._level else 0.25
        self._level += (target - self._level) * k

        if self.is_playing:
            self._audio_phase += dt * 5.0
        ph = self._audio_phase

        # بخشی از دامنه ثابت است تا موج در سطح صدای پایین هم دیده شود.
        # amp = r × (0.07 + 0.55 × level)
        amp = r * (0.07 + 0.55 * self._level)

        segments = 80
        ys = []
        for i in range(segments + 1):
            # از چپ تا راست، یک پوش سینوسی دامنه را در دو سر موج به صفر می‌رساند.
            t = i / segments
            env = math.sin(t * math.pi)
            # در حالت افزودن نویز دو موج سینوسی و در حالت کاهش نویز یک موج برای تصویر می‌سازیم.
            if self.mode == 'noise':
                y = math.sin(t * 12 + ph * 2.0) * amp
                y += math.sin(t * 30 - ph * 3.0) * (amp * 0.35)
            else:
                y = math.sin(t * 6 + ph) * amp
            ys.append((cx - r + 2 * r * t, y * env))

        # لبهٔ پایین را قرینهٔ لبهٔ بالا می‌کشیم تا شکل بسته شود.
        pts = []
        for x, y in ys:
            pts.extend([x, cy + y])
        for x, y in reversed(ys):
            pts.extend([x, cy - y])
        self.wave_shape.points = pts

    # سرعت چرخش و تغییر شکل حلقه به وضعیت پخش بستگی دارد.
    def update_anim(self, dt):
        speed = 1.2 if self.is_playing else 0.4
        # زاویه را پس از هر دور کامل به بازهٔ یک دور برمی‌گردانیم.
        # angle_new = (angle_old + speed × dt) mod (2π)
        self._arc_rotation = (self._arc_rotation + speed * dt) % (math.pi * 2)

        wave_speed = 4.0 if self.is_playing else 1.5
        self._wave_time += dt * wave_speed

        # رنگ را به‌آرامی به رنگ مخصوص حالت انتخابی نزدیک می‌کنیم.
        target = self.NOISE_COLOR if self.mode == 'noise' else self.DENOISE_COLOR
        lerp = min(1.0, dt * 8.0)
        for i in range(3):
            self._current_color[i] += (target[i] - self._current_color[i]) * lerp

        r, g, b = self._current_color
        self._glow_color.rgba  = (r, g, b, 0.15)
        self._core_color.rgba  = (r, g, b, 0.6)
        # برای روشن‌تر شدن لایهٔ داخلی، هر مؤلفهٔ رنگ را ۳۵ درصد به یک نزدیک می‌کنیم.
        self._inner_color.rgba = (
            r + (1 - r) * 0.35,
            g + (1 - g) * 0.35,
            b + (1 - b) * 0.35,
            1.0,
        )

        self._update_circle()
        self._update_wave(dt)

        # هنگام پخش، زمان حرکت را جلو می‌بریم و پس از توقف، آن را به‌تدریج به صفر می‌رسانیم.
        if self.is_playing or self.time > 0:
            if self.is_playing:
                self.time += dt * 4
            else:
                self.time = max(0, self.time - dt * 5)
            self.redraw_dynamic()

    # اگر فایل صوتی بارگذاری شده باشد، با هر لمس بین پخش و توقف جابه‌جا می‌شویم.
    def toggle_play(self):
        if not self.sound:
            return
        self.is_playing = not self.is_playing
        if self.is_playing:
            # زمان شروع را برای تخمین موقعیت پخش ذخیره می‌کنیم.
            self._play_clock_start = time.time()
            self.sound.play()
        else:
            self.sound.stop()
        self.redraw_dynamic()

    # فقط لمس‌هایی که داخل کادر نمایشگر هستند فرمان پخش یا توقف می‌دهند.
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.toggle_play()
            return True
        return super().on_touch_down(touch)

    # برای حاشیهٔ نورانی، مختصات نقاط یک دایره با شعاع متغیر را محاسبه می‌کنیم.
    def _update_circle(self):
        cx, cy = self.center
        r = min(self.width, self.height) * 0.25
        if r <= 0:
            return

        pts = []
        steps = 180
        wave_freq = 6
        wave_amp = 3.5 if self.is_playing else 1.5

        # یک دور کامل را به ۱۸۰ قسمت تقسیم می‌کنیم. موج سینوسی روی شعاع، لبهٔ حلقه را موج‌دار می‌کند.
        for i in range(steps + 1):
            a = (i / steps) * math.pi * 2
            wave_offset = math.sin(a * wave_freq + self._wave_time) * wave_amp
            curr_r = r + wave_offset
            angle = a + self._arc_rotation
            # شعاع و زاویه را به مختصات صفحه تبدیل می‌کنیم.
            # x = cx + curr_r × cos(angle)
            # y = cy + curr_r × sin(angle)
            x = cx + math.cos(angle) * curr_r
            y = cy + math.sin(angle) * curr_r
            pts.extend([x, y])

        self.glow_line.points = pts
        self.core_line.points = pts
        self.inner_line.points = pts

    # وسط کادر را پیدا می‌کنیم تا نشان پخش با جابه‌جایی یا تغییر اندازه در مرکز بماند.
    def update_static_geometry(self, *args):
        cx, cy = self.center
        if min(self.width, self.height) * 0.25 <= 0:
            return

        # هنگام پخش دو میله و هنگام توقف یک مثلث در وسط نمایشگر می‌گذاریم.
        if self.is_playing:
            self.play_btn_tri.points = []
            self.play_btn_rect1.pos = (cx - 7, cy - 8)
            self.play_btn_rect1.size = (4, 16)
            self.play_btn_rect2.pos = (cx + 3, cy - 8)
            self.play_btn_rect2.size = (4, 16)
        else:
            self.play_btn_rect1.size = (0, 0)
            self.play_btn_rect2.size = (0, 0)
            self.play_btn_tri.points = [cx - 4, cy - 8, cx + 8, cy, cx - 4, cy + 8]

        self._update_circle()
        self.redraw_dynamic()

    # دو حلقهٔ بیرونی را با دامنه و سرعت متفاوت رسم می‌کنیم.
    def redraw_dynamic(self):
        cx, cy = self.center
        r = min(self.width, self.height) * 0.25
        if r <= 0:
            return

        ring1_pts, ring2_pts = [], []
        # برای رسم هر حلقه، زاویه را در گام‌های هشت‌درجه‌ای جلو می‌بریم و آن را به رادیان تبدیل می‌کنیم.
        # radians = degrees × π / 180
        for angle in range(0, 361, 8):
            rad = math.radians(angle)
            if self.is_playing:
                # در حالت افزودن نویز، دامنهٔ نوسان حلقه‌ها را بزرگ‌تر می‌گیریم.
                amp1 = 10 if self.mode == 'noise' else 3
                amp2 = 15 if self.mode == 'noise' else 5
                freq = 0.3 if self.mode == 'noise' else 0.1
                offset1 = math.sin(angle * freq + self.time * 4) * amp1
                offset2 = math.sin(angle * freq * 1.5 - self.time * 3) * amp2
                if self.mode == 'noise':
                    offset1 += math.sin(angle * 0.9 + self.time * 8) * (amp1 * 0.5)
            else:
                offset1, offset2 = 2, 4
            # به شعاع پایه، فاصلهٔ هر حلقه از مرکز موج و جابه‌جایی همان نقطه را اضافه می‌کنیم.
            rr1 = r + 15 + offset1
            rr2 = r + 25 + offset2
            ring1_pts.extend([cx + math.cos(rad) * rr1, cy + math.sin(rad) * rr1])
            ring2_pts.extend([cx + math.cos(rad) * rr2, cy + math.sin(rad) * rr2])
        self.ring1.points = ring1_pts
        self.ring2.points = ring2_pts


        # شکل نشان مرکزی را با وضعیت فعلی پخش هماهنگ می‌کنیم.
        if self.is_playing:
            self.play_btn_tri.points = []
            self.play_btn_rect1.pos = (cx - 7, cy - 8)
            self.play_btn_rect2.pos = (cx + 3, cy - 8)
        else:
            self.play_btn_rect1.size = (0, 0)
            self.play_btn_rect2.size = (0, 0)
            self.play_btn_tri.points = [cx - 4, cy - 8, cx + 8, cy, cx - 4, cy + 8]


# این کلاس صفحهٔ اصلی، انتخاب فایل و دو روش پردازش صدا را به هم وصل می‌کند.
class NoiseAdderApp(App):
    # هنگام ساخت صفحه، عنوان برنامه و حالت تیرهٔ آغازین را تنظیم می‌کنیم.
    def build(self):
        self.title = "Audio Processor"
        self.is_dark_theme = True

        # اجزای صفحه را عمودی می‌چینیم و رنگ زمینه را پشت آن‌ها رسم می‌کنیم.
        root = BoxLayout(orientation='vertical')
        with root.canvas.before:
            root._bg_color = Color(*THEMES['dark']['bg'])
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(root._bg, 'pos', v),
                  size=lambda i, v: setattr(root._bg, 'size', v))

        # بالای صفحه برای عنوان، دکمهٔ راهنما و کلید تغییر ظاهر جا می‌گذاریم.
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(115),
                           padding=[dp(24), dp(38), dp(24), dp(12)], spacing=dp(2))

        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))

        # عنوان را در ردیف بالا قرار می‌دهیم و پهنای متن را با عرض کادر هماهنگ می‌کنیم.
        self.title_label = Label(
            text="[b]Audio Processor[/b]", markup=True, font_size='26sp',
            color=(0.94, 0.95, 0.98, 1), halign='left', valign='middle'
        )
        self.title_label.bind(size=lambda i, v: setattr(i, 'text_size', v))

        # تغییر وضعیت این کلید، رنگ‌های کل صفحه را به‌روز می‌کند.
        self.theme_switch = ThemeSwitch(size_hint=(None, None), size=(dp(62), dp(34)))
        self.theme_switch.bind(is_dark=self._on_theme_switch)

        switch_container = AnchorLayout(size_hint=(None, 1), width=dp(64))
        switch_container.add_widget(self.theme_switch)

        # علامت سؤال، پنجرهٔ راهنمای کار با برنامه را باز می‌کند.
        self.help_btn = HelpButton(text="[b]?[/b]", markup=True, font_size='17sp',
                                   size_hint=(None, None), size=(dp(34), dp(34)),
                                   radius=dp(17))
        self.help_btn.bind(on_release=self.show_help)
        help_container = AnchorLayout(size_hint=(None, 1), width=dp(46))
        help_container.add_widget(self.help_btn)

        top_row.add_widget(self.title_label)
        top_row.add_widget(help_container)
        top_row.add_widget(switch_container)
        header.add_widget(top_row)

        # زیر عنوان، توضیح کوتاهی دربارهٔ دو کار اصلی برنامه می‌نویسیم.
        self.subtitle_label = Label(
            text="Add noise or denoise your audio files", font_size='13sp',
            color=(0.55, 0.58, 0.65, 1), halign='left', valign='top',
            size_hint_y=None, height=dp(20)
        )
        self.subtitle_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        header.add_widget(self.subtitle_label)

        root.add_widget(header)

        # دکمه‌های افزودن و کاهش نویز را کنار هم در یک کارت می‌گذاریم.
        mode_wrapper = BoxLayout(padding=[dp(24), 0, dp(24), dp(16)],
                                 size_hint_y=None, height=dp(76), orientation='vertical')
        self.mode_card = Card(orientation='horizontal', size_hint_y=None, height=dp(58),
                              padding=[dp(6)] * 4, spacing=dp(6),
                              bg_color=(0.09, 0.10, 0.13, 1),
                              border_color=(0.15, 0.17, 0.22, 1))
        # در شروع برنامه، حالت افزودن نویز انتخاب شده است.
        self.btn_mode_noise = SegmentedToggleButton(
            text="Add Noise", group='mode', state='down',
            active_color=(0.06, 0.72, 0.51, 1),
            inactive_text_color=(0.62, 0.65, 0.72, 1),
            font_size='15sp', bold=True
        )
        # دکمهٔ کاهش نویز عضو همان گروه انتخاب است.
        self.btn_mode_denoise = SegmentedToggleButton(
            text="Denoise", group='mode',
            active_color=(0.39, 0.40, 0.95, 1),
            inactive_text_color=(0.62, 0.65, 0.72, 1),
            font_size='15sp', bold=True
        )
        self.mode_card.add_widget(self.btn_mode_noise)
        self.mode_card.add_widget(self.btn_mode_denoise)
        mode_wrapper.add_widget(self.mode_card)
        root.add_widget(mode_wrapper)

        # بخش میانی صفحه را برای پیام وضعیت و نمایش نتیجه در نظر می‌گیریم.
        center_wrapper = BoxLayout(padding=[dp(24), 0, dp(24), dp(18)], size_hint_y=0.72)
        self.center_card = Card(orientation='vertical', padding=[dp(18)] * 4, spacing=dp(12),
                                radius=dp(28))

        # نمایشگر صدا تا زمان آماده شدن اولین نتیجه پنهان می‌ماند.
        self.visualizer = AudioVisualizer(size_hint_y=0, opacity=0)
        self.center_card.add_widget(self.visualizer)

        # در ابتدا، پیام وسط صفحه از کاربر می‌خواهد یک حالت و سپس یک فایل انتخاب کند.
        self.status_label = Label(
            text="Select a mode and add an audio file.",
            font_size='16sp', halign='center', valign='middle',
            color=(0.65, 0.68, 0.75, 1), markup=True, size_hint_y=1
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.center_card.add_widget(self.status_label)

        center_wrapper.add_widget(self.center_card)
        root.add_widget(center_wrapper)

        # نویز سفید، نوع پیش‌فرض برای افزودن به صداست.
        self.noise_kind = 'White noise'
        self.SETTINGS_H = dp(160)

        # کارت افزودن نویز، انتخاب نوع و تنظیم شدت را کنار هم نگه می‌دارد.
        self.settings_wrapper = BoxLayout(padding=[dp(24), 0, dp(24), 0],
                                          size_hint_y=None, height=self.SETTINGS_H)
        self.settings_card = Card(orientation='vertical',
                                  padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(6),
                                  radius=dp(24))

        # نماد تنظیمات را کنار عنوان کارت قرار می‌دهیم.
        title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(10))
        self.settings_icon = SettingsIcon(size_hint=(None, None), size=(dp(26), dp(26)),
                                          pos_hint={'center_y': 0.5})
        icon_holder = AnchorLayout(size_hint_x=None, width=dp(26))
        icon_holder.add_widget(self.settings_icon)
        self.settings_title = Label(text="[b]Noise settings[/b]", markup=True, font_size='17sp',
                                    halign='left', valign='middle')
        self.settings_title.bind(size=lambda i, v: setattr(i, 'text_size', v))
        title_row.add_widget(icon_holder)
        title_row.add_widget(self.settings_title)
        self.settings_card.add_widget(title_row)

        # در این ردیف نوع نویز دیده می‌شود و کاربر می‌تواند فهرست انواع آن را باز کند.
        type_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=dp(10))
        self.noise_type_label = Label(text="Noise type", font_size='14sp', halign='left',
                                      valign='middle', size_hint_x=0.34)
        self.noise_type_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.noise_type_btn = DropdownField(text=self.noise_kind, font_size='15sp',
                                            radius=dp(14), size_hint_x=0.66)
        self.noise_type_btn.bind(on_release=self.show_noise_type_picker)
        type_row.add_widget(self.noise_type_label)
        type_row.add_widget(self.noise_type_btn)
        self.settings_card.add_widget(type_row)

        # درصد شدت را در مقابل عنوان نشان می‌دهیم تا هنگام حرکت دسته خوانده شود.
        int_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22))
        self.intensity_label = Label(text="Intensity", font_size='14sp', halign='left', valign='middle')
        self.intensity_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.intensity_value_label = Label(text="0%", markup=False, font_size='16sp', bold=True,
                                           halign='right', valign='middle')
        self.intensity_value_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        int_row.add_widget(self.intensity_label)
        int_row.add_widget(self.intensity_value_label)
        self.settings_card.add_widget(int_row)

        # مقدار اولیه صفر است. با جابه‌جایی لغزنده، درصد کنار آن بلافاصله تغییر می‌کند.
        self.noise_slider = NoiseSlider(size_hint_y=None, height=dp(28), value=0)
        self.noise_slider.bind(
            value=lambda i, v: setattr(self.intensity_value_label, 'text', f"{int(v)}%"))
        self.intensity_value_label.text = f"{int(self.noise_slider.value)}%"
        self.settings_card.add_widget(self.noise_slider)

        self.settings_wrapper.add_widget(self.settings_card)
        root.add_widget(self.settings_wrapper)

        # تنظیمات کاهش نویز کارت جداگانه‌ای دارد که با انتخاب این حالت نمایش داده می‌شود.
        self.denoise_wrapper = BoxLayout(padding=[dp(24), 0, dp(24), 0],
                                         size_hint_y=None, height=self.SETTINGS_H)
        self.denoise_card = Card(orientation='vertical',
                                 padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(6),
                                 radius=dp(24))

        # نماد و عنوان کاهش نویز را در بالای کارت قرار می‌دهیم.
        dn_title_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(10))
        self.denoise_icon = SettingsIcon(size_hint=(None, None), size=(dp(26), dp(26)))
        dn_icon_holder = AnchorLayout(size_hint_x=None, width=dp(26))
        dn_icon_holder.add_widget(self.denoise_icon)
        self.denoise_title = Label(text="[b]Denoise settings[/b]", markup=True, font_size='17sp',
                                   halign='left', valign='middle')
        self.denoise_title.bind(size=lambda i, v: setattr(i, 'text_size', v))
        dn_title_row.add_widget(dn_icon_holder)
        dn_title_row.add_widget(self.denoise_title)
        self.denoise_card.add_widget(dn_title_row)

        # در این حالت برنامه خودش نویز را برآورد می‌کند. این ردیف روش خودکار را نشان می‌دهد.
        dn_type_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=dp(10))
        self.denoise_type_label = Label(text="Noise type", font_size='14sp', halign='left',
                                        valign='middle', size_hint_x=0.34)
        self.denoise_type_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.denoise_auto_card = Card(orientation='horizontal', size_hint_x=0.66,
                                      padding=[dp(16), 0, dp(8), 0], radius=dp(14))
        self.denoise_auto_label = Label(text="Auto (all noise types)", font_size='15sp',
                                        halign='left', valign='middle')
        self.denoise_auto_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.denoise_auto_card.add_widget(self.denoise_auto_label)
        dn_type_row.add_widget(self.denoise_type_label)
        dn_type_row.add_widget(self.denoise_auto_card)
        self.denoise_card.add_widget(dn_type_row)

        # قدرت کاهش نویز را با یک عدد درصدی کنار عنوان نشان می‌دهیم.
        dn_int_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22))
        self.denoise_strength_label = Label(text="Strength", font_size='14sp', halign='left', valign='middle')
        self.denoise_strength_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.denoise_value_label = Label(text="70%", font_size='16sp', bold=True,
                                         halign='right', valign='middle')
        self.denoise_value_label.bind(size=lambda i, v: setattr(i, 'text_size', v))
        dn_int_row.add_widget(self.denoise_strength_label)
        dn_int_row.add_widget(self.denoise_value_label)
        self.denoise_card.add_widget(dn_int_row)

        # قدرت اولیهٔ کاهش نویز ۷۰ درصد است و با حرکت دسته تغییر می‌کند.
        self.denoise_slider = NoiseSlider(size_hint_y=None, height=dp(28), value=70)
        self.denoise_slider.bind(
            value=lambda i, v: setattr(self.denoise_value_label, 'text', f"{int(v)}%"))
        self.denoise_value_label.text = f"{int(self.denoise_slider.value)}%"
        self.denoise_card.add_widget(self.denoise_slider)

        self.denoise_wrapper.add_widget(self.denoise_card)

        # تغییر حالت، کارت تنظیمات مناسب را جایگزین کارت قبلی می‌کند.
        self.btn_mode_noise.bind(state=self._on_mode_change)

        bottom_wrapper = BoxLayout(padding=[dp(24), dp(10), dp(24), dp(30)],
                                   size_hint_y=None, height=dp(100))
        # دکمهٔ پایین صفحه، پنجرهٔ انتخاب فایل را باز می‌کند.
        self.btn_add_file = ModernButton(
            text="[b]ADD AUDIO FILE[/b]", markup=True, font_size='16sp',
            bg_color=(0.39, 0.40, 0.95, 1), pressed_color=(0.28, 0.29, 0.75, 1),
            height=dp(58), radius=dp(20)
        )
        self.btn_add_file.bind(on_press=self.show_file_chooser)
        bottom_wrapper.add_widget(self.btn_add_file)
        root.add_widget(bottom_wrapper)

        # چیدمان کامل را به کیوی می‌دهیم تا صفحهٔ اصلی را نمایش دهد.
        return root

    # با آغاز برنامه، روی اندروید مجوزهای لازم برای دسترسی به فایل‌ها را درخواست می‌کنیم.
    def on_start(self):
        if IS_ANDROID:
            try:
                permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
                # اگر مجوز ویژهٔ خواندن فایل‌های صوتی تعریف شده باشد، آن را هم به درخواست اضافه می‌کنیم.
                if hasattr(Permission, 'READ_MEDIA_AUDIO'):
                    permissions.append(Permission.READ_MEDIA_AUDIO)
                request_permissions(permissions)
            except Exception as e:
                print("Permission error:", e)
        # ظاهر تیره را اعمال می‌کنیم و پس از چیدمان، جای دسته‌های لغزنده را به‌روز می‌کنیم.
        self.apply_theme(True)
        Clock.schedule_once(self._refresh_sliders, 0.3)

    # انتخاب کلید را ذخیره می‌کنیم و همان حالت را روی صفحه اعمال می‌کنیم.
    def _on_theme_switch(self, instance, value):
        self.is_dark_theme = value
        self.apply_theme(value)

    # رنگ بخش‌های صفحه را از جدول حالت روشن یا تیره برمی‌داریم.
    def apply_theme(self, is_dark):
        theme = THEMES['dark'] if is_dark else THEMES['light']

        # زمینه، نوشته‌ها و دکمه‌های قسمت اصلی را با رنگ‌های انتخابی به‌روز می‌کنیم.
        self.root._bg_color.rgba = theme['bg']
        self.title_label.color = theme['text_primary']
        self.subtitle_label.color = theme['text_secondary']
        self.center_card.bg_color = theme['card_bg']
        self.center_card.border_color = theme['card_border']
        self.mode_card.bg_color = theme['mode_card_bg']
        self.mode_card.border_color = theme['mode_card_border']
        self.btn_mode_noise.inactive_text_color = theme['segmented_inactive']
        self.btn_mode_denoise.inactive_text_color = theme['segmented_inactive']
        self.status_label.color = theme['text_secondary']
        self.btn_add_file.disabled_color = theme['button_disabled']
        # رنگ زمینه، حاشیه و علامت سؤال را برای دکمهٔ راهنما تنظیم می‌کنیم.
        self.help_btn.bg_color = theme['mode_card_bg']
        self.help_btn.pressed_color = theme['mode_card_border']
        self.help_btn.border_color = theme['input_border']
        self.help_btn._normal_text_color = theme['accent']
        self.help_btn._update_color()
        # در کارت افزودن نویز، رنگ نوشته‌ها، دکمهٔ انتخاب نوع و لغزنده را هماهنگ می‌کنیم.
        self.settings_card.bg_color = theme['card_bg']
        self.settings_card.border_color = theme['card_border']
        self.settings_title.color = theme['text_primary']
        self.settings_icon.icon_color = theme['accent']
        self.noise_type_label.color = theme['text_secondary']
        self.intensity_label.color = theme['text_secondary']
        self.intensity_value_label.color = theme['accent']
        self.noise_type_btn.bg_color = theme['input_bg']
        self.noise_type_btn.pressed_color = theme['mode_card_border']
        self.noise_type_btn.border_color = theme['input_border']
        self.noise_type_btn.chevron_color = theme['text_primary']
        self.noise_type_btn._normal_text_color = theme['text_primary']
        self.noise_type_btn._update_color()
        self.noise_slider.track_color = theme['slider_track']
        self.noise_slider.fill_color = theme['accent']
        self.noise_slider.ring_color = theme['slider_ring']
        # همین رنگ‌بندی را به کارت کاهش نویز و نمایشگر صدا هم می‌دهیم.
        self.denoise_card.bg_color = theme['card_bg']
        self.denoise_card.border_color = theme['card_border']
        self.denoise_title.color = theme['text_primary']
        self.denoise_icon.icon_color = theme['accent']
        self.denoise_type_label.color = theme['text_secondary']
        self.denoise_strength_label.color = theme['text_secondary']
        self.denoise_value_label.color = theme['accent']
        self.denoise_auto_card.bg_color = theme['input_bg']
        self.denoise_auto_card.border_color = theme['input_border']
        self.denoise_auto_label.color = theme['text_primary']
        self.denoise_slider.track_color = theme['slider_track']
        self.denoise_slider.fill_color = theme['accent']
        self.denoise_slider.ring_color = theme['slider_ring']
        self.visualizer.set_theme(is_dark)

    # این هشت گزینه در فهرست انتخاب نوع نویز نمایش داده می‌شوند. روش ساخت هرکدام در تابع تولید نویز آمده است.
    NOISE_TYPES = [
        'White noise',
        'Gaussian noise',
        'Pink noise',
        'Brown noise',
        'Blue noise',
        'Violet noise',
        'Impulse noise',
        'Hum 50Hz',
    ]

    # برای هر نوع نویز، توضیح کوتاهی دربارهٔ صدایی که ایجاد می‌کند نمایش می‌دهیم.
    NOISE_DESC = {
        'White noise':    'Even hiss across all frequencies',
        'Gaussian noise': 'Natural random hiss',
        'Pink noise':     'Softer hiss, like steady rain',
        'Brown noise':    'Deep rumble, like a waterfall',
        'Blue noise':     'Bright, thin hiss',
        'Violet noise':   'Very sharp, high-pitched hiss',
        'Impulse noise':  'Random crackles and pops',
        'Hum 50Hz':       'Electrical mains buzz',
    }

    # هنگام تغییر حالت، کارت قبلی را برمی‌داریم و کارت مرتبط را بالای دکمهٔ انتخاب فایل می‌گذاریم.
    def _on_mode_change(self, instance, state):
        noise_mode = (state == 'down')
        show = self.settings_wrapper if noise_mode else self.denoise_wrapper
        hide = self.denoise_wrapper if noise_mode else self.settings_wrapper
        if hide.parent is not None:
            hide.parent.remove_widget(hide)
        if show.parent is None:
            show.opacity = 0
            # کارت تازه به‌تدریج ظاهر می‌شود تا تغییر حالت قابل تشخیص باشد.
            self.root.add_widget(show, index=1)
            Animation(opacity=1, d=0.2).start(show)
        Clock.schedule_once(self._refresh_sliders, 0.1)

    # راهنما را در پنجره‌ای جدا روی صفحهٔ فعلی باز می‌کنیم.
    def show_help(self, *args):
        theme = self.get_theme()
        sheet = Sheet(theme, size_hint=(0.92, 0.82))
        sheet.add_header("How it works")

        # راهنما افزودن نویز، کاهش نویز، پخش نتیجه و محل ذخیرهٔ فایل‌ها را توضیح می‌دهد.
        sections = [
            ("Add Noise",
             "Adds noise to your audio file.\n"
             "•  Noise type: White, Gaussian, Pink, Brown, Blue, Violet, Impulse (crackle) or 50 Hz hum.\n"
             "•  Intensity: how loud the noise is compared to your audio. "
             "0% adds nothing, 100% makes the noise as loud as the audio.",
             theme['good']),
            ("Denoise",
             "Removes noise from your audio automatically. It handles every noise "
             "type, so there is nothing to choose.\n"
             "•  Strength: higher removes more noise, but very high values can make "
             "voices sound thin. 60-80% is a good start.",
             theme['accent']),
            ("Playing the result",
             "When processing finishes, tap the circle to play or pause. "
             "The wave inside it follows the sound.",
             theme['folder']),
            ("Where files are saved",
             "Add Noise saves to the Noise folder and Denoise saves to the "
             "Denoised folder, each with a waveform image.",
             (0.30, 0.60, 1.0, 1)),
        ]

        scroll = ScrollView(bar_width=dp(3), bar_color=(*theme['accent'][:3], 0.8),
                            bar_inactive_color=(0, 0, 0, 0))
        col = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        col.bind(minimum_height=col.setter('height'))
        # برای هر بخش راهنما یک کارت می‌سازیم تا نوشته‌ها با پیمایش قابل خواندن باشند.
        for title, body, color in sections:
            sec = Card(orientation='vertical', size_hint_y=None, padding=[dp(16), dp(14), dp(16), dp(14)],
                       bg_color=theme['row_bg'], border_color=theme['row_bg'], radius=dp(18))
            hexc = self._rgb_to_hex(color)
            lbl = Label(text=f"[color={hexc}][b]{title}[/b][/color]\n{body}", markup=True,
                        font_size='14sp', color=theme['text_secondary'],
                        halign='left', valign='top', size_hint_y=None)
            lbl.bind(width=lambda i, w: setattr(i, 'text_size', (w, None)))

            # ارتفاع نوشته و کارت را از ارتفاع واقعی متن می‌گیریم تا سطرهای طولانی جا شوند.
            def fit(inst, ts, card=sec):
                inst.height = ts[1]
                card.height = ts[1] + dp(28)
            lbl.bind(texture_size=fit)
            sec.add_widget(lbl)
            col.add_widget(sec)
        scroll.add_widget(col)
        sheet.card.add_widget(scroll)

        close = ModernButton(text="[b]Got it[/b]", markup=True, size_hint_y=None, height=dp(52),
                             bg_color=theme['accent'], pressed_color=(0.28, 0.29, 0.75, 1),
                             color=(1, 1, 1, 1), font_size='16sp', radius=dp(18))
        close.bind(on_release=sheet.dismiss)
        sheet.card.add_widget(close)
        sheet.open()

    # بعد از جابه‌جایی کارت‌ها، دسته‌ها و عدد درصد هر دو لغزنده را تازه می‌کنیم.
    def _refresh_sliders(self, *args):
        for sl, lb in ((self.noise_slider, self.intensity_value_label),
                       (self.denoise_slider, self.denoise_value_label)):
            sl._redraw()
            lb.text = f"{int(sl.value)}%"

    # فهرست نوع نویز را با رنگ‌ها و قلم‌های حالت فعلی باز می‌کنیم.
    def show_noise_type_picker(self, *args):
        theme = self.get_theme()
        sheet = Sheet(theme, size_hint=(0.92, 0.82))
        sheet.add_header("Noise type")

        scroll = ScrollView(bar_width=dp(3), bar_color=(*theme['accent'][:3], 0.8),
                            bar_inactive_color=(0, 0, 0, 0))
        items = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        items.bind(minimum_height=items.setter('height'))

        # برای هر نوع نویز یک ردیف می‌سازیم و گزینهٔ فعلی را علامت می‌زنیم.
        for kind in self.NOISE_TYPES:
            row = ListRow(theme, _esc(kind), self.NOISE_DESC.get(kind), icon='wave',
                          tint=theme['accent'], selected=(kind == self.noise_kind))

            # مقدار همان ردیف را نگه می‌داریم تا لمس آن، نوع نویز و متن روی دکمه را با هم عوض کند.
            def pick(inst, k=kind):
                self.noise_kind = k
                self.noise_type_btn.text = k
                sheet.dismiss()

            row.bind(on_release=pick)
            items.add_widget(row)

        scroll.add_widget(items)
        sheet.card.add_widget(scroll)
        sheet.open()

    def generate_noise(self, kind, n, std, sample_rate):
        """به تعداد نمونه‌های خواسته‌شده نویز می‌سازد و دامنهٔ آن را با انحراف معیار هدف تنظیم می‌کند."""
        # برای نویز سفید، دامنهٔ هر نمونه را به‌طور مستقل از توزیع یکنواخت بین منفی یک و یک می‌گیریم.
        if kind == 'White noise':
            noise = np.random.uniform(-1.0, 1.0, n)
        # برای نویز گوسی، مقدارها را از توزیع نرمال با میانگین صفر و انحراف معیار یک می‌گیریم.
        elif kind == 'Gaussian noise':
            noise = np.random.normal(0.0, 1.0, n)
        elif kind == 'Impulse noise':
            # هر نمونه با احتمال دو درصد به یک ضربهٔ مثبت یا منفی تبدیل می‌شود و بقیه صفر می‌مانند.
            mask = np.random.random(n) < 0.02
            noise = np.zeros(n)
            noise[mask] = np.random.choice([-1.0, 1.0], size=int(mask.sum()))
        elif kind == 'Hum 50Hz':
            # شمارهٔ نمونه را بر نرخ نمونه‌برداری تقسیم می‌کنیم تا زمان آن بر حسب ثانیه به دست آید.
            t = np.arange(n) / float(sample_rate)
            # وزوز را از مؤلفه‌های ۵۰، ۱۰۰ و ۱۵۰ هرتز و کمی نویز تصادفی می‌سازیم. واحد Hz تعداد چرخه در ثانیه است.
            # Hz = Hertz
            # hum(t) = sin(2π × 50t) + 0.5 sin(2π × 100t) + 0.3 sin(2π × 150t) + 0.05 z
            # در این رابطه z یک نمونهٔ تصادفی با توزیع نرمال استاندارد است.
            noise = (np.sin(2 * np.pi * 50 * t)
                     + 0.5 * np.sin(2 * np.pi * 100 * t)
                     + 0.3 * np.sin(2 * np.pi * 150 * t)
                     + 0.05 * np.random.normal(0, 1, n))
        else:
            # برای ساخت نویزهای رنگی، از یک نویز سفید گوسی شروع می‌کنیم.
            white = np.random.normal(0, 1, n)
            # برای کمتر از چهار نمونه، همان نویز اولیه را به مرحلهٔ تنظیم دامنه می‌فرستیم.
            if n < 4:
                noise = white
            else:
                # با تبدیل FFT ویژهٔ ورودی حقیقی، دامنه و فاز مؤلفه‌های فرکانسی را به دست می‌آوریم.
                # FFT = Fast Fourier Transform
                # RFFT = Real-input Fast Fourier Transform
                spec = np.fft.rfft(white)
                freqs = np.fft.rfftfreq(n)
                # برای اینکه وزن‌دهی در فرکانس صفر به تقسیم بر صفر نرسد، بسامد خانهٔ دوم را جای آن می‌گذاریم.
                freqs[0] = freqs[1]
                # در نویز صورتی، دامنه را بر ریشهٔ فرکانس تقسیم می‌کنیم. در نتیجه توان تقریباً با معکوس فرکانس تغییر می‌کند.
                # A_pink(f) = A_white(f) / √f
                if kind == 'Pink noise':
                    spec = spec / np.sqrt(freqs)
                # در نویز قهوه‌ای، دامنهٔ فرکانس‌های بالا بیشتر کاهش می‌یابد و صدای بم برجسته‌تر می‌شود.
                # A_brown(f) = A_white(f) / f
                elif kind == 'Brown noise':
                    spec = spec / freqs
                # در نویز آبی، مؤلفه‌های فرکانس بالا را با ریشهٔ فرکانس تقویت می‌کنیم.
                # A_blue(f) = A_white(f) × √f
                elif kind == 'Blue noise':
                    spec = spec * np.sqrt(freqs)
                # در نویز بنفش، دامنه را مستقیماً در فرکانس ضرب می‌کنیم.
                # A_violet(f) = A_white(f) × f
                elif kind == 'Violet noise':
                    spec = spec * freqs
                # با تبدیل معکوس به نمونه‌های زمانی برمی‌گردیم و میانگین نویز رنگی را از آن کم می‌کنیم.
                # IRFFT = Inverse of the Real-input Fast Fourier Transform
                noise = np.fft.irfft(spec, n)
                noise = noise - np.mean(noise)
        # دامنه را با انحراف معیار هدف تنظیم می‌کنیم. عدد کوچک مخرج از تقسیم بر صفر جلوگیری می‌کند.
        # noise_out = noise × std_target / (std(noise) + 10⁻¹²)
        noise = noise / (np.std(noise) + 1e-12)
        return noise * std

    # وقتی برنامه به پس‌زمینه می‌رود، پخش فعال را متوقف می‌کنیم.
    def on_pause(self):
        if self.visualizer.is_playing:
            self.visualizer.toggle_play()
        return True

    # مجموعهٔ رنگ‌های حالت فعلی را برای پنجره‌ها و دکمه‌ها برمی‌گردانیم.
    def get_theme(self):
        return THEMES['dark'] if self.is_dark_theme else THEMES['light']

    # سه مؤلفهٔ RGB را در ۲۵۵ ضرب می‌کنیم و بخش صحیح هرکدام را با دو رقم شانزده‌مبنایی می‌نویسیم.
    # RGB = Red, Green, Blue
    def _rgb_to_hex(self, rgb):
        return '%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

    def _quick_places(self):
        """مسیرهای پرکاربرد دستگاه را برای دسترسی سریع از مرورگر فایل آماده می‌کند."""
        places = []
        # در اندروید، حافظهٔ مشترک و پوشه‌های موجود مانند موسیقی و ضبط صدا را پیشنهاد می‌دهیم.
        if IS_ANDROID:
            base = '/storage/emulated/0'
            places.append(('Storage', base))
            for label, sub in (('Music', 'Music'), ('Download', 'Download'),
                               ('Recordings', 'Recordings'), ('Voice', 'Voice Recorder'),
                               ('Documents', 'Documents')):
                p = os.path.join(base, sub)
                if os.path.isdir(p):
                    places.append((label, p))
        else:
            # در رایانه، پوشهٔ کاربر و پوشه‌های پرکاربرد موجود را به میان‌برها اضافه می‌کنیم.
            home = os.path.expanduser('~')
            places.append(('Home', home))
            for label, sub in (('Desktop', 'Desktop'), ('Music', 'Music'),
                               ('Downloads', 'Downloads'), ('Documents', 'Documents')):
                p = os.path.join(home, sub)
                if os.path.isdir(p):
                    places.append((label, p))
        return places

    # بر اساس سیستم‌عامل، پنجرهٔ مناسب برای انتخاب فایل صوتی را باز می‌کنیم.
    def show_file_chooser(self, instance):
        if platform == 'win':
            import tkinter as tk
            from tkinter import filedialog
            # در ویندوز، پنجرهٔ کمکی را پنهان می‌کنیم تا فقط پنجرهٔ انتخاب فایل دیده شود.
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Select an Audio file",
                filetypes=[("All Audio Files", "*.wav;*.mp3;*.m4a;*.ogg;*.flac;*.aac;*.wma;*.WAV;*.MP3"), ("All Files", "*.*")]
            )
            root.destroy()
            # مسیر انتخاب‌شده را مستقیم به تابع پردازش می‌دهیم. لغو انتخاب فقط یک پیام نشان می‌دهد.
            if file_path:
                self.process_audio_file(file_path)
            else:
                self.status_label.text = "No file selected!"
            return

        # روی اندروید، حافظهٔ مشترک هم نقطهٔ شروع و هم مرز بالایی پیمایش است.
        if IS_ANDROID:
            start_path = '/storage/emulated/0'
            root_path = '/storage/emulated/0'
        else:
            start_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            root_path = None
        # اگر مسیر آغازین وجود نداشته باشد، پوشهٔ کاربر یا پوشهٔ جاری را باز می‌کنیم.
        if not os.path.isdir(start_path):
            start_path = os.path.expanduser('~') if os.path.isdir(os.path.expanduser('~')) else '.'

        # در مرورگر داخلی، دکمهٔ تأیید فایل به تابع پردازش وصل می‌شود.
        self.popup = FileBrowser(self.get_theme(), start_path, root_path,
                                 self._quick_places(), self.process_audio_file)
        self.popup.open()

    # نام پوشهٔ خروجی را از حالت انتخاب‌شدهٔ برنامه می‌گیریم.
    def get_output_dir(self):
        folder_name = 'Noise' if self.btn_mode_noise.state == 'down' else 'Denoised'
        if IS_ANDROID:
            try:
                # روی اندروید، ابتدا ساخت پوشه در حافظهٔ مشترک را امتحان می‌کنیم.
                target = f'/storage/emulated/0/{folder_name}'
                os.makedirs(target, exist_ok=True)
                return target
            except Exception:
                # اگر ساخت پوشه در حافظهٔ مشترک ممکن نباشد، از پوشهٔ داده‌های خود برنامه استفاده می‌کنیم.
                target = os.path.join(self.user_data_dir, folder_name)
                os.makedirs(target, exist_ok=True)
                return target
        else:
            # در رایانه، پوشهٔ خروجی را روی میز کار کاربر می‌سازیم.
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            out_dir = os.path.join(desktop, folder_name)
            os.makedirs(out_dir, exist_ok=True)
            return out_dir

    # شکل موج فایل خروجی را رسم و در کنار فایل صوتی ذخیره می‌کنیم.
    def save_waveform(self, samples, sample_rate, out_dir, prefix):
        try:
            # نمونه‌های صحیح را به دامنهٔ نسبی تبدیل می‌کنیم و برای محور افقی، زمان را بر حسب ثانیه می‌سازیم.
            # amplitude = sample / 32768
            # duration = number_of_samples / sample_rate
            audio_float = samples.astype(np.float32) / 32768.0
            seconds = len(audio_float) / sample_rate
            time_axis = np.linspace(0, seconds, len(audio_float))

            # دامنه بر حسب زمان رسم می‌شود تا تغییرات سطح صدا در طول فایل دیده شود.
            plt.figure(figsize=(14, 5))
            plt.plot(time_axis, audio_float, color="deepskyblue", linewidth=0.5)
            plt.title(f"{prefix.capitalize()} Audio Waveform")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Amplitude")
            plt.grid(alpha=0.3)
            plt.tight_layout()

            # تصویر شکل موج را با پسوند PNG و با پیشوندی مشترک با فایل صوتی ذخیره می‌کنیم.
            # PNG = Portable Network Graphics
            img_path = os.path.join(out_dir, f"{prefix}_waveform.png")
            # مقدار DPI برای این تصویر ۱۰۰ است و وضوح خروجی را نسبت به اندازهٔ شکل تعیین می‌کند.
            # DPI = Dots Per Inch
            plt.savefig(img_path, dpi=100)
            plt.close()
            return img_path
        # اگر ذخیرهٔ تصویر خطا بدهد، پیام خطا چاپ می‌شود و نوشتن فایل صوتی همچنان می‌تواند ادامه پیدا کند.
        except Exception as e:
            print(f"Error saving waveform: {e}")
            return None

    def _remove_impulses(self, x, k):
        """برای کاهش ضربه‌های کوتاه، نمونه‌های پرت را با میانهٔ پنج نمونهٔ مجاور جایگزین می‌کند."""
        n = len(x)
        # اگر تعداد نمونه‌ها کمتر از ۹ باشد، این مرحله از صدا عبور می‌کند.
        if n < 9:
            return x
        # در دو سر صدا، نمونهٔ لبه را تکرار می‌کنیم تا برای هر نقطه یک پنجرهٔ پنج‌نمونه‌ای داشته باشیم.
        xp = np.pad(x, 2, mode='edge')
        # میانهٔ هر پنج نمونه را به‌عنوان مقدار محلی می‌گیریم و فاصلهٔ نمونهٔ وسط را از آن می‌سنجیم.
        # dev[i] = abs(x[i] - median(x[i-2 : i+3]))
        med = np.median(np.stack([xp[i:i + n] for i in range(5)]), axis=0)
        dev = np.abs(x - med)
        # برای برآورد پراکندگی از معیار MAD استفاده می‌کنیم. اینجا فاصلهٔ هر نمونه از میانهٔ محلی خودش سنجیده می‌شود.
        # MAD = Median Absolute Deviation
        # mad = 1.4826 × median(dev) + 10⁻⁹
        mad = float(np.median(dev)) * 1.4826 + 1e-9
        # اگر فاصله از k برابر این معیار بیشتر باشد، نمونه را یک ضربهٔ احتمالی در نظر می‌گیریم.
        mask = dev > (k * mad)
        if not mask.any():
            return x
        # فقط نمونه‌های علامت‌خورده را در یک کپی با میانهٔ محلی جایگزین می‌کنیم.
        y = x.copy()
        y[mask] = med[mask]
        return y

    # ضریب کاهش صدا را یک بار در زمان و یک بار در فرکانس هموار می‌کنیم.
    @staticmethod
    def _smooth_gain(g):
        # در هر جهت، میانگین سه خانهٔ مجاور را می‌گیریم. جابه‌جایی چرخشی دو انتهای هر محور را به هم وصل می‌کند.
        # g_new[i] = (g[i-1] + g[i] + g[i+1]) / 3
        g = (np.roll(g, 1, axis=1) + g + np.roll(g, -1, axis=1)) / 3.0
        g = (np.roll(g, 1, axis=0) + g + np.roll(g, -1, axis=0)) / 3.0
        return g

    @staticmethod
    def _median_freq(v, width=25):
        """با گرفتن میانه در امتداد فرکانس، اثر قله‌های باریک را در برآورد زمینه کمتر می‌کند."""
        # در دو لبه، نزدیک‌ترین مقدار را تکرار می‌کنیم تا پنجرهٔ محاسبهٔ میانه کامل بماند.
        h = width // 2
        vp = np.pad(v, h, mode='edge')
        return np.median(np.stack([vp[i:i + len(v)] for i in range(width)]), axis=0)

    def _hum_bins(self, mag, sample_rate, n_fft):
        """خانه‌های طیفی مشکوک به وزوز برق ۵۰ یا ۶۰ هرتز و هارمونیک‌های آن را پیدا می‌کند."""
        # میانهٔ دامنهٔ هر فرکانس را در طول زمان می‌گیریم تا قله‌های پایدار را پیدا کنیم.
        med = np.median(mag, axis=1)
        # ضریب تغییرات CV نشان می‌دهد دامنهٔ هر فرکانس نسبت به میانگین خودش چقدر تغییر کرده است.
        # CV = Coefficient of Variation
        # cv = std(mag) / (mean(mag) + 10⁻¹⁰)
        cv = mag.std(axis=1) / (mag.mean(axis=1) + 1e-10)
        base = self._median_freq(med, 25)
        nb = len(med)
        bins = set()
        # جست‌وجو را به حداکثر ۱۵۰۰ هرتز و تا ۱۰۰ هرتز پایین‌تر از نصف نرخ نمونه‌برداری محدود می‌کنیم.
        limit = min(1500.0, sample_rate / 2 - 100)
        # برای هر دو فرکانس پایهٔ ۵۰ و ۶۰ هرتز، حداکثر سی مضرب صحیح را بررسی می‌کنیم.
        # f = f₀ × h
        for f0 in (50.0, 60.0):
            for h in range(1, 31):
                f = f0 * h
                if f > limit:
                    break
                # فرکانس موردنظر را به شمارهٔ نزدیک‌ترین خانهٔ طیف تبدیل می‌کنیم.
                # k = round(f × n_fft / sample_rate)
                k = int(round(f * n_fft / sample_rate))
                lo, hi = max(0, k - 1), min(nb, k + 2)
                if hi <= lo:
                    continue
                # از خانهٔ هدف و دو همسایه‌اش، خانه‌ای را می‌یابیم که بیشترین میانهٔ دامنه را دارد.
                kk = lo + int(np.argmax(med[lo:hi]))
                # اگر قله از چهار برابر زمینه بلندتر و ضریب تغییراتش کمتر از نیم باشد، آن خانه و همسایه‌هایش را علامت می‌زنیم.
                if med[kk] > 4.0 * base[kk] and cv[kk] < 0.5:
                    bins.update(range(max(0, kk - 1), min(nb, kk + 2)))
        return sorted(bins)

    def denoise_audio(self, samples, sample_rate, strength=0.7):
        """ضربه‌های کوتاه، نویز زمینه و وزوز برق را با قدرتی بین صفر و یک کاهش می‌دهد."""
        # قدرت کاهش نویز را بین صفر و یک محدود می‌کنیم. مقدار صفر یک کپی از نمونه‌های ورودی برمی‌گرداند.
        strength = float(max(0.0, min(1.0, strength)))
        if strength <= 0.0:
            return samples.copy()

        # نمونه‌های ۱۶ بیتی را به مقدار اعشاری تبدیل می‌کنیم تا محاسبات فیلتر با دامنهٔ نسبی انجام شود.
        audio = samples.astype(np.float32) / 32768.0
        # طول هر قطعه ۱۰۲۴ نمونه است. با گام ۲۵۶ نمونه، دو قطعهٔ پیاپی ۷۵ درصد هم‌پوشانی دارند.
        # overlap = 1 - hop / n_fft = 0.75
        n_fft = 1024
        hop = 256
        # برای صدایی کوتاه‌تر از ۲۰۴۸ نمونه، کاهش نویز انجام نمی‌شود.
        if len(audio) < n_fft * 2:
            return samples.copy()

        # ابتدا ضربه‌ها را کاهش می‌دهیم. افزایش قدرت، آستانهٔ تشخیص ضربه را پایین می‌آورد.
        # k = 8 - 4 × strength
        audio = self._remove_impulses(audio, 8.0 - 4.0 * strength)

        # برای محاسبهٔ STFT، هر قطعه را در پنجرهٔ هان ضرب می‌کنیم تا اثر بریدن لبه‌های آن کمتر شود.
        # STFT = Short-Time Fourier Transform
        # w[n] = 0.5 - 0.5 × cos(2πn / (N - 1))
        window = np.hanning(n_fft).astype(np.float32)
        # دو سر صدا را با بازتاب نمونه‌ها گسترش می‌دهیم تا قطعه‌های نزدیک لبه هم داده داشته باشند.
        padded = np.pad(audio, (n_fft // 2, n_fft // 2), mode='reflect')
        # تعداد قطعه‌ها از طول دادهٔ گسترش‌یافته، طول پنجره و گام حرکت به دست می‌آید.
        # frames = 1 + floor((padded_length - n_fft) / hop)
        n_frames = (len(padded) - n_fft) // hop + 1
        # هر ستون یک لحظه و هر ردیف یک خانهٔ فرکانسی است. برای ورودی حقیقی، ۵۱۳ خانه کافی است.
        stft = np.empty((n_fft // 2 + 1, n_frames), dtype=np.complex64)
        for i in range(n_frames):
            # طیف هر قطعه را پس از اعمال پنجره در ستون همان قطعه می‌گذاریم.
            # X[:, i] = rfft(frame_i × window)
            stft[:, i] = np.fft.rfft(padded[i * hop:i * hop + n_fft] * window)

        # قدر مطلق طیف مختلط، دامنهٔ هر فرکانس را در هر قطعه به ما می‌دهد.
        mag = np.abs(stft)
        # برای برآورد زمینهٔ نویز هر فرکانس، صدک بیستم دامنه‌های آن را در زمان می‌گیریم.
        # noise_estimate = 1.9 × percentile(magnitude, 20)
        noise = np.percentile(mag, 20, axis=1) * 1.9
        # میانهٔ ۲۵ خانهٔ مجاور، اثر قله‌های باریک را روی برآورد زمینه کمتر می‌کند.
        noise = self._median_freq(noise, 25)[:, np.newaxis]
        # خانه‌های مشکوک به وزوز برق را جدا علامت می‌زنیم تا بیشتر تضعیف شوند.
        hum = self._hum_bins(mag, sample_rate, n_fft)

        # با افزایش قدرت، سهم بیشتری از نویز تخمینی را کم می‌کنیم و حداقل ضریب عبور پایین‌تر می‌آید.
        # alpha = 0.7 + 2.2 × strength
        # floor_gain = 0.004 + 0.2 × (1 - strength)²
        alpha = 0.7 + 2.2 * strength
        floor = 0.004 + 0.2 * (1.0 - strength) ** 2
        # برای هر خانه، نسبت نویز به دامنهٔ کل را حساب می‌کنیم و ضریب عبور را بین حداقل تعیین‌شده و یک نگه می‌داریم.
        # gain = clip(1 - alpha × noise / (magnitude + 10⁻¹⁰), floor_gain, 1)
        gain = np.clip(1.0 - alpha * noise / (mag + 1e-10), floor, 1.0)
        # هموار کردن ضرایب، تغییرات ناگهانی بین زمان‌ها و فرکانس‌های مجاور را کمتر می‌کند.
        gain = self._smooth_gain(gain)
        freqs = np.fft.rfftfreq(n_fft, 1.0 / sample_rate)
        # زیر ۳۰ هرتز بیشترین تضعیف اضافی را داریم. از ۳۰ تا ۶۰ هرتز اثر به‌تدریج به صفر می‌رسد.
        # hp = clip((60 - frequency) / 30, 0, 1)
        # gain_new = gain × (1 - 0.98 × strength × hp)
        hp = np.clip((60.0 - freqs) / 30.0, 0.0, 1.0)
        gain *= (1.0 - 0.98 * strength * hp)[:, np.newaxis]
        if hum:
            # برای خانه‌های وزوز علامت‌خورده، یک ضریب کاهش دیگر هم اعمال می‌کنیم.
            gain[hum, :] *= (1.0 - 0.98 * strength)
        # ضریب واقعی را در طیف مختلط ضرب می‌کنیم تا دامنه تغییر کند و فاز اولیه حفظ شود.
        clean_stft = stft * gain

        # برای بازسازی، یک آرایه برای جمع قطعه‌ها و یک آرایه برای مجموع وزن پنجره‌ها می‌سازیم.
        out = np.zeros(len(padded), dtype=np.float32)
        wsum = np.zeros(len(padded), dtype=np.float32)
        w2 = window ** 2
        for i in range(n_frames):
            st = i * hop
            # هر ستون را به زمان برمی‌گردانیم، دوباره پنجره می‌زنیم و در محل هم‌پوشانی به خروجی اضافه می‌کنیم.
            out[st:st + n_fft] += np.fft.irfft(clean_stft[:, i], n_fft).astype(np.float32) * window
            # چون پنجره هم در تحلیل و هم در بازسازی ضرب شده، وزن هر سهم برابر مربع پنجره است.
            wsum[st:st + n_fft] += w2
        # مجموع قطعه‌ها را بر مجموع وزن‌ها تقسیم می‌کنیم و بخش‌های اضافه‌شده به دو سر صدا را برمی‌داریم.
        # output[n] = sum_of_windowed_frames[n] / sum_of_squared_windows[n]
        wsum[wsum < 1e-6] = 1.0
        out = (out / wsum)[n_fft // 2: -n_fft // 2]

        # دامنه را به بازهٔ اعداد صحیح ۱۶ بیتی برمی‌گردانیم و طول خروجی را با ورودی یکسان می‌کنیم.
        out = np.clip(out * 32768.0, -32768, 32767).astype(np.int16)
        if len(out) < len(samples):
            out = np.pad(out, (0, len(samples) - len(out)))
        return out[:len(samples)]

    # پس از انتخاب فایل، تنظیمات فعلی را می‌خوانیم و پردازش را در پس‌زمینه آغاز می‌کنیم.
    def process_audio_file(self, file_path):
        # تا پایان پردازش، دکمهٔ افزودن فایل را غیرفعال و پخش قبلی را در صورت لزوم متوقف می‌کنیم.
        self.btn_add_file.disabled = True

        if self.visualizer.is_playing:
            self.visualizer.toggle_play()

        # حالت پردازش و نوع نویز را پیش از شروع کار نگه می‌داریم.
        is_noise_mode = (self.btn_mode_noise.state == 'down')
        action_text = "Adding Noise" if is_noise_mode else "Denoising"
        noise_kind = self.noise_kind
        # با تقسیم درصد لغزنده‌ها بر صد، شدت و قدرت را به نسبت بین صفر و یک تبدیل می‌کنیم.
        intensity = self.noise_slider.value / 100.0
        strength = self.denoise_slider.value / 100.0

        # پیام هر مرحله را در رشتهٔ اصلی نمایش می‌دهیم و تا آماده شدن نتیجه، نمایشگر موج را پنهان می‌کنیم.
        def update_label(text):
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text), 0)
            Clock.schedule_once(lambda dt: setattr(self.visualizer, 'opacity', 0), 0)
            Clock.schedule_once(lambda dt: setattr(self.visualizer, 'size_hint_y', 0), 0)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'size_hint_y', 1), 0)

        # این تابع خواندن فایل، پردازش نمونه‌ها و ذخیرهٔ خروجی را انجام می‌دهد.
        def _worker():
            try:
                update_label(f"Decoding audio...\n({action_text})")
                samples = None
                sample_rate = 16000

                try:
                    # ابتدا فایل را با کتابخانهٔ پردازش صدا باز می‌کنیم.
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(file_path)
                    # کانال‌ها را به یک کانال تبدیل می‌کنیم و نرخ نمونه‌برداری واقعی فایل را می‌خوانیم.
                    audio = audio.set_channels(1)
                    sample_rate = audio.frame_rate
                    # در این شاخه، پیش از بررسی پهنای نمونه، داده‌ها به عدد صحیح ۱۶ بیتی تبدیل می‌شوند.
                    samples = np.array(audio.get_array_of_samples(), dtype=np.int16)
                    # برای ورودی یک‌بایتی، کد ابتدا ۱۲۸ را کم می‌کند و سپس دامنه را ۲۵۶ برابر می‌کند.
                    if audio.sample_width == 1:
                        samples = ((samples.astype(np.int16) - 128) * 256)
                    elif audio.sample_width == 4:
                        # جابه‌جایی ۱۶ بیتی پس از تبدیل بالا انجام می‌شود. در این نقطه، بیت‌های بالای نمونهٔ اصلی دیگر در آرایه نیستند.
                        samples = (samples >> 16).astype(np.int16)
                except ImportError:
                    # اگر کتابخانه در دسترس نباشد، فایل موج را مستقیماً با ابزار استاندارد پایتون می‌خوانیم.
                    if file_path.lower().endswith('.wav'):
                        with wave.open(file_path, 'rb') as wf:
                            # تعداد کانال‌ها، تعداد بایت هر نمونه و نرخ نمونه‌برداری را از سربرگ فایل می‌گیریم.
                            n_channels = wf.getnchannels()
                            sampwidth = wf.getsampwidth()
                            sample_rate = wf.getframerate()
                            raw = wf.readframes(wf.getnframes())
                        # برای نمونهٔ دوبایتی، داده را مستقیماً به‌صورت عدد صحیح ۱۶ بیتی می‌خوانیم.
                        if sampwidth == 2:
                            samples = np.frombuffer(raw, dtype=np.int16).copy()
                        elif sampwidth == 1:
                            # مقدار ۸ بیتی بدون علامت را حول صفر قرار می‌دهیم و به مقیاس ۱۶ بیتی می‌بریم.
                            # sample16 = (sample8 - 128) × 256
                            samples = ((np.frombuffer(raw, dtype=np.uint8).astype(np.int16) - 128) * 256)
                        elif sampwidth == 4:
                            # برای ورودی چهاربایتی ابتدا عدد ۳۲ بیتی را می‌خوانیم و سپس ۱۶ بیت بالایی آن را نگه می‌داریم.
                            samples = (np.frombuffer(raw, dtype=np.int32) >> 16).astype(np.int16)
                        else:
                            raise ValueError("Unsupported WAV sample width")
                        # در فایل چندکاناله، برای هر لحظه میانگین کانال‌ها را می‌گیریم تا یک کانال داشته باشیم.
                        if n_channels > 1:
                            samples = samples.reshape(-1, n_channels).mean(axis=1).astype(np.int16)
                    else:
                        raise ValueError("To read this format, please install pydub first.")
                except Exception as e:
                    raise ValueError(f"Error reading audio file: {str(e)}\nIs the file valid?")

                # اگر داده‌ای برای پردازش به دست نیامده باشد، خطای فایل خالی را نشان می‌دهیم.
                if samples is None or len(samples) == 0:
                    raise ValueError("Empty audio file")

                if is_noise_mode:
                    update_label(f"Adding {noise_kind.lower()}...")
                    # سطح مؤثر کل فایل را با RMS حساب می‌کنیم. تبدیل به عدد اعشاری پیش از توان دو، از سرریز عدد صحیح جلوگیری می‌کند.
                    # RMS = Root Mean Square
                    # RMS = √(Σ xᵢ² / N)
                    rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2))
                    # شدت نویز با سطح فایل متناسب است. برای فایل‌های خیلی آرام، سطح مرجع را دست‌کم ۵۰۰ می‌گیریم.
                    # noise_level = max(rms, 500) × intensity
                    noise_level = max(rms, 500.0) * intensity
                    noise = self.generate_noise(noise_kind, len(samples), noise_level, sample_rate)
                    # نمونه‌های صدا و نویز ساخته‌شده را نقطه‌به‌نقطه با هم جمع می‌کنیم.
                    # output[i] = input[i] + noise[i]
                    processed_samples = samples.astype(np.float64) + noise
                    file_prefix = "noisy"
                else:
                    update_label("Denoising audio...\n(Removing all noise types)")
                    # در حالت کاهش نویز، همان نمونه‌ها و نرخ نمونه‌برداری را با قدرت انتخابی به فیلتر می‌دهیم.
                    processed_samples = self.denoise_audio(samples, sample_rate, strength)
                    file_prefix = "denoised"

                # مقدارهای خارج از بازه را پیش از تبدیل نهایی به نزدیک‌ترین حد ۱۶ بیتی می‌بریم.
                # sample16 = clip(value, -32768, 32767)
                processed_samples = np.clip(processed_samples, -32768, 32767).astype(np.int16)

                update_label("Saving audio & waveform...")
                # پوشهٔ خروجی را پیدا می‌کنیم و زمان فعلی را بر حسب ثانیه در نام فایل می‌گذاریم.
                out_dir = self.get_output_dir()
                timestamp = int(time.time())
                output_path = os.path.join(out_dir, f"{file_prefix}_{timestamp}.wav")
                img_prefix = f"{file_prefix}_{timestamp}"

                # شکل موج را از نمونه‌های پردازش‌شده رسم می‌کنیم تا تصویر مربوط به همان صدای خروجی باشد.
                self.save_waveform(processed_samples, sample_rate, out_dir, img_prefix)

                # صدا را در یک فایل موج تک‌کاناله با دو بایت برای هر نمونه و نرخ نمونه‌برداری فایل ورودی می‌نویسیم.
                with wave.open(output_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(processed_samples.tobytes())

                # پیام پایان کار، نام پوشه و روش پخش نتیجه را برای کاربر آماده می‌کند.
                msg = (
                    f"[color=00C853][b]√ SUCCESS![/b][/color]\n"
                    f"Saved in [{os.path.basename(out_dir)}]\n"
                    f"[size=14sp][color=aaaaaa]Tap the circle to play/pause[/color][/size]\n"
                    f"[size=12sp][color=888888]Made by saber[/color][/size]"
                )

                # نتیجه را به رشتهٔ اصلی می‌فرستیم تا فایل صوتی و نمایشگر روی صفحه آماده شوند.
                Clock.schedule_once(
                    lambda dt: self._on_success(msg, output_path, is_noise_mode,
                                                processed_samples, sample_rate), 0)

            # در صورت خطا، جزئیات را برای عیب‌یابی چاپ می‌کنیم و پیام کوتاه را روی صفحه می‌فرستیم.
            except Exception as e:
                err = f"[color=F44336][b]× ERROR:[/b][/color]\n{str(e)}"
                print(traceback.format_exc())
                Clock.schedule_once(lambda dt: self._on_error(err), 0)

        # رشتهٔ پردازش را جدا از رشتهٔ اصلی شروع می‌کنیم تا صفحه هنگام پردازش پاسخ‌گو بماند.
        threading.Thread(target=_worker, daemon=True).start()

    # پس از موفقیت، دکمهٔ انتخاب فایل را دوباره فعال می‌کنیم و نتیجه را نشان می‌دهیم.
    def _on_success(self, msg, audio_path, is_noise_mode, samples, sample_rate):
        self.btn_add_file.disabled = False
        self.status_label.text = msg

        # پخش‌کننده فایل ذخیره‌شده را می‌خواند و نمایشگر، سطح صدا را از نمونه‌های همان فایل می‌سازد.
        self.visualizer.set_sound(audio_path)
        self.visualizer.set_audio_data(samples, sample_rate)
        self.visualizer.mode = 'noise' if is_noise_mode else 'denoise'

        # نمایشگر را آشکار می‌کنیم و بخشی از فضای پایین آن را برای پیام وضعیت می‌گذاریم.
        self.visualizer.opacity = 1
        self.visualizer.size_hint_y = 0.75
        self.status_label.size_hint_y = 0.25

    # پس از خطا، پیام را نشان می‌دهیم و امکان انتخاب فایل دیگری را فراهم می‌کنیم.
    def _on_error(self, msg):
        self.btn_add_file.disabled = False
        self.status_label.text = msg
        self.visualizer.opacity = 0
        self.visualizer.size_hint_y = 0
        self.status_label.size_hint_y = 1


# اگر این فایل مستقیماً اجرا شود، یک نمونه از برنامه می‌سازیم و حلقهٔ اصلی کیوی را آغاز می‌کنیم.
if __name__ == '__main__':
    NoiseAdderApp().run()
