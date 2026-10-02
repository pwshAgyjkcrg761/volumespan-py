# ==============================================================================
# SCRIPT: VolumeSpan.py
# VERSION: 2026.10.02__14.36.16
# TARGET: Python 3.14.5
#
# Copyright (C) 2026 pwshAgyjkcrg761
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
# ==============================================================================
# <PROTECTED>
# ==============================================================================
# AI INSTRUCTIONS
# Copyright (c) 2026 pwshAgyjkcrg761
# License: MIT
# Source: https://git.disroot.org/pwshAgyjkcrg761/AI_Instructions
#
# AI INSTRUCTIONS v2026.09.01__04.25.09 : 
#
# 1. MESSAGE STAMP: 
#    - Every response containing code MUST begin with a standalone version stamp.
#    - Use CHICAGO TIME (Central Time), 24-hour clock.
#    - Format: YYYY.MM.DD__HH.MM.SS.
#    - CRITICAL: Use the time provided in the prompt or at 
#      https://www.timeanddate.com/worldclock/usa/chicago. Ensure minutes are exact.
#
# 2. VERSION SNIPPET PROHIBITION:
#    - DO NOT provide code snippets, anchors, or steps to update the script's 
#      internal VERSION comment or $scriptVersion variable. 
#    - The user handles internal file versioning manually based on the Message Stamp.
#
# 3. SCRIPT OUTPUT (SURGICAL FIXES ONLY):
#    - Provide minimal, highly targeted, surgical edits. Do not rewrite large blocks or 
#      entire functions.
#    - Always use a codebox with a copy button.
#    - Multiple modifications MUST be presented strictly ONE step at a time. Wait for 
#      user confirmation before proceeding to the next step. 
#    - DO NOT modify or refactor any code inside <PROTECTED> tags.
#
# 4. VERBATIM ANCHOR PROTOCOL (FOR NOTEPAD++):
#    - To facilitate "Find" in Notepad++, always structure edits with:
#      - "Verbatim Anchor (Before)" - The exact lines of existing code immediately before 
#         the change.
#      - "Verbatim Anchor (After)" - The exact lines of existing code immediately after 
#         the change.
#      - "Snippet to REPLACE" - The exact code block to be deleted.
#      - "What to PASTE in its place" - The new code block to be inserted.
#    - Do not summarize, truncate, or refactor the existing code used as an anchor.
#    - Match spaces, comments, and symbols exactly as they appear in the file.
#
# 5. CONTENT PRESERVATION:
#    - Do not remove, modify, or strip out telemetry data or DevDebug information from any 
#      provided code.
# ==============================================================================
# </PROTECTED>

import sys
import re
import os
import json
import ctypes
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, 
                             QMessageBox, QDialog, QComboBox, QDoubleSpinBox, QSpinBox,
                             QTextBrowser, QDialogButtonBox, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtGui import QActionGroup, QPalette, QColor, QIcon

APP_VERSION = "2026.10.02__14.36.16"

def increment_disc_id(disc_id: str) -> str:
    match = re.search(r'(.*?)(\d+)$', disc_id)
    if not match:
        return disc_id
    prefix, number_str = match.groups()
    new_number = int(number_str) + 1
    return f"{prefix}{new_number:0{len(number_str)}d}"

class SettingsWrapper:
    def __init__(self, config_path):
        self.path = config_path
        self.data = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.data = json.load(f)
            except: pass
    def value(self, key, default):
        return self.data.get(key, default)
    def setValue(self, key, value):
        self.data[key] = value
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f)
        except: pass

class VolumeSpanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"VolumeSpan v{APP_VERSION}")
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            bundle_dir = getattr(sys, '_MEIPASS', base_dir)
        else:
            base_dir = os.path.dirname(os.path.realpath(__file__))
            bundle_dir = base_dir

        internal_dir = os.path.join(base_dir, "VolumeSpan_internal")
        os.makedirs(internal_dir, exist_ok=True)
        self.config_file = os.path.join(internal_dir, "VolumeSpan.config.json")
        
        if sys.platform == "win32":
            myappid = f"pwshAgyjkcrg761.volumespan.{APP_VERSION}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        icon_path = os.path.join(bundle_dir, "VolumeSpan_internal", "icons", "volumespan_cd_icon.svg")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)
            
        self.default_size = (840, 368)
        
        self.settings = SettingsWrapper(self.config_file)
        self.load_geometry()
        
        self.current_theme = self.settings.value("theme", "System")
        self.apply_theme(self.current_theme)
        
        self.source_directory = os.path.normpath(self.settings.value("source_directory", os.getcwd()))
        self.target_directory = os.path.normpath(self.settings.value("target_directory", os.getcwd()))
        
        self.init_ui()
        self.load_saved_settings()

    def init_ui(self):
        self.create_menu()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        disc_id_layout = QHBoxLayout()
        disc_id_label = QLabel("Disc ID:")
        self.disc_id_input = QLineEdit()
        self.disc_id_input.setText("BD-0001")
        self.disc_id_input.setFixedWidth(120)
        disc_id_layout.addWidget(disc_id_label)
        disc_id_layout.addWidget(self.disc_id_input)
        
        self.lbl_last_disc = QLabel("")
        self.lbl_last_disc.setStyleSheet("color: #007acc; font-weight: bold; margin-left: 10px;")
        self.lbl_last_disc.setVisible(False)
        disc_id_layout.addWidget(self.lbl_last_disc)
        disc_id_layout.addStretch()
        
        layout.addLayout(disc_id_layout)
        
        # Source Directory Selection
        src_layout = QHBoxLayout()
        self.src_label = QLabel(f"Source: {self.source_directory}")
        self.src_label.setWordWrap(True)
        btn_src_select = QPushButton("Select Source Folder")
        btn_src_select.clicked.connect(self.select_source_directory)
        src_layout.addWidget(self.src_label, 1)
        src_layout.addWidget(btn_src_select)
        layout.addLayout(src_layout)
        
        # Staging Target Selection
        target_layout = QHBoxLayout()
        self.target_label = QLabel(f"Staging Target: {self.target_directory}")
        self.target_label.setWordWrap(True)
        btn_target_select = QPushButton("Select Staging Target")
        btn_target_select.clicked.connect(self.select_target_directory)
        target_layout.addWidget(self.target_label, 1)
        target_layout.addWidget(btn_target_select)
        layout.addLayout(target_layout)
        
        # Multi-Tier Capacity Options
        media_items = [
            "BDXL QL (128 GB)", "BDXL TL (100 GB)", "BD-R DL (50 GB)", 
            "BD-R SL (25 GB)", "DVD-9 (8.5 GB)", "DVD-5 (4.7 GB)", 
            "Mini DVD-R (1.4 GB)", "CD-R (700 MB)", "Mini CD-R (210 MB)", 
            "USB Flash Drive", "Custom Size"
        ]
        fallback_items = ["None (Disabled)"] + media_items

        # Primary Media
        cap_layout = QHBoxLayout()
        lbl_pri = QLabel("Primary Media:")
        lbl_pri.setFixedWidth(110)
        cap_layout.addWidget(lbl_pri)
        self.combo_primary_media = QComboBox()
        self.combo_primary_media.addItems(media_items)
        self.combo_primary_media.setMinimumWidth(180)
        cap_layout.addWidget(self.combo_primary_media, 1)

        lbl_nom = QLabel("Nominal:")
        lbl_nom.setFixedWidth(55)
        cap_layout.addWidget(lbl_nom)
        self.spin_nominal = QDoubleSpinBox()
        self.spin_nominal.setRange(0.1, 999999.0)
        self.spin_nominal.setDecimals(1)
        self.spin_nominal.setValue(128.0)
        self.spin_nominal.setFixedWidth(75)
        self.spin_nominal.setEnabled(False)
        cap_layout.addWidget(self.spin_nominal)

        self.combo_unit = QComboBox()
        self.combo_unit.addItems(["GB", "MB"])
        self.combo_unit.setFixedWidth(55)
        self.combo_unit.setEnabled(False)
        cap_layout.addWidget(self.combo_unit)
        
        lbl_ceil = QLabel("Ceiling (GiB):")
        lbl_ceil.setFixedWidth(75)
        cap_layout.addWidget(lbl_ceil)
        self.spin_ceiling = QDoubleSpinBox()
        self.spin_ceiling.setRange(0.01, 10000.0)
        self.spin_ceiling.setDecimals(2)
        self.spin_ceiling.setValue(118.00)
        self.spin_ceiling.setFixedWidth(75)
        cap_layout.addWidget(self.spin_ceiling)

        lbl_lim = QLabel("Limit (0=∞):")
        lbl_lim.setFixedWidth(75)
        cap_layout.addWidget(lbl_lim)
        self.spin_limit = QSpinBox()
        self.spin_limit.setRange(0, 9999)
        self.spin_limit.setValue(0)
        self.spin_limit.setFixedWidth(60)
        cap_layout.addWidget(self.spin_limit)
        layout.addLayout(cap_layout)

        # Fallback 1
        fb1_layout = QHBoxLayout()
        lbl_fb1 = QLabel("Fallback 1 Media:")
        lbl_fb1.setFixedWidth(110)
        fb1_layout.addWidget(lbl_fb1)
        self.combo_fb1_media = QComboBox()
        self.combo_fb1_media.addItems(fallback_items)
        self.combo_fb1_media.setMinimumWidth(180)
        fb1_layout.addWidget(self.combo_fb1_media, 1)

        lbl_fb1_nom = QLabel("Nominal:")
        lbl_fb1_nom.setFixedWidth(55)
        fb1_layout.addWidget(lbl_fb1_nom)
        self.spin_fb1_nominal = QDoubleSpinBox()
        self.spin_fb1_nominal.setRange(0.1, 999999.0)
        self.spin_fb1_nominal.setDecimals(1)
        self.spin_fb1_nominal.setValue(100.0)
        self.spin_fb1_nominal.setFixedWidth(75)
        self.spin_fb1_nominal.setEnabled(False)
        fb1_layout.addWidget(self.spin_fb1_nominal)

        self.combo_fb1_unit = QComboBox()
        self.combo_fb1_unit.addItems(["GB", "MB"])
        self.combo_fb1_unit.setFixedWidth(55)
        self.combo_fb1_unit.setEnabled(False)
        fb1_layout.addWidget(self.combo_fb1_unit)
        
        lbl_fb1_ceil = QLabel("Ceiling (GiB):")
        lbl_fb1_ceil.setFixedWidth(75)
        fb1_layout.addWidget(lbl_fb1_ceil)
        self.spin_fb1_ceiling = QDoubleSpinBox()
        self.spin_fb1_ceiling.setRange(0.01, 10000.0)
        self.spin_fb1_ceiling.setDecimals(2)
        self.spin_fb1_ceiling.setValue(93.00)
        self.spin_fb1_ceiling.setFixedWidth(75)
        fb1_layout.addWidget(self.spin_fb1_ceiling)

        lbl_fb1_lim = QLabel("Limit (0=∞):")
        lbl_fb1_lim.setFixedWidth(75)
        fb1_layout.addWidget(lbl_fb1_lim)
        self.spin_fb1_limit = QSpinBox()
        self.spin_fb1_limit.setRange(0, 9999)
        self.spin_fb1_limit.setValue(0)
        self.spin_fb1_limit.setFixedWidth(60)
        fb1_layout.addWidget(self.spin_fb1_limit)
        layout.addLayout(fb1_layout)

        # Fallback 2
        fb2_layout = QHBoxLayout()
        lbl_fb2 = QLabel("Fallback 2 Media:")
        lbl_fb2.setFixedWidth(110)
        fb2_layout.addWidget(lbl_fb2)
        self.combo_fb2_media = QComboBox()
        self.combo_fb2_media.addItems(fallback_items)
        self.combo_fb2_media.setMinimumWidth(180)
        fb2_layout.addWidget(self.combo_fb2_media, 1)

        lbl_fb2_nom = QLabel("Nominal:")
        lbl_fb2_nom.setFixedWidth(55)
        fb2_layout.addWidget(lbl_fb2_nom)
        self.spin_fb2_nominal = QDoubleSpinBox()
        self.spin_fb2_nominal.setRange(0.1, 999999.0)
        self.spin_fb2_nominal.setDecimals(1)
        self.spin_fb2_nominal.setValue(50.0)
        self.spin_fb2_nominal.setFixedWidth(75)
        self.spin_fb2_nominal.setEnabled(False)
        fb2_layout.addWidget(self.spin_fb2_nominal)

        self.combo_fb2_unit = QComboBox()
        self.combo_fb2_unit.addItems(["GB", "MB"])
        self.combo_fb2_unit.setFixedWidth(55)
        self.combo_fb2_unit.setEnabled(False)
        fb2_layout.addWidget(self.combo_fb2_unit)
        
        lbl_fb2_ceil = QLabel("Ceiling (GiB):")
        lbl_fb2_ceil.setFixedWidth(75)
        fb2_layout.addWidget(lbl_fb2_ceil)
        self.spin_fb2_ceiling = QDoubleSpinBox()
        self.spin_fb2_ceiling.setRange(0.01, 10000.0)
        self.spin_fb2_ceiling.setDecimals(2)
        self.spin_fb2_ceiling.setValue(46.50)
        self.spin_fb2_ceiling.setFixedWidth(75)
        fb2_layout.addWidget(self.spin_fb2_ceiling)

        lbl_fb2_lim = QLabel("Limit (0=∞):")
        lbl_fb2_lim.setFixedWidth(75)
        fb2_layout.addWidget(lbl_fb2_lim)
        self.spin_fb2_limit = QSpinBox()
        self.spin_fb2_limit.setRange(0, 9999)
        self.spin_fb2_limit.setValue(0)
        self.spin_fb2_limit.setFixedWidth(60)
        fb2_layout.addWidget(self.spin_fb2_limit)
        layout.addLayout(fb2_layout)

        # Fallback 3
        fb3_layout = QHBoxLayout()
        lbl_fb3 = QLabel("Fallback 3 Media:")
        lbl_fb3.setFixedWidth(110)
        fb3_layout.addWidget(lbl_fb3)
        self.combo_fb3_media = QComboBox()
        self.combo_fb3_media.addItems(fallback_items)
        self.combo_fb3_media.setMinimumWidth(180)
        fb3_layout.addWidget(self.combo_fb3_media, 1)

        lbl_fb3_nom = QLabel("Nominal:")
        lbl_fb3_nom.setFixedWidth(55)
        fb3_layout.addWidget(lbl_fb3_nom)
        self.spin_fb3_nominal = QDoubleSpinBox()
        self.spin_fb3_nominal.setRange(0.1, 999999.0)
        self.spin_fb3_nominal.setDecimals(1)
        self.spin_fb3_nominal.setValue(25.0)
        self.spin_fb3_nominal.setFixedWidth(75)
        self.spin_fb3_nominal.setEnabled(False)
        fb3_layout.addWidget(self.spin_fb3_nominal)

        self.combo_fb3_unit = QComboBox()
        self.combo_fb3_unit.addItems(["GB", "MB"])
        self.combo_fb3_unit.setFixedWidth(55)
        self.combo_fb3_unit.setEnabled(False)
        fb3_layout.addWidget(self.combo_fb3_unit)
        
        lbl_fb3_ceil = QLabel("Ceiling (GiB):")
        lbl_fb3_ceil.setFixedWidth(75)
        fb3_layout.addWidget(lbl_fb3_ceil)
        self.spin_fb3_ceiling = QDoubleSpinBox()
        self.spin_fb3_ceiling.setRange(0.01, 10000.0)
        self.spin_fb3_ceiling.setDecimals(2)
        self.spin_fb3_ceiling.setValue(23.20)
        self.spin_fb3_ceiling.setFixedWidth(75)
        fb3_layout.addWidget(self.spin_fb3_ceiling)

        lbl_fb3_lim = QLabel("Limit (0=∞):")
        lbl_fb3_lim.setFixedWidth(75)
        fb3_layout.addWidget(lbl_fb3_lim)
        self.spin_fb3_limit = QSpinBox()
        self.spin_fb3_limit.setRange(0, 9999)
        self.spin_fb3_limit.setValue(0)
        self.spin_fb3_limit.setFixedWidth(60)
        fb3_layout.addWidget(self.spin_fb3_limit)
        layout.addLayout(fb3_layout)

        # Connect media selection and nominal size handlers
        self.combo_primary_media.currentIndexChanged.connect(self.primary_media_changed)
        self.combo_fb1_media.currentIndexChanged.connect(lambda idx: self.fallback_changed(idx, self.spin_fb1_nominal, self.combo_fb1_unit, self.spin_fb1_ceiling))
        self.combo_fb2_media.currentIndexChanged.connect(lambda idx: self.fallback_changed(idx, self.spin_fb2_nominal, self.combo_fb2_unit, self.spin_fb2_ceiling))
        self.combo_fb3_media.currentIndexChanged.connect(lambda idx: self.fallback_changed(idx, self.spin_fb3_nominal, self.combo_fb3_unit, self.spin_fb3_ceiling))

        self.spin_nominal.valueChanged.connect(lambda: self.nominal_changed(self.combo_primary_media, self.spin_nominal, self.combo_unit, self.spin_ceiling))
        self.combo_unit.currentIndexChanged.connect(lambda: self.nominal_changed(self.combo_primary_media, self.spin_nominal, self.combo_unit, self.spin_ceiling))

        self.spin_fb1_nominal.valueChanged.connect(lambda: self.nominal_changed(self.combo_fb1_media, self.spin_fb1_nominal, self.combo_fb1_unit, self.spin_fb1_ceiling))
        self.combo_fb1_unit.currentIndexChanged.connect(lambda: self.nominal_changed(self.combo_fb1_media, self.spin_fb1_nominal, self.combo_fb1_unit, self.spin_fb1_ceiling))

        self.spin_fb2_nominal.valueChanged.connect(lambda: self.nominal_changed(self.combo_fb2_media, self.spin_fb2_nominal, self.combo_fb2_unit, self.spin_fb2_ceiling))
        self.combo_fb2_unit.currentIndexChanged.connect(lambda: self.nominal_changed(self.combo_fb2_media, self.spin_fb2_nominal, self.combo_fb2_unit, self.spin_fb2_ceiling))

        self.spin_fb3_nominal.valueChanged.connect(lambda: self.nominal_changed(self.combo_fb3_media, self.spin_fb3_nominal, self.combo_fb3_unit, self.spin_fb3_ceiling))
        self.combo_fb3_unit.currentIndexChanged.connect(lambda: self.nominal_changed(self.combo_fb3_media, self.spin_fb3_nominal, self.combo_fb3_unit, self.spin_fb3_ceiling))
        
# Action Buttons (2x2 Workflow Grid)
        layout.addStretch(1)

        row1_layout = QHBoxLayout()
        btn_dry_run = QPushButton("1. Run Simulation (Dry Run)")
        btn_dry_run.clicked.connect(self.run_dry_run)
        row1_layout.addWidget(btn_dry_run)
        
        btn_execute = QPushButton("2. Generate Hardlink Backup Trees")
        btn_execute.clicked.connect(self.execute_hardlinks)
        row1_layout.addWidget(btn_execute)
        layout.addLayout(row1_layout)

        row2_layout = QHBoxLayout()
        btn_cleanup = QPushButton("3. Clean Staging Target (Remove Hardlinks)")
        btn_cleanup.clicked.connect(self.cleanup_staging)
        row2_layout.addWidget(btn_cleanup)

        btn_purge = QPushButton("4. Purge Burned Files from Source (Exclude Tail)")
        btn_purge.clicked.connect(self.purge_burned_source)
        row2_layout.addWidget(btn_purge)
        layout.addLayout(row2_layout)

        for btn in (btn_dry_run, btn_execute, btn_cleanup, btn_purge):
            btn.setMinimumHeight(42)
            btn.setMaximumHeight(54)

        layout.addStretch(1)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _compute_nominal_ceiling(self, nominal_val, unit_str):
        if unit_str == "MB":
            total_bytes = nominal_val * 1_000_000
        else: # GB
            total_bytes = nominal_val * 1_000_000_000
        
        # 95% of nominal decimal capacity converted to GiB gives safe Windows usable ceiling
        safe_gib = (total_bytes * 0.95) / (1024**3)
        return max(0.01, round(safe_gib, 2))

    def nominal_changed(self, combo_media, spin_nominal, combo_unit, spin_ceiling):
        media_text = combo_media.currentText()
        if "USB Flash Drive" in media_text or "Custom" in media_text:
            val = spin_nominal.value()
            unit = combo_unit.currentText()
            calc_ceiling = self._compute_nominal_ceiling(val, unit)
            spin_ceiling.setValue(calc_ceiling)

    def _get_media_name_from_ceiling(self, ceiling_bytes):
        gib = ceiling_bytes / (1024**3)
        mapping = [
            (118.00, "BDXL QL (128 GB)"),
            (93.00, "BDXL TL (100 GB)"),
            (46.50, "BD-R DL (50 GB)"),
            (23.20, "BD-R SL (25 GB)"),
            (7.90, "DVD-9 (8.5 GB)"),
            (4.35, "DVD-5 (4.7 GB)"),
            (1.36, "Mini DVD-R (1.4 GB)"),
            (0.68, "CD-R (700 MB)"),
            (0.19, "Mini CD-R (210 MB)")
        ]
        for preset_gib, name in mapping:
            if abs(gib - preset_gib) < 0.05:
                return name
        return f"Custom / Flash ({gib:.2f} GiB)"

    def primary_media_changed(self, index):
        presets = {
            0: (128.0, "GB", 118.00),
            1: (100.0, "GB", 93.00),
            2: (50.0, "GB", 46.50),
            3: (25.0, "GB", 23.20),
            4: (8.5, "GB", 7.90),
            5: (4.7, "GB", 4.35),
            6: (1.4, "GB", 1.36),
            7: (700.0, "MB", 0.68),
            8: (210.0, "MB", 0.19)
        }
        if index in presets:
            nom, unit, ceil = presets[index]
            self.spin_nominal.setEnabled(False)
            self.combo_unit.setEnabled(False)
            self.spin_nominal.setValue(nom)
            self.combo_unit.setCurrentText(unit)
            self.spin_ceiling.setValue(ceil)
        elif index == 9: # USB Flash Drive
            self.spin_nominal.setEnabled(True)
            self.combo_unit.setEnabled(True)
            calc_ceil = self._compute_nominal_ceiling(self.spin_nominal.value(), self.combo_unit.currentText())
            self.spin_ceiling.setValue(calc_ceil)
        else: # Custom Size
            self.spin_nominal.setEnabled(True)
            self.combo_unit.setEnabled(True)

    def fallback_changed(self, index, spin_nominal, combo_unit, spin_ceiling):
        presets = {
            1: (128.0, "GB", 118.00),
            2: (100.0, "GB", 93.00),
            3: (50.0, "GB", 46.50),
            4: (25.0, "GB", 23.20),
            5: (8.5, "GB", 7.90),
            6: (4.7, "GB", 4.35),
            7: (1.4, "GB", 1.36),
            8: (700.0, "MB", 0.68),
            9: (210.0, "MB", 0.19)
        }
        if index in presets:
            nom, unit, ceil = presets[index]
            spin_nominal.setEnabled(False)
            combo_unit.setEnabled(False)
            spin_nominal.setValue(nom)
            combo_unit.setCurrentText(unit)
            spin_ceiling.setValue(ceil)
        elif index == 10: # USB Flash Drive
            spin_nominal.setEnabled(True)
            combo_unit.setEnabled(True)
            calc_ceil = self._compute_nominal_ceiling(spin_nominal.value(), combo_unit.currentText())
            spin_ceiling.setValue(calc_ceil)
        elif index == 11: # Custom Size
            spin_nominal.setEnabled(True)
            combo_unit.setEnabled(True)
        else: # None (Disabled)
            spin_nominal.setEnabled(False)
            combo_unit.setEnabled(False)

    def select_source_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Source Directory", self.source_directory)
        if dir_path:
            self.source_directory = os.path.normpath(dir_path).replace('/', os.sep)
            self.src_label.setText(f"Source: {self.source_directory}")
            self.settings.setValue("source_directory", self.source_directory)

    def select_target_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Staging Target Directory", self.target_directory)
        if dir_path:
            self.target_directory = os.path.normpath(dir_path).replace('/', os.sep)
            self.target_label.setText(f"Staging Target: {self.target_directory}")
            self.settings.setValue("target_directory", self.target_directory)

    def calculate_discs(self):
        tiers = [
            {
                "id": "primary",
                "ceiling": int(self.spin_ceiling.value() * 1024 * 1024 * 1024),
                "limit": self.spin_limit.value(),
                "used": 0
            }
        ]
        if self.combo_fb1_media.currentIndex() > 0:
            tiers.append({
                "id": "fb1",
                "ceiling": int(self.spin_fb1_ceiling.value() * 1024 * 1024 * 1024),
                "limit": self.spin_fb1_limit.value(),
                "used": 0
            })
        if self.combo_fb2_media.currentIndex() > 0:
            tiers.append({
                "id": "fb2",
                "ceiling": int(self.spin_fb2_ceiling.value() * 1024 * 1024 * 1024),
                "limit": self.spin_fb2_limit.value(),
                "used": 0
            })
        if self.combo_fb3_media.currentIndex() > 0:
            tiers.append({
                "id": "fb3",
                "ceiling": int(self.spin_fb3_ceiling.value() * 1024 * 1024 * 1024),
                "limit": self.spin_fb3_limit.value(),
                "used": 0
            })

        all_files = []
        for root, _, files in os.walk(self.source_directory):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.source_directory)
                try:
                    fsize = os.path.getsize(full_path)
                    all_files.append((rel_path, full_path, fsize))
                except Exception as e:
                    print(f"Error accessing file {full_path}: {e}")

        if not all_files:
            return []

        all_files.sort(key=lambda x: x[0])

        max_configured_capacity = max(t["ceiling"] for t in tiers)
        for rel_path, full_path, fsize in all_files:
            if fsize > max_configured_capacity:
                fsize_gib = fsize / (1024**3)
                max_gib = max_configured_capacity / (1024**3)
                QMessageBox.critical(
                    self, 
                    "File Exceeds Media Capacity", 
                    f"Unable to partition archive.\n\n"
                    f"The following file exceeds the largest selected media tier ({max_gib:.2f} GiB):\n"
                    f"• {rel_path} ({fsize_gib:.2f} GiB)\n\n"
                    f"Please select a larger media format or remove the oversized file."
                )
                return None

        def select_tier_for_data(remaining_bytes, file_size):
            available = [t for t in tiers if t["limit"] == 0 or t["used"] < t["limit"]]
            if not available:
                return None

            fitting = [t for t in available if remaining_bytes <= t["ceiling"]]
            if fitting:
                candidate = min(fitting, key=lambda t: t["ceiling"])
            else:
                candidate = max(available, key=lambda t: t["ceiling"])

            if file_size > candidate["ceiling"]:
                larger = [t for t in available if file_size <= t["ceiling"]]
                if not larger:
                    return None
                candidate = min(larger, key=lambda t: t["ceiling"])

            return candidate

        discs = []
        start_disc_id = self.disc_id_input.text().strip() or "BD-0001"
        current_disc_label = start_disc_id

        total_remaining = sum(f[2] for f in all_files)
        initial_tier = select_tier_for_data(total_remaining, all_files[0][2])
        if initial_tier is None:
            QMessageBox.critical(
                self,
                "Media Limit Exceeded",
                "Unable to start allocation. Media limits have been reached or no tier is capable of holding the first file."
            )
            return None

        initial_tier["used"] += 1
        current_disc = {
            "label": current_disc_label,
            "files": [],
            "size": 0,
            "ceiling": initial_tier["ceiling"]
        }

        for i, (rel_path, full_path, fsize) in enumerate(all_files):
            if current_disc["size"] + fsize <= current_disc["ceiling"]:
                current_disc["files"].append((rel_path, full_path, fsize))
                current_disc["size"] += fsize
            else:
                if current_disc["files"]:
                    discs.append(current_disc)
                    current_disc_label = increment_disc_id(current_disc_label)

                remaining_bytes = sum(f[2] for f in all_files[i:])
                next_tier = select_tier_for_data(remaining_bytes, fsize)
                if next_tier is None:
                    QMessageBox.critical(
                        self,
                        "Media Limit Reached",
                        f"Unable to partition remaining archive files.\n\n"
                        f"Configured disc limits have been exhausted before allocating:\n"
                        f"• {rel_path} ({fsize / (1024**3):.2f} GiB)\n\n"
                        f"Please increase the disc limits or enable additional fallback media tiers."
                    )
                    return None

                next_tier["used"] += 1
                current_disc = {
                    "label": current_disc_label,
                    "files": [(rel_path, full_path, fsize)],
                    "size": fsize,
                    "ceiling": next_tier["ceiling"]
                }

        if current_disc["files"]:
            discs.append(current_disc)

        return discs

    def validate_paths(self) -> bool:
        src_path = os.path.abspath(self.source_directory)
        target_path = os.path.abspath(self.target_directory)

        # Ensure source and target are not identical
        if os.path.normcase(src_path) == os.path.normcase(target_path):
            QMessageBox.critical(self, "Invalid Path Selection", 
                                 "Source and Staging Target directories cannot be the same folder.")
            return False

        # Ensure target is not inside source, and source is not inside target
        try:
            common = os.path.commonpath([src_path, target_path])
            if os.path.normcase(common) == os.path.normcase(src_path):
                QMessageBox.critical(self, "Invalid Path Selection", 
                                     "Staging Target cannot be located inside the Source directory.")
                return False
            if os.path.normcase(common) == os.path.normcase(target_path):
                QMessageBox.critical(self, "Invalid Path Selection", 
                                     "Source directory cannot be located inside the Staging Target folder.")
                return False
        except ValueError:
            pass

        # Ensure paths are not network UNC shares
        if src_path.startswith(("\\\\", "//")) or target_path.startswith(("\\\\", "//")):
            QMessageBox.critical(self, "Network Drive Error", 
                                 "Network paths (UNC shares) are not supported. Hardlinks require local disk partitions.")
            return False

        src_drive = os.path.splitdrive(src_path)[0].upper()
        target_drive = os.path.splitdrive(target_path)[0].upper()

        # Verify both reside on the same drive volume
        if not src_drive or not target_drive or src_drive != target_drive:
            QMessageBox.critical(self, "Volume Mismatch Error", 
                                 f"NTFS Hardlinks require source and staging target to be on the exact same drive partition.\n\nSource Drive: {src_drive}\nTarget Drive: {target_drive}")
            return False

        # Verify drive is a local physical/removable volume, not a mapped network drive
        if sys.platform == "win32":
            src_root = src_drive if src_drive.endswith("\\") else src_drive + "\\"
            # DRIVE_REMOTE = 4
            if ctypes.windll.kernel32.GetDriveTypeW(src_root) == 4:
                QMessageBox.critical(self, "Network Drive Error", 
                                     f"Drive {src_drive} is a network-mapped drive. Hardlinks require a local drive partition.")
                return False

        return True

    def run_dry_run(self):
        if not self.validate_paths():
            return

        discs = self.calculate_discs()
        if discs is None or not discs:
            QMessageBox.information(self, "Scan Complete", "No files found or operation cancelled.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Dry Run Report - VolumeSpan")
        dialog.resize(700, 500)
        d_layout = QVBoxLayout(dialog)

        tree = QTreeWidget()
        tree.setHeaderLabels(["Disc / Relative Path", "Size", "Free Space", "Media Type"])
        tree.setColumnWidth(0, 360)
        tree.setColumnWidth(1, 95)
        tree.setColumnWidth(2, 95)

        total_bytes = 0

        for d in discs:
            disc_item = QTreeWidgetItem(tree)
            pct = (d["size"] / d["ceiling"]) * 100 if d["ceiling"] > 0 else 0.0
            media_name = self._get_media_name_from_ceiling(d["ceiling"])
            free_gib = max(0.0, (d["ceiling"] - d["size"]) / (1024**3))
            warn_tag = " [< 70% Full]" if pct < 70.0 else ""
            disc_item.setText(0, f"{d['label']} ({len(d['files'])} files) - {pct:.1f}% filled{warn_tag}")
            disc_item.setText(1, f"{d['size'] / (1024**3):.2f} GiB")
            disc_item.setText(2, f"{free_gib:.2f} GiB")
            disc_item.setText(3, media_name)

            if pct < 70.0:
                for col in range(4):
                    disc_item.setForeground(col, QColor("#e04848"))

            total_bytes += d["size"]

            for rel_path, _, fsize in d["files"]:
                file_item = QTreeWidgetItem(disc_item)
                file_item.setText(0, rel_path)
                file_item.setText(1, f"{fsize / (1024**2):.2f} MiB")
                file_item.setText(2, "")
                file_item.setText(3, "")

        d_layout.addWidget(tree)
        
        summary_label = QLabel(f"Total Discs: {len(discs)} | Total Data: {total_bytes / (1024**3):.2f} GiB")
        d_layout.addWidget(summary_label)

        def save_index(exclude_tail=False):
            export_discs = discs[:-1] if (exclude_tail and len(discs) > 1) else discs
            if not export_discs:
                return

            export_bytes = sum(d["size"] for d in export_discs)

            if len(export_discs) == 1:
                suggested_filename = f"{export_discs[0]['label']}.txt"
            else:
                suggested_filename = f"{export_discs[0]['label']} - {export_discs[-1]['label']}.txt"

            default_save_path = os.path.join(self.target_directory, suggested_filename)
            file_path, _ = QFileDialog.getSaveFileName(
                dialog, "Save Index Report", default_save_path, "Text Files (*.txt);;All Files (*)"
            )
            if not file_path:
                return

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("=" * 80 + "\n")
                    f.write("VOLUMESPAN INDEX REPORT\n")
                    f.write(f"Total Discs: {len(export_discs)} | Total Data: {export_bytes / (1024**3):.2f} GiB\n")
                    f.write(f"Source: {self.source_directory}\n")
                    f.write(f"Staging Target: {self.target_directory}\n")
                    f.write("=" * 80 + "\n\n")

                    for d in export_discs:
                        pct = (d["size"] / d["ceiling"]) * 100 if d["ceiling"] > 0 else 0.0
                        media_name = self._get_media_name_from_ceiling(d["ceiling"])
                        f.write(f"[{d['label']}] - {media_name} ({d['size'] / (1024**3):.2f} GiB / {d['ceiling'] / (1024**3):.2f} GiB, {pct:.1f}% filled, {len(d['files'])} files)\n")
                        f.write("-" * 80 + "\n")
                        for rel_path, _, fsize in d["files"]:
                            f.write(f"  {rel_path} ({fsize / (1024**2):.2f} MiB)\n")
                        f.write("\n")

                QMessageBox.information(dialog, "Index Saved", f"Index report successfully saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(dialog, "Error Saving Index", f"An error occurred while saving the index report:\n{e}")

        btn_layout = QHBoxLayout()
        btn_save_index = QPushButton("Save As Index")
        btn_save_index.clicked.connect(lambda: save_index(exclude_tail=False))
        btn_layout.addWidget(btn_save_index)

        btn_save_index_no_tail = QPushButton("Save Index (Exclude Tail)")
        btn_save_index_no_tail.setEnabled(len(discs) > 1)
        btn_save_index_no_tail.clicked.connect(lambda: save_index(exclude_tail=True))
        btn_layout.addWidget(btn_save_index_no_tail)
        btn_layout.addStretch()

        btn_close = QPushButton("Close Report")
        btn_close.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_close)

        d_layout.addLayout(btn_layout)

        dialog.exec()

    def execute_hardlinks(self):
        if not self.validate_paths():
            return

        discs = self.calculate_discs()
        if not discs:
            return

        reply = QMessageBox.question(self, "Confirm Staging Execution", 
                                     f"Ready to create hardlinks for {len(discs)} disc volume(s) in:\n{self.target_directory}\n\nProceed?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        created_links = 0
        try:
            for d in discs:
                disc_dir = os.path.join(self.target_directory, d["label"])
                os.makedirs(disc_dir, exist_ok=True)

                for rel_path, full_path, _ in d["files"]:
                    dest_path = os.path.join(disc_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    if not os.path.exists(dest_path):
                        os.link(full_path, dest_path)
                        created_links += 1

            tail_disc = discs[-1]
            tail_size_gib = tail_disc["size"] / (1024**3)
            tail_free_gib = max(0.0, (tail_disc["ceiling"] - tail_disc["size"]) / (1024**3))
            pct = (tail_disc["size"] / tail_disc["ceiling"]) * 100 if tail_disc["ceiling"] > 0 else 0.0
            warning_tag = " <span style='color: #e04848; font-weight: bold;'>[&lt; 70% Full]</span>" if pct < 70.0 else ""
            self.lbl_last_disc.setText(f"Last Disc ID Created: {tail_disc['label']} ({tail_size_gib:.2f} GiB / {tail_free_gib:.2f} GiB){warning_tag}")
            self.lbl_last_disc.setVisible(True)

            QMessageBox.information(self, "Execution Complete", 
                                    f"Successfully created {created_links} hardlink(s) across {len(discs)} disc staging folder(s).")
        except Exception as e:
            QMessageBox.critical(self, "Error Creating Hardlinks", f"An error occurred during hardlinking:\n{e}")

    def cleanup_staging(self):
        if not self.validate_paths():
            return

        target_dir = os.path.abspath(self.target_directory)
        if not os.path.isdir(target_dir):
            QMessageBox.warning(self, "Invalid Directory", f"Staging target folder does not exist:\n{target_dir}")
            return

        reply = QMessageBox.question(
            self, 
            "Confirm Staging Cleanup",
            f"Are you sure you want to clean up staging structures in:\n{target_dir}\n\n"
            "Safety Check: Only verified hardlinks (link count > 1) and empty directories will be removed. "
            "Original single files will be preserved.\n\nProceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted_links = 0
        skipped_files = 0
        removed_dirs = 0

        try:
            for root, dirs, files in os.walk(target_dir, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        # Ensure it is a hardlink (link count >= 2 pointing to the underlying file data)
                        if stat.st_nlink > 1:
                            os.unlink(file_path)
                            deleted_links += 1
                        else:
                            skipped_files += 1
                    except Exception as e:
                        print(f"Error checking/deleting file {file_path}: {e}")

                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        # os.rmdir will only remove a folder if it is completely empty
                        os.rmdir(dir_path)
                        removed_dirs += 1
                    except OSError:
                        pass

            msg = f"Cleanup complete.\n\nRemoved {deleted_links} hardlink(s) and {removed_dirs} staging folder(s)."
            if skipped_files > 0:
                msg += f"\n\nSafety Notice: Preserved {skipped_files} file(s) because their hardlink count was 1 (non-hardlinks)."

            QMessageBox.information(self, "Cleanup Complete", msg)

        except Exception as e:
            QMessageBox.critical(self, "Cleanup Error", f"An error occurred while cleaning up staging:\n{e}")

    def purge_burned_source(self):
        if not self.validate_paths():
            return

        discs = self.calculate_discs()
        if not discs:
            return

        if len(discs) <= 1:
            QMessageBox.information(
                self, 
                "No Completed Volumes to Purge",
                f"Only 1 volume ({discs[0]['label']}) was generated, which is currently the tail volume.\n\n"
                "There are no earlier completed volumes to purge."
            )
            return

        burned_discs = discs[:-1]
        tail_disc = discs[-1]

        total_files = sum(len(d["files"]) for d in burned_discs)
        total_bytes = sum(d["size"] for d in burned_discs)
        label_range = (f"{burned_discs[0]['label']} through {burned_discs[-1]['label']}"
                       if len(burned_discs) > 1 else burned_discs[0]['label'])

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Purge Burned Files from Source")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(
            f"<b>Ready to purge {len(burned_discs)} completed volume(s) ({label_range})</b><br><br>"
            f"<b>Source Folder:</b> {self.source_directory}<br>"
            f"<b>Data to Remove:</b> {total_files:,} files ({total_bytes / (1024**3):.2f} GiB)<br>"
            f"<b>Protected Tail Volume:</b> {tail_disc['label']} ({len(tail_disc['files']):,} files, "
            f"{tail_disc['size'] / (1024**3):.2f} GiB) will be <b>PRESERVED</b>.<br><br>"
            "<i>WARNING: Only proceed if you have verified that these completed discs are burned and readable.</i>"
        )

        btn_purge_now = msg_box.addButton("Purge Source Files Now", QMessageBox.ButtonRole.AcceptRole)
        btn_export_bat = msg_box.addButton("Export Cleanup .BAT File", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.setDefaultButton(btn_cancel)

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == btn_purge_now:
            confirm = QMessageBox.question(
                self,
                "Final Confirmation - Delete Source Files",
                f"Permanently delete {total_files:,} source files ({total_bytes / (1024**3):.2f} GiB) from your drive?\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

            deleted_files = 0
            errors = 0
            for d in burned_discs:
                for _, full_path, _ in d["files"]:
                    try:
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            deleted_files += 1
                    except Exception as e:
                        errors += 1
                        print(f"Error deleting {full_path}: {e}")

            # Prune empty directories in Source tree
            removed_dirs = 0
            for root, dirs, _ in os.walk(self.source_directory, topdown=False):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        os.rmdir(dir_path)
                        removed_dirs += 1
                    except OSError:
                        pass

            result_msg = (
                f"Purge complete.\n\n"
                f"• Deleted: {deleted_files:,} file(s)\n"
                f"• Cleaned: {removed_dirs:,} empty subfolder(s)\n"
                f"• Preserved: Tail volume {tail_disc['label']} remains intact in Source."
            )
            if errors > 0:
                result_msg += f"\n\nNotice: {errors} file(s) could not be removed (in use or access denied)."

            QMessageBox.information(self, "Purge Complete", result_msg)

        elif clicked == btn_export_bat:
            suggested_bat = (f"Purge_Burned_{burned_discs[0]['label']}_to_{burned_discs[-1]['label']}.bat"
                             if len(burned_discs) > 1 else f"Purge_Burned_{burned_discs[0]['label']}.bat")
            default_path = os.path.join(self.target_directory, suggested_bat)
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Cleanup Batch Script", default_path, "Batch Files (*.bat);;All Files (*)"
            )
            if not file_path:
                return

            try:
                ps_source_dir = self.source_directory.replace("'", "''")

                with open(file_path, "w", encoding="utf-8") as f:
                    # Windows cmd launcher extracting PowerShell execution block safely
                    f.write("@echo off\n")
                    f.write("setlocal\n")
                    f.write('set "SCRIPT_PATH=%~f0"\n')
                    f.write('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=$env:SCRIPT_PATH; $lines=[System.IO.File]::ReadAllLines($p,[System.Text.Encoding]::UTF8); $s=[Array]::IndexOf($lines,\':::POWERSHELL_START:::\'); $e=[Array]::IndexOf($lines,\':::FILE_LIST_START:::\'); if($s -ge 0 -and $e -gt $s){ $code=$lines[($s+1)..($e-1)] -join [Environment]::NewLine; & ([scriptblock]::Create($code)) $p } else { Write-Error \'Script boundary markers missing.\'; exit 1 }"\n')
                    f.write("if %ERRORLEVEL% NEQ 0 (\n")
                    f.write("    echo.\n")
                    f.write("    echo Script execution failed with error code %ERRORLEVEL%.\n")
                    f.write("    pause\n")
                    f.write(")\n")
                    f.write("exit /b %ERRORLEVEL%\n\n")

                    # PowerShell logic block (executed cleanly, never parses raw file paths as code)
                    f.write(":::POWERSHELL_START:::\n")
                    f.write("param([string]$scriptPath)\n")
                    f.write("[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n")
                    f.write('Write-Host "============================================================" -ForegroundColor Cyan\n')
                    f.write('Write-Host "VOLUMESPAN SOURCE PURGE SCRIPT" -ForegroundColor Cyan\n')
                    f.write(f'Write-Host "Burned Volume(s): {label_range}" -ForegroundColor Yellow\n')
                    f.write(f'Write-Host "Files to Delete: {total_files:,} ({total_bytes / (1024**3):.2f} GiB)"\n')
                    f.write(f'Write-Host "Preserved Tail: {tail_disc["label"]}" -ForegroundColor Green\n')
                    f.write('Write-Host "============================================================" -ForegroundColor Cyan\n')
                    f.write('Write-Host "WARNING: This will permanently delete the burned source files!" -ForegroundColor Red\n')
                    f.write('Write-Host "Only proceed if all discs have finished burning and verified." -ForegroundColor Yellow\n')
                    f.write('Write-Host ""\n')
                    f.write('$confirm = Read-Host "Do you want to proceed? (Y/N)"\n')
                    f.write('if ($confirm.Trim().ToUpper() -ne "Y") {\n')
                    f.write('    Write-Host "Operation cancelled. No files were deleted." -ForegroundColor Yellow\n')
                    f.write('    exit 0\n')
                    f.write('}\n')
                    f.write('Write-Host ""\n')
                    f.write('Write-Host "Reading file list..." -ForegroundColor Cyan\n')
                    f.write('$allLines = [System.IO.File]::ReadAllLines($scriptPath, [System.Text.Encoding]::UTF8)\n')
                    f.write('$listIdx = [Array]::IndexOf($allLines, ":::FILE_LIST_START:::")\n')
                    f.write('if ($listIdx -lt 0) { Write-Error "File list boundary missing."; exit 1 }\n\n')
                    f.write('$files = $allLines[($listIdx + 1)..($allLines.Length - 1)] | Where-Object { $_.Trim() -ne \'\' -and -not $_.StartsWith(\'#\') }\n')
                    f.write('Write-Host "Deleting $($files.Count) burned source file(s)..." -ForegroundColor Cyan\n')
                    f.write('$deletedCount = 0\n')
                    f.write('foreach ($file in $files) {\n')
                    f.write('    if (Test-Path -LiteralPath $file) {\n')
                    f.write('        try {\n')
                    f.write('            Remove-Item -LiteralPath $file -Force -ErrorAction Stop\n')
                    f.write('            $deletedCount++\n')
                    f.write('        } catch {\n')
                    f.write('            Write-Warning "Could not delete: $file ($($_.Exception.Message))"\n')
                    f.write('        }\n')
                    f.write('    }\n')
                    f.write('}\n\n')
                    f.write('Write-Host "Pruning empty directories in source tree..." -ForegroundColor Cyan\n')
                    f.write(f'$srcDir = \'{ps_source_dir}\'\n')
                    f.write('if (Test-Path -LiteralPath $srcDir) {\n')
                    f.write('    Get-ChildItem -LiteralPath $srcDir -Recurse -Directory -Force | Sort-Object -Property FullName -Descending | ForEach-Object {\n')
                    f.write('        if (($_.GetFileSystemInfos().Count -eq 0)) {\n')
                    f.write('            try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue } catch {}\n')
                    f.write('        }\n')
                    f.write('    }\n')
                    f.write('}\n\n')
                    f.write('Write-Host ""\n')
                    f.write('Write-Host "Cleanup completed successfully. Deleted $deletedCount file(s)." -ForegroundColor Green\n')
                    f.write('Write-Host "Press any key to exit..."\n')
                    f.write('$null = [Console]::ReadKey($true)\n\n')

                    # Plain text file list section
                    f.write(":::FILE_LIST_START:::\n")
                    for d in burned_discs:
                        f.write(f"# --- Files for {d['label']} ---\n")
                        for _, full_path, _ in d["files"]:
                            f.write(f"{full_path}\n")

                QMessageBox.information(self, "Script Exported", f"Cleanup batch script exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"An error occurred while exporting batch file:\n{e}")

    def load_saved_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                    # Clamp loaded indices within valid range of updated media options list
                    max_primary = self.combo_primary_media.count() - 1
                    max_fallback = self.combo_fb1_media.count() - 1

                    idx_primary = min(config.get("primary_media_index", 0), max_primary)
                    self.combo_primary_media.setCurrentIndex(idx_primary)
                    self.spin_nominal.setValue(config.get("nominal", 128.0))
                    self.combo_unit.setCurrentText(config.get("unit", "GB"))
                    self.spin_ceiling.setValue(config.get("ceiling_gib", 118.00))
                    self.spin_limit.setValue(config.get("limit", 0))

                    idx_fb1 = min(config.get("fb1_media_index", 0), max_fallback)
                    self.combo_fb1_media.setCurrentIndex(idx_fb1)
                    self.spin_fb1_nominal.setValue(config.get("fb1_nominal", 100.0))
                    self.combo_fb1_unit.setCurrentText(config.get("fb1_unit", "GB"))
                    self.spin_fb1_ceiling.setValue(config.get("fb1_ceiling_gib", 93.00))
                    self.spin_fb1_limit.setValue(config.get("fb1_limit", 0))

                    idx_fb2 = min(config.get("fb2_media_index", 0), max_fallback)
                    self.combo_fb2_media.setCurrentIndex(idx_fb2)
                    self.spin_fb2_nominal.setValue(config.get("fb2_nominal", 50.0))
                    self.combo_fb2_unit.setCurrentText(config.get("fb2_unit", "GB"))
                    self.spin_fb2_ceiling.setValue(config.get("fb2_ceiling_gib", 46.50))
                    self.spin_fb2_limit.setValue(config.get("fb2_limit", 0))

                    idx_fb3 = min(config.get("fb3_media_index", 0), max_fallback)
                    self.combo_fb3_media.setCurrentIndex(idx_fb3)
                    self.spin_fb3_nominal.setValue(config.get("fb3_nominal", 25.0))
                    self.combo_fb3_unit.setCurrentText(config.get("fb3_unit", "GB"))
                    self.spin_fb3_ceiling.setValue(config.get("fb3_ceiling_gib", 23.20))
                    self.spin_fb3_limit.setValue(config.get("fb3_limit", 0))
                    
                    saved_disc_id = config.get("disc_id_input", "")
                    if saved_disc_id:
                        self.disc_id_input.setText(saved_disc_id)
                    
                    last_disc = config.get("last_disc_id", "")
                    if last_disc:
                        self.lbl_last_disc.setText(f"Last Disc ID Created: {last_disc}")
                        self.lbl_last_disc.setVisible(True)
            except: pass

    def load_geometry(self):
        self.resize(*self.default_size)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if "x" in config and "y" in config:
                        self.move(config.get("x"), config.get("y"))
                    else:
                        self.center_window()
                    self.resize(config.get("width", self.default_size[0]),
                                config.get("height", self.default_size[1]))
            except:
                self.center_window()
        else:
            self.center_window()

    def center_window(self):
        frame_geo = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame_geo.moveCenter(screen)
        self.move(frame_geo.topLeft())

    def closeEvent(self, event):
        pos = self.pos()
        self.settings.setValue("x", pos.x())
        self.settings.setValue("y", pos.y())
        self.settings.setValue("width", self.width())
        self.settings.setValue("height", self.height())
        self.settings.setValue("ceiling_gib", self.spin_ceiling.value())
        self.settings.setValue("primary_media_index", self.combo_primary_media.currentIndex())
        self.settings.setValue("nominal", self.spin_nominal.value())
        self.settings.setValue("unit", self.combo_unit.currentText())
        self.settings.setValue("limit", self.spin_limit.value())

        self.settings.setValue("fb1_ceiling_gib", self.spin_fb1_ceiling.value())
        self.settings.setValue("fb1_media_index", self.combo_fb1_media.currentIndex())
        self.settings.setValue("fb1_nominal", self.spin_fb1_nominal.value())
        self.settings.setValue("fb1_unit", self.combo_fb1_unit.currentText())
        self.settings.setValue("fb1_limit", self.spin_fb1_limit.value())

        self.settings.setValue("fb2_ceiling_gib", self.spin_fb2_ceiling.value())
        self.settings.setValue("fb2_media_index", self.combo_fb2_media.currentIndex())
        self.settings.setValue("fb2_nominal", self.spin_fb2_nominal.value())
        self.settings.setValue("fb2_unit", self.combo_fb2_unit.currentText())
        self.settings.setValue("fb2_limit", self.spin_fb2_limit.value())

        self.settings.setValue("fb3_ceiling_gib", self.spin_fb3_ceiling.value())
        self.settings.setValue("fb3_media_index", self.combo_fb3_media.currentIndex())
        self.settings.setValue("fb3_nominal", self.spin_fb3_nominal.value())
        self.settings.setValue("fb3_unit", self.combo_fb3_unit.currentText())
        self.settings.setValue("fb3_limit", self.spin_fb3_limit.value())

        self.settings.setValue("theme", self.current_theme)
        self.settings.setValue("disc_id_input", self.disc_id_input.text().strip())
        
        if self.lbl_last_disc.isVisible():
            raw_text = self.lbl_last_disc.text().replace("Last Disc ID Created: ", "")
            self.settings.setValue("last_disc_id", raw_text)
            
        event.accept()

    def create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        tools_menu = menu_bar.addMenu("&Tools")
        themes_menu = tools_menu.addMenu("&Themes")
        
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        themes = ["Dark", "Light", "System"]
        for theme in themes:
            action = themes_menu.addAction(theme)
            action.setCheckable(True)
            self.theme_group.addAction(action)
            action.triggered.connect(lambda checked, t=theme: self.change_theme(t))
            
        saved_theme = self.settings.value("theme", "System")
        for action in self.theme_group.actions():
            if action.text() == saved_theme:
                action.setChecked(True)
        
        help_menu = menu_bar.addMenu("&Help")
        manual_action = help_menu.addAction("Manual")
        manual_action.triggered.connect(self.show_manual)
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def apply_theme(self, theme_name):
        app = QApplication.instance()
        app.setStyle("Fusion")
        palette = QPalette()
        
        if theme_name == "Dark":
            palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d2d"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#252526"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#aaaaaa"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#007acc"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#666666"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#666666"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#666666"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor("#1e1e1e"))
            
        elif theme_name == "Light":
            palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#fcfcfc"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#e1e1e1"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#777777"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d7"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#a0a0a0"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#a0a0a0"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#a0a0a0"))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor("#e1e1e1"))
            
        else:
            is_dark = app.style().standardPalette().color(QPalette.ColorRole.Window).lightness() < 128
            self.apply_theme("Dark" if is_dark else "Light")
            return
            
        app.setPalette(palette)

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme(theme_name)

    def show_manual(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manual")
        dialog.resize(680, 580)
        layout = QVBoxLayout(dialog)

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: palette(text);
                background-color: palette(base);
                border: none;
                padding: 20px;
            }
            h1 { color: #007acc; font-size: 22px; margin-bottom: 0px; }
            h2 { color: #007acc; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 5px; margin-top: 25px; }
            b { color: #007acc; }
            .step-card {
                background-color: rgba(0, 122, 204, 0.05);
                border: 1px solid rgba(0, 122, 204, 0.2);
                border-radius: 6px;
                padding: 12px;
                margin-bottom: 10px;
            }
            code { 
                font-family: 'Consolas', monospace; 
                background-color: rgba(128, 128, 128, 0.2); 
                padding: 2px 5px; 
                border-radius: 3px; 
            }
            a { color: #007acc; text-decoration: none; }
        """)

        manual_text = (
            f"<h1>VolumeSpan v{APP_VERSION}</h1>"
            f"<p style='margin-top: 0;'>MANUAL & USAGE GUIDE | Copyright (C) 2026 pwshAgyjkcrg761</p>"
            f"<br>"
            f"<h2>OVERVIEW</h2>"
            f"<p>VolumeSpan is an automated optical disc and removable media staging utility designed to partition local directory trees sequentially into fixed-capacity volumes (e.g., <b>BD-0001</b>, <b>BD-0002</b>) using native NTFS hardlinks.</p>"
            f"<h2>USAGE WORKFLOW</h2>"
            f"<div class='step-card'><b>1. Select Source & Staging Target:</b> Choose the source folder to archive and a staging folder on the <b>same local drive volume</b>.</div>"
            f"<div class='step-card'><b>2. Configure Media, Limits & Fallbacks:</b> Select your primary media and optional fallback tiers for tail volumes. Set a volume count limit per tier (<code>0</code> for unlimited). For USB Flash Drives or Custom sizes, enter manufacturer ratings (MB/GB) to auto-calculate the safe usable ceiling.</div>"
            f"<div class='step-card'><b>3. Step 1 — Run Simulation (Dry Run):</b> Inspect the allocation breakdown, including used capacity, remaining free space, and media tiers. Underfilled volumes (&lt; 70% full) are highlighted in red with a <code>[&lt; 70% Full]</code> indicator. Use <b>Save As Index</b> or <b>Save Index (Exclude Tail)</b> to export catalog text files.</div>"
            f"<div class='step-card'><b>4. Step 2 — Generate Hardlink Backup Trees:</b> Creates zero-byte NTFS hardlink folders ready for burning. The <b>Last Disc ID Created</b> indicator tracks the final volume's size, free space, and fill warnings.</div>"
            f"<div class='step-card'><b>5. Step 3 — Clean Staging Target:</b> Safely removes staging hardlinks after burning. Non-hardlinked files and source data are strictly preserved.</div>"
            f"<div class='step-card'><b>6. Step 4 — Purge Burned Files from Source:</b> Deletes verified source files for completed volumes while strictly preserving unburned tail volume files. Choose direct in-app Python deletion or export a double-clickable, Unicode-safe <code>.bat</code> script with explicit <code>(Y/N)</code> confirmation.</div>"
            f"<h2>CORE FEATURES</h2>"
            f"<p><b>4-Step Workflow Grid:</b> Intuitive sequential interface guiding you from pre-burn simulation to post-burn cleanup.</p>"
            f"<p><b>Source Purge & Tail Protection:</b> Safely reclaims source disk space after burning while keeping leftover tail files intact for replenishment.</p>"
            f"<p><b>Universal Unicode Cleanup Scripts:</b> Generates self-bootstrapping <code>.bat</code> scripts powered by PowerShell that seamlessly handle Asian characters, division slashes (<code>∕</code>), and special characters on Windows.</p>"
            f"<p><b>Selective Index Export:</b> Export complete index reports or easily omit underfilled tail volumes with auto-recalculated summaries.</p>"
            f"<p><b>Tail Capacity Warnings:</b> Real-time visual alerts (<code>[&lt; 70% Full]</code>) on underutilized volumes across both the simulation tree and main status label.</p>"
            f"<p><b>Tier Volume Limits:</b> Enforce maximum volume counts per media tier (<code>0 = unlimited</code>), automatically stepping down to fallback media.</p>"
            f"<p><b>Zero Storage Duplication:</b> Native NTFS hardlinks allow staging multi-disc sets without using additional hard drive storage.</p>"
            f"<h2>DEPENDENCIES</h2>"
            f"<p><b>Python:</b> Built with Python 3.14.5.</p>"
            f"<p><b>PyQt6:</b> Orchestrates the graphical user interface.</p>"
            f"<hr><p style='text-align: center; color: #888888;'><small>Licensed under GPLv3. See the <b>About</b> section for full details.</small></p>"
        )

        text_browser.setHtml(manual_text)
        layout.addWidget(text_browser)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.exec()

    def show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.resize(550, 425)
        
        layout = QVBoxLayout(dialog)
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 13px;
                line-height: 1.5;
                color: palette(text);
                background-color: palette(base);
                border: none;
                padding: 10px;
            }
            h1 { color: #007acc; font-size: 20px; margin-bottom: 5px; }
            b { color: #007acc; }
            a { color: #007acc; text-decoration: none; }
            hr { border: 0; border-top: 1px solid #444; margin: 10px 0; }
        """)
        
        about_text = (
            f"<h1><a href=\"https://git.disroot.org/pwshAgyjkcrg761/volumespan-py\">VolumeSpan</a> v{APP_VERSION}</h1>"
            "<p>Copyright (C) 2026 <b>pwshAgyjkcrg761</b><br>"
            "Licensed under <b>GPLv3</b></p>"
            "<p>This program is free software: you can redistribute it and/or modify "
            "it under the terms of the GNU General Public License as published by "
            "the Free Software Foundation, either version 3 of the License, or "
            "(at your option) any later version.</p>"
            "<p>This program is distributed in the hope that it will be useful, "
            "but WITHOUT ANY WARRANTY; without even the implied warranty of "
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
            "GNU General Public License for more details.</p>"
            "<p>Official License: <a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">gnu.org/licenses/gpl-3.0.html</a></p>"
            "<hr>"
            "<p><b>Icon Credits:</b><br>"
            "'Compact Disc Cd SVG Vector' via <a href=\"https://www.svgrepo.com/svg/224282/compact-disc-cd\">SVGRepo</a>.<br>"
            "Used under <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0 License</a>. Modified by pwshAgyjkcrg761.</p>"
        )
        text_browser.setHtml(about_text)
        layout.addWidget(text_browser)
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = VolumeSpanApp()
    window.show()
    sys.exit(app.exec())