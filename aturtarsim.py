"""
سامانه کاداستر و تحلیل مزارع (Cadastre & Field Analysis Suite)
نسخه‌ی نمایشی گیت‌هاب (Lite / Demo Edition)

در این نسخه:
  - تمام منوها و ابزارها برای نمایش قابلیت‌های سامانه در رابط کاربری حضور دارند.
  - قابلیت‌های تجاری (ژئورفرنس، شاخص ExG، حذف مناطق مسکونی، ترسیم دستی، هوش مصنوعی SAM،
    و خروجی‌های GIS / Excel / PDF) دارای نشان قفل (🔒) هستند و با کلیک روی آن‌ها پنجره‌ی
    راهنمای ارتقا به نسخه Pro نمایش داده می‌شود.
  - بخش پردازش تصویر از الگوریتم لبه‌یابی پایه استفاده می‌کند و ذخیره‌ی عکس مرزبندی‌شده
    (همراه با واترمارک نسخه دمو) برای تست توسط کاربر فعال است.
"""

import threading
import os

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
from shapely.geometry import Polygon, Point

from detection import extract_parcels, DetectionParams
from i18n import Translator

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

CANVAS_W, CANVAS_H = 760, 640
FONT = "Tahoma"

BG_APP = "#0f172a"
BG_PANEL = "#1e293b"
BG_PANEL_ALT = "#172033"
BORDER = "#334155"
TEXT_PRIMARY = "#e2e8f0"
TEXT_SECONDARY = "#94a3b8"
ACCENT = "#10b981"
ACCENT_HOVER = "#059669"
ACCENT2 = "#6366f1"
ACCENT2_HOVER = "#4f46e5"
WARN = "#f59e0b"
DANGER = "#ef4444"
DANGER_HOVER = "#dc2626"
MUTED_BTN = "#334155"
MUTED_BTN_HOVER = "#475569"


class UltimateGISApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.tr = Translator("fa")

        self.title("Cadastre & Field Analysis Suite — Lite Edition")
        self.geometry("1560x990")
        self.minsize(1320, 870)
        self.configure(fg_color=BG_APP)

        self.image_path = None
        self.original_img = None
        self.processed_img = None
        self.last_polygons = []

        self.img_scale = 1.0
        self.img_offset_x = 0
        self.img_offset_y = 0

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()
        self._retranslate()

    # ------------------------------------------------------------ Pro Lock Dialog
    def show_pro_lock(self, feature_name: str):
        """Displays a sleek upgrade prompt whenever the user interacts with a Pro feature."""
        messagebox.showinfo(
            self.tr.t("pro.title"),
            self.tr.t("pro.body", feature=feature_name)
        )

    # ------------------------------------------------------------ sidebar
    def _section(self, parent, pady=(14, 6)):
        f = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=14, border_width=1, border_color=BORDER)
        f.pack(padx=18, pady=pady, fill="x")
        return f

    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=430, corner_radius=0, fg_color=BG_PANEL_ALT)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        header_row = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        header_row.pack(padx=18, pady=(18, 10), fill="x")
        self.logo_label = ctk.CTkLabel(header_row, text="", font=ctk.CTkFont(family=FONT, size=15, weight="bold"),
                                       text_color=TEXT_PRIMARY, anchor="w", justify="left")
        self.logo_label.pack(side="left", fill="x", expand=True)
        self.btn_lang = ctk.CTkButton(header_row, text="EN", width=46, height=28, font=(FONT, 11, "bold"),
                                      fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8,
                                      command=self.toggle_language)
        self.btn_lang.pack(side="right")

        ctk.CTkFrame(self.sidebar_frame, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=18, pady=(0, 10))

        self.btn_load = ctk.CTkButton(self.sidebar_frame, text="", font=(FONT, 13, "bold"), height=40,
                                      command=self.load_image, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                      corner_radius=10)
        self.btn_load.pack(padx=18, pady=(0, 4), fill="x")

        # ---- georeferencing (Locked in Lite) ----
        self.geo_frame = self._section(self.sidebar_frame)
        self.lbl_geo_header = ctk.CTkLabel(self.geo_frame, text="", font=(FONT, 12, "bold"), text_color=WARN, anchor="e", justify="right")
        self.lbl_geo_header.pack(fill="x", padx=14, pady=(12, 2))
        self.lbl_geo_help = ctk.CTkLabel(self.geo_frame, text="", font=(FONT, 10), text_color=TEXT_SECONDARY, justify="right", anchor="e")
        self.lbl_geo_help.pack(fill="x", padx=14)

        tl_row = ctk.CTkFrame(self.geo_frame, fg_color="transparent")
        tl_row.pack(fill="x", padx=14, pady=(8, 2))
        self.lbl_tl = ctk.CTkLabel(tl_row, text="", width=80, font=(FONT, 10), anchor="e")
        self.lbl_tl.pack(side="right")
        self.entry_tl_lat = ctk.CTkEntry(tl_row, placeholder_text="Lat (Pro)", width=90, corner_radius=8)
        self.entry_tl_lat.pack(side="right", padx=4)
        self.entry_tl_lon = ctk.CTkEntry(tl_row, placeholder_text="Lon (Pro)", width=90, corner_radius=8)
        self.entry_tl_lon.pack(side="right", padx=4)

        br_row = ctk.CTkFrame(self.geo_frame, fg_color="transparent")
        br_row.pack(fill="x", padx=14, pady=(2, 8))
        self.lbl_br = ctk.CTkLabel(br_row, text="", width=80, font=(FONT, 10), anchor="e")
        self.lbl_br.pack(side="right")
        self.entry_br_lat = ctk.CTkEntry(br_row, placeholder_text="Lat (Pro)", width=90, corner_radius=8)
        self.entry_br_lat.pack(side="right", padx=4)
        self.entry_br_lon = ctk.CTkEntry(br_row, placeholder_text="Lon (Pro)", width=90, corner_radius=8)
        self.entry_br_lon.pack(side="right", padx=4)

        self.btn_set_geo = ctk.CTkButton(
            self.geo_frame, text="", font=(FONT, 11, "bold"), height=34,
            command=lambda: self.show_pro_lock("Georeferencing / ثبت مختصات مرجع"),
            fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8
        )
        self.btn_set_geo.pack(fill="x", padx=14, pady=(0, 6))

        self.lbl_geo_status = ctk.CTkLabel(self.geo_frame, text="", font=(FONT, 10, "bold"), text_color=WARN)
        self.lbl_geo_status.pack(padx=14, pady=(0, 12))

        # ---- detection options ----
        self.options_frame = self._section(self.sidebar_frame)

        def _switch_row(parent, var, pady, command=None):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=pady)
            switch = ctk.CTkSwitch(
                row, text="", variable=var, progress_color=ACCENT,
                button_color="#e2e8f0", button_hover_color="#ffffff", width=40,
                command=command
            )
            switch.pack(side="left")
            label = ctk.CTkLabel(row, text="", font=(FONT, 11), anchor="e", justify="right", text_color=TEXT_PRIMARY)
            label.pack(side="right", fill="x", expand=True, padx=(8, 0))
            return switch, label

        self.chk_exg_var = ctk.BooleanVar(value=False)
        self.chk_exg, self.lbl_exg = _switch_row(
            self.options_frame, self.chk_exg_var, (14, 6),
            command=self._on_locked_exg_toggle
        )

        self.show_id_img_var = ctk.BooleanVar(value=True)
        self.chk_show_id, self.lbl_show_id = _switch_row(
            self.options_frame, self.show_id_img_var, 6,
            command=self.redraw_processed_image
        )

        self.save_attributes_var = ctk.BooleanVar(value=False)
        self.chk_save_attrs, self.lbl_save_attrs = _switch_row(
            self.options_frame, self.save_attributes_var, 6,
            command=self._on_locked_attrs_toggle
        )

        self.suppress_builtup_var = ctk.BooleanVar(value=False)
        self.chk_suppress, self.lbl_suppress = _switch_row(
            self.options_frame, self.suppress_builtup_var, (6, 2),
            command=self._on_locked_suppress_toggle
        )

        self.lbl_suppress_help = ctk.CTkLabel(self.options_frame, text="", font=(FONT, 9), text_color=WARN, justify="right", anchor="e")
        self.lbl_suppress_help.pack(fill="x", padx=16, pady=(4, 14))

        # ---- manual drawing + SAM (Locked in Lite) ----
        draw_frame = self._section(self.sidebar_frame)
        self.btn_toggle_draw = ctk.CTkButton(
            draw_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=lambda: self.show_pro_lock("Manual Polygon Drawing / ترسیم دستی"),
            fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8
        )
        self.btn_toggle_draw.pack(fill="x", padx=14, pady=(14, 6))

        self.btn_finish_draw = ctk.CTkButton(
            draw_frame, text="", font=(FONT, 10, "bold"), height=32,
            command=lambda: self.show_pro_lock("Manual Polygon Drawing / ترسیم دستی"),
            fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8
        )
        self.btn_finish_draw.pack(fill="x", padx=14, pady=(0, 6))

        self.btn_toggle_sam = ctk.CTkButton(
            draw_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=lambda: self.show_pro_lock("SAM AI Smart Segmentation / برش هوشمند با هوش مصنوعی"),
            fg_color=ACCENT2, hover_color=ACCENT2_HOVER, corner_radius=8
        )
        self.btn_toggle_sam.pack(fill="x", padx=14, pady=(2, 14))

        # ---- color + sliders ----
        self.color_frame = self._section(self.sidebar_frame)
        self.lbl_color = ctk.CTkLabel(self.color_frame, text="", font=(FONT, 11), anchor="e")
        self.lbl_color.pack(fill="x", padx=14, pady=(14, 2))
        self.color_dropdown = ctk.CTkComboBox(self.color_frame, values=[], state="readonly", corner_radius=8, command=lambda _: self.redraw_processed_image())
        self.color_dropdown.pack(fill="x", padx=14, pady=(0, 14))

        sliders_frame = self._section(self.sidebar_frame)
        self.lbl_thresh = ctk.CTkLabel(sliders_frame, text="", font=(FONT, 11), anchor="e")
        self.lbl_thresh.pack(fill="x", padx=14, pady=(14, 0))
        self.thresh_slider = ctk.CTkSlider(sliders_frame, from_=10, to=100, number_of_steps=90,
                                           command=self.update_thresh_label, progress_color=ACCENT, button_color=ACCENT)
        self.thresh_slider.set(30)
        self.thresh_slider.pack(padx=14, pady=(4, 10), fill="x")

        self.lbl_area = ctk.CTkLabel(sliders_frame, text="", font=(FONT, 11), anchor="e")
        self.lbl_area.pack(fill="x", padx=14)
        self.area_slider = ctk.CTkSlider(sliders_frame, from_=0.02, to=3.0, number_of_steps=149,
                                         command=self.update_area_label, progress_color=ACCENT, button_color=ACCENT)
        self.area_slider.set(0.10)
        self.area_slider.pack(padx=14, pady=(4, 10), fill="x")

        self.lbl_smooth = ctk.CTkLabel(sliders_frame, text="", font=(FONT, 11), anchor="e")
        self.lbl_smooth.pack(fill="x", padx=14)
        self.smooth_slider = ctk.CTkSlider(sliders_frame, from_=1, to=10, number_of_steps=9,
                                           command=self.update_smooth_label, progress_color=ACCENT, button_color=ACCENT)
        self.smooth_slider.set(3)
        self.smooth_slider.pack(padx=14, pady=(4, 14), fill="x")

        self.progress = ctk.CTkProgressBar(self.sidebar_frame, orientation="horizontal", progress_color=ACCENT)
        self.progress.pack(padx=18, pady=(2, 8), fill="x")
        self.progress.set(0)

        self.btn_process = ctk.CTkButton(self.sidebar_frame, text="", font=(FONT, 13, "bold"), height=42,
                                         command=self.process_image, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                         corner_radius=10)
        self.btn_process.pack(padx=18, pady=(0, 10), fill="x")

        # ---- outputs (GIS/Excel/PDF locked, Annotated Image unlocked) ----
        self.output_frame = self._section(self.sidebar_frame)
        self.format_dropdown = ctk.CTkComboBox(
            self.output_frame,
            values=["🔒 Shapefile (.shp) [Pro]", "🔒 GeoJSON (.geojson) [Pro]", "🔒 GeoPackage (.gpkg) [Pro]", "🔒 KML (.kml) [Pro]", "🔒 KMZ (.kmz) [Pro]"],
            state="readonly", corner_radius=8
        )
        self.format_dropdown.set("🔒 Shapefile (.shp) [Pro]")
        self.format_dropdown.pack(fill="x", padx=14, pady=(14, 6))

        self.crs_dropdown = ctk.CTkComboBox(self.output_frame, values=[], state="readonly", corner_radius=8)
        self.crs_dropdown.pack(fill="x", padx=14, pady=6)

        self.btn_save_gis = ctk.CTkButton(
            self.output_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=lambda: self.show_pro_lock("GIS / KML Spatial Export / خروجی لایه مکانی"),
            fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8
        )
        self.btn_save_gis.pack(fill="x", padx=14, pady=4)

        self.btn_save_excel = ctk.CTkButton(
            self.output_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=lambda: self.show_pro_lock("Excel Statistical Report / گزارش اکسل"),
            fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8
        )
        self.btn_save_excel.pack(fill="x", padx=14, pady=4)

        self.btn_save_pdf = ctk.CTkButton(
            self.output_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=lambda: self.show_pro_lock("PDF Map Report / گزارش نقشه PDF"),
            fg_color=MUTED_BTN, hover_color=MUTED_BTN_HOVER, corner_radius=8
        )
        self.btn_save_pdf.pack(fill="x", padx=14, pady=4)

        self.btn_save_img = ctk.CTkButton(
            self.output_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=self.save_image, fg_color=ACCENT, hover_color=ACCENT_HOVER, corner_radius=8
        )
        self.btn_save_img.pack(fill="x", padx=14, pady=(4, 14))

        self.btn_contact = ctk.CTkButton(
            self.sidebar_frame, text="", font=(FONT, 11, "bold"), height=36,
            command=self.show_contact_info, fg_color=WARN, hover_color="#d97706",
            corner_radius=8, text_color="#0f172a"
        )
        self.btn_contact.pack(padx=18, pady=(4, 20), fill="x")

    # --------------------------------------------------------- locked switch handlers
    def _on_locked_exg_toggle(self):
        self.chk_exg_var.set(False)
        self.show_pro_lock("Excess Green (ExG) Vegetation Index / شاخص گیاهی")

    def _on_locked_attrs_toggle(self):
        self.save_attributes_var.set(False)
        self.show_pro_lock("GIS Attribute Table Export / ذخیره جدول مساحت در GIS")

    def _on_locked_suppress_toggle(self):
        self.suppress_builtup_var.set(False)
        self.show_pro_lock("Built-up & Village Suppression / حذف خودکار مناطق مسکونی")

    # --------------------------------------------------------- main panel
    def _build_main_panel(self):
        self.right_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_main_frame.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.right_main_frame.grid_rowconfigure(0, weight=3)
        self.right_main_frame.grid_rowconfigure(1, weight=2)
        self.right_main_frame.grid_columnconfigure(0, weight=1)

        self.canvas_frame = ctk.CTkFrame(self.right_main_frame, fg_color="#0b1220", corner_radius=16,
                                         border_width=1, border_color=BORDER)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self.canvas_frame, text="", font=(FONT, 12), text_color=TEXT_SECONDARY)
        self.image_label.grid(row=0, column=0)
        self.image_label.bind("<Button-1>", self.on_image_click)

        self.status_label = ctk.CTkLabel(self.right_main_frame, text="", font=(FONT, 11), text_color=TEXT_SECONDARY, anchor="w")
        self.status_label.grid(row=0, column=0, sticky="sw", padx=14, pady=8)

        self.table_frame = ctk.CTkFrame(self.right_main_frame, fg_color=BG_PANEL, corner_radius=16,
                                        border_width=1, border_color=BORDER)
        self.table_frame.grid(row=1, column=0, sticky="nsew")
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.lbl_table_header = ctk.CTkLabel(self.table_frame, text="", font=(FONT, 13, "bold"), text_color=WARN)
        self.lbl_table_header.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0f1b2d", fieldbackground="#0f1b2d", foreground=TEXT_PRIMARY,
                        rowheight=26, borderwidth=0, font=(FONT, 10))
        style.configure("Treeview.Heading", background=BG_PANEL_ALT, foreground=TEXT_PRIMARY, font=(FONT, 10, "bold"),
                        borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT2)])

        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Area", "Perimeter"), show="headings", height=8)
        self.tree.column("ID", anchor="center", width=120)
        self.tree.column("Area", anchor="center", width=220)
        self.tree.column("Perimeter", anchor="center", width=220)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=8)

    # --------------------------------------------------------------- i18n
    def toggle_language(self):
        self.tr.set_lang("en" if self.tr.lang == "fa" else "fa")
        self._retranslate()
        self.redraw_processed_image()

    def _retranslate(self):
        t = self.tr.t
        self.title(t("app.title"))
        self.logo_label.configure(text=t("sidebar.header"))
        self.btn_lang.configure(text=t("btn.lang"))
        self.btn_load.configure(text=t("btn.load_image"))

        self.lbl_geo_header.configure(text=t("geo.header"))
        self.lbl_geo_help.configure(text=t("geo.help"))
        self.lbl_tl.configure(text=t("geo.top_left"))
        self.lbl_br.configure(text=t("geo.bottom_right"))
        self.btn_set_geo.configure(text=t("geo.set_button"))
        self.lbl_geo_status.configure(text=t("geo.status_unset"), text_color=WARN)

        self.lbl_exg.configure(text=t("opt.exg"))
        self.lbl_show_id.configure(text=t("opt.show_id"))
        self.lbl_save_attrs.configure(text=t("opt.save_attrs"))
        self.lbl_suppress.configure(text=t("opt.suppress_builtup"))
        self.lbl_suppress_help.configure(text=t("opt.suppress_builtup_help"))

        self.btn_toggle_draw.configure(text=t("draw.toggle_off"))
        self.btn_finish_draw.configure(text=t("draw.finish"))
        self.btn_toggle_sam.configure(text=t("sam.toggle"))

        self.lbl_color.configure(text=t("color.label"))
        prev_color_idx = self.color_dropdown._values.index(self.color_dropdown.get()) if self.color_dropdown.get() in getattr(self.color_dropdown, "_values", []) else 0
        color_values = [t("color.red"), t("color.green"), t("color.blue"), t("color.yellow")]
        self.color_dropdown.configure(values=color_values)
        self.color_dropdown.set(color_values[prev_color_idx] if prev_color_idx < len(color_values) else color_values[0])

        self.lbl_thresh.configure(text=t("slider.canny", val=int(self.thresh_slider.get())))
        self.lbl_area.configure(text=t("slider.area", val=self.area_slider.get()))
        self.lbl_smooth.configure(text=t("slider.smooth", val=int(self.smooth_slider.get())))

        self.btn_process.configure(text=t("btn.process"))
        self.btn_save_gis.configure(text=t("btn.save_gis"))
        self.btn_save_excel.configure(text=t("btn.save_excel"))
        self.btn_save_pdf.configure(text=t("btn.save_pdf"))
        self.btn_save_img.configure(text=t("btn.save_img"))
        self.btn_contact.configure(text=t("btn.contact"))

        crs_values = [t("out.crs_wgs84"), "🔒 UTM Zone 39N (EPSG:32639) [Pro]", "🔒 UTM Zone 38N (EPSG:32638) [Pro]", t("out.crs_utm_auto")]
        self.crs_dropdown.configure(values=crs_values)
        if not self.crs_dropdown.get():
            self.crs_dropdown.set(crs_values[0])

        self.lbl_table_header.configure(text=t("table.header"))
        self.tree.heading("ID", text=t("table.col_id"))
        self.tree.heading("Area", text=t("table.col_area"))
        self.tree.heading("Perimeter", text=t("table.col_perimeter"))

        if self.original_img is None:
            self.image_label.configure(text=t("status.no_image"))
        if not hasattr(self, "_status_key"):
            self._status_key = "status.ready"
            self._status_kwargs = {}
        self.set_status(self._status_key, **self._status_kwargs)

    # --------------------------------------------------------------- misc
    def set_status(self, key, color=None, **kwargs):
        self._status_key = key
        self._status_kwargs = kwargs
        self.status_label.configure(text=self.tr.t(key, **kwargs), text_color=color or TEXT_SECONDARY)

    def update_thresh_label(self, val):
        self.lbl_thresh.configure(text=self.tr.t("slider.canny", val=int(val)))

    def update_area_label(self, val):
        self.lbl_area.configure(text=self.tr.t("slider.area", val=val))

    def update_smooth_label(self, val):
        self.lbl_smooth.configure(text=self.tr.t("slider.smooth", val=int(val)))

    def _msgbox(self, kind, title_key, body_key=None, body_text=None, **kwargs):
        title = self.tr.t(title_key)
        body = body_text if body_text is not None else self.tr.t(body_key, **kwargs)
        {"info": messagebox.showinfo, "warning": messagebox.showwarning, "error": messagebox.showerror}[kind](title, body)

    def show_contact_info(self):
        messagebox.showinfo(self.tr.t("contact.title"), self.tr.t("contact.body"))

    # ---------------------------------------------------------- image I/O
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg *.tif *.tiff")])
        if not file_path:
            return
        img = cv2.imread(file_path)
        if img is None:
            self._msgbox("error", "msg.error", "msg.file_not_readable")
            return
        self.image_path = file_path
        self.original_img = img
        self.processed_img = None
        self.last_polygons = []
        self.display_image(self.original_img)
        self.redraw_processed_image()
        self.set_status("status.image_loaded", name=os.path.basename(file_path), w=img.shape[1], h=img.shape[0])

    def display_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img.ndim == 3 else img
        h_orig, w_orig = img.shape[:2]

        self.img_scale = min(CANVAS_W / w_orig, CANVAS_H / h_orig)
        new_w = max(1, int(w_orig * self.img_scale))
        new_h = max(1, int(h_orig * self.img_scale))
        self.img_offset_x = (CANVAS_W - new_w) // 2
        self.img_offset_y = (CANVAS_H - new_h) // 2

        img_pil = Image.fromarray(img_rgb).resize((new_w, new_h), Image.Resampling.LANCZOS)
        bg_pil = Image.new("RGB", (CANVAS_W, CANVAS_H), (11, 18, 32))
        bg_pil.paste(img_pil, (self.img_offset_x, self.img_offset_y))

        img_tk = ImageTk.PhotoImage(bg_pil)
        self.image_label.configure(image=img_tk, text="")
        self.image_label.image = img_tk

    def _selected_line_color(self):
        s = self.color_dropdown.get()
        t = self.tr.t
        if s == t("color.green"):
            return (0, 255, 0)
        if s == t("color.blue"):
            return (255, 0, 0)
        if s == t("color.yellow"):
            return (0, 255, 255)
        return (0, 0, 255)

    def _apply_demo_watermark(self, img: np.ndarray) -> np.ndarray:
        """Draws a subtle banner watermark on the image in Lite Edition."""
        out = img.copy()
        h, w = out.shape[:2]
        banner_h = max(32, int(h * 0.05))
        overlay = out.copy()
        cv2.rectangle(overlay, (0, h - banner_h), (w, h), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.78, out, 0.22, 0, out)
        text = "CadastreVision Lite Demo  |  Coded by Moghtaderi (@mogtdri)  |  Upgrade to Pro for GIS & AI Engine"
        font_scale = max(0.45, min(1.0, w / 1150.0))
        thickness = max(1, int(round(font_scale * 2)))
        cv2.putText(out, text, (16, h - int(banner_h * 0.32)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (16, 185, 129), thickness, cv2.LINE_AA)
        return out

    def redraw_processed_image(self):
        if self.original_img is None:
            return

        result_img = self.original_img.copy()
        show_ids = self.show_id_img_var.get()
        line_color = self._selected_line_color()

        for row in self.tree.get_children():
            self.tree.delete(row)

        areas, perims, area_unit, perim_unit = self._compute_stats(self.last_polygons)

        for idx, (coords, area_val, perim_val) in enumerate(zip(self.last_polygons, areas, perims), start=1):
            cv2.polylines(result_img, [coords.reshape(-1, 1, 2)], True, line_color, 2)
            self.tree.insert("", "end", values=(idx, f"{area_val:.1f} {area_unit}", f"{perim_val:.1f} {perim_unit}"))
            if show_ids:
                M = cv2.moments(coords)
                if M["m00"] != 0:
                    cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                    cv2.putText(result_img, str(idx), (cX - 10, cY + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, line_color, 2)

        if self.last_polygons:
            result_img = self._apply_demo_watermark(result_img)

        self.processed_img = result_img
        self.display_image(result_img)

    def on_image_click(self, event):
        if self.original_img is None or not self.last_polygons:
            return
        click_x = (event.x - self.img_offset_x) / self.img_scale
        click_y = (event.y - self.img_offset_y) / self.img_scale
        click_point = Point(click_x, click_y)
        kept = []
        removed = False
        for coords in self.last_polygons:
            if Polygon(coords).contains(click_point):
                removed = True
            else:
                kept.append(coords)
        if removed:
            self.last_polygons = kept
            self.redraw_processed_image()

    # ---------------------------------------------------------- processing
    def process_image(self):
        if self.original_img is None:
            self._msgbox("error", "msg.error", "msg.no_image_selected")
            return

        params = DetectionParams(
            canny_low=int(self.thresh_slider.get()),
            min_area_ratio=self.area_slider.get() / 100.0,
            smooth_factor=self.smooth_slider.get(),
        )

        self.btn_process.configure(state="disabled", text=self.tr.t("btn.process.working"))
        self.set_status("status.processing", WARN)
        self.progress.set(0.15)

        img_copy = self.original_img.copy()
        threading.Thread(target=self._process_worker, args=(img_copy, params), daemon=True).start()

    def _process_worker(self, img, params):
        try:
            polygons = extract_parcels(img, params)
            error = None
        except Exception as e:
            polygons = []
            error = str(e)
        self.after(0, self._process_done, polygons, error)

    def _process_done(self, polygons, error):
        self.progress.set(1.0)
        self.btn_process.configure(state="normal", text=self.tr.t("btn.process"))

        if error:
            messagebox.showerror(self.tr.t("msg.error"), self.tr.t("msg.process_error", error=error))
            self.set_status("status.error", DANGER)
            self.progress.set(0)
            return

        self.last_polygons = polygons
        self.redraw_processed_image()
        self.set_status("status.done", ACCENT, n=len(polygons))
        self._msgbox("info", "msg.success", "msg.detected_n", n=len(polygons))
        self.progress.set(0)

    # ---------------------------------------------------------- stats / units
    def _compute_stats(self, polygons_px):
        if not polygons_px:
            return [], [], "", ""
        areas = [Polygon(c).area for c in polygons_px]
        perims = [Polygon(c).length for c in polygons_px]
        return areas, perims, self.tr.t("unit.px2"), self.tr.t("unit.px")

    # ---------------------------------------------------------- exports
    def save_image(self):
        if self.processed_img is None:
            self._msgbox("warning", "msg.warning", "msg.need_process_first")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if save_path:
            cv2.imwrite(save_path, self.processed_img)
            self._msgbox("info", "msg.saved", "msg.image_saved", path=save_path)


if __name__ == "__main__":
    app = UltimateGISApp()
    app.mainloop()  