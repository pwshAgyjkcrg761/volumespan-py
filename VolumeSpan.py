# ==============================================================================
# SCRIPT: VolumeSpan.py
# VERSION: 2026.09.04__08.40.53
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
                             QMessageBox, QDialog, QComboBox, QDoubleSpinBox,
                             QTextBrowser, QDialogButtonBox, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtGui import QActionGroup, QPalette, QColor, QIcon

APP_VERSION = "2026.09.04__08.40.53"

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
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        
        internal_dir = os.path.join(script_dir, "VolumeSpan_internal")
        os.makedirs(internal_dir, exist_ok=True)
        self.config_file = os.path.join(internal_dir, "VolumeSpan.config.json")
        
        if sys.platform == "win32":
            myappid = f"pwshAgyjkcrg761.volumespan.{APP_VERSION}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        icon_path = os.path.join(internal_dir, "icons", "volumespan_cd_icon.svg")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)
            
        self.default_size = (680, 368)
        
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
            "Mini DVD-R (1.4 GB)", "CD-R (700 MB)", "Mini CD-R (210 MB)", "Custom Size"
        ]
        fallback_items = ["None (Disabled)"] + media_items

        # Primary Media
        cap_layout = QHBoxLayout()
        cap_layout.addWidget(QLabel("Primary Media:"))
        self.combo_primary_media = QComboBox()
        self.combo_primary_media.addItems(media_items)
        self.combo_primary_media.currentIndexChanged.connect(self.primary_media_changed)
        cap_layout.addWidget(self.combo_primary_media)
        
        cap_layout.addWidget(QLabel("Ceiling (GiB):"))
        self.spin_ceiling = QDoubleSpinBox()
        self.spin_ceiling.setRange(0.1, 1000.0)
        self.spin_ceiling.setDecimals(2)
        self.spin_ceiling.setValue(118.00)
        cap_layout.addWidget(self.spin_ceiling)
        layout.addLayout(cap_layout)

        # Fallback 1
        fb1_layout = QHBoxLayout()
        fb1_layout.addWidget(QLabel("Fallback 1 Media:"))
        self.combo_fb1_media = QComboBox()
        self.combo_fb1_media.addItems(fallback_items)
        self.combo_fb1_media.currentIndexChanged.connect(lambda idx: self.fallback_changed(idx, self.spin_fb1_ceiling))
        fb1_layout.addWidget(self.combo_fb1_media)
        
        fb1_layout.addWidget(QLabel("Ceiling (GiB):"))
        self.spin_fb1_ceiling = QDoubleSpinBox()
        self.spin_fb1_ceiling.setRange(0.1, 1000.0)
        self.spin_fb1_ceiling.setDecimals(2)
        self.spin_fb1_ceiling.setValue(93.00)
        fb1_layout.addWidget(self.spin_fb1_ceiling)
        layout.addLayout(fb1_layout)

        # Fallback 2
        fb2_layout = QHBoxLayout()
        fb2_layout.addWidget(QLabel("Fallback 2 Media:"))
        self.combo_fb2_media = QComboBox()
        self.combo_fb2_media.addItems(fallback_items)
        self.combo_fb2_media.currentIndexChanged.connect(lambda idx: self.fallback_changed(idx, self.spin_fb2_ceiling))
        fb2_layout.addWidget(self.combo_fb2_media)
        
        fb2_layout.addWidget(QLabel("Ceiling (GiB):"))
        self.spin_fb2_ceiling = QDoubleSpinBox()
        self.spin_fb2_ceiling.setRange(0.1, 1000.0)
        self.spin_fb2_ceiling.setDecimals(2)
        self.spin_fb2_ceiling.setValue(46.50)
        fb2_layout.addWidget(self.spin_fb2_ceiling)
        layout.addLayout(fb2_layout)

        # Fallback 3
        fb3_layout = QHBoxLayout()
        fb3_layout.addWidget(QLabel("Fallback 3 Media:"))
        self.combo_fb3_media = QComboBox()
        self.combo_fb3_media.addItems(fallback_items)
        self.combo_fb3_media.currentIndexChanged.connect(lambda idx: self.fallback_changed(idx, self.spin_fb3_ceiling))
        fb3_layout.addWidget(self.combo_fb3_media)
        
        fb3_layout.addWidget(QLabel("Ceiling (GiB):"))
        self.spin_fb3_ceiling = QDoubleSpinBox()
        self.spin_fb3_ceiling.setRange(0.1, 1000.0)
        self.spin_fb3_ceiling.setDecimals(2)
        self.spin_fb3_ceiling.setValue(23.20)
        fb3_layout.addWidget(self.spin_fb3_ceiling)
        layout.addLayout(fb3_layout)
        
        # Action Buttons
        btn_dry_run = QPushButton("Run Simulation (Dry Run)")
        btn_dry_run.clicked.connect(self.run_dry_run)
        layout.addWidget(btn_dry_run)
        
        btn_execute = QPushButton("Generate Hardlink Backup Trees")
        btn_execute.clicked.connect(self.execute_hardlinks)
        layout.addWidget(btn_execute)

        btn_cleanup = QPushButton("Clean Staging Target (Remove Hardlinks)")
        btn_cleanup.clicked.connect(self.cleanup_staging)
        layout.addWidget(btn_cleanup)
        layout.addStretch()
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

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
        return f"Custom ({gib:.2f} GiB)"

    def primary_media_changed(self, index):
        # 0: BDXL QL, 1: BDXL TL, 2: BD-R DL, 3: BD-R SL, 4: DVD-9, 5: DVD-5, 6: Mini DVD-R, 7: CD-R, 8: Mini CD-R
        presets = {0: 118.00, 1: 93.00, 2: 46.50, 3: 23.20, 4: 7.90, 5: 4.35, 6: 1.36, 7: 0.68, 8: 0.19}
        if index in presets:
            self.spin_ceiling.setValue(presets[index])

    def fallback_changed(self, index, spin_target):
        # Index 0 is "None (Disabled)"; presets start from index 1
        presets = {1: 118.00, 2: 93.00, 3: 46.50, 4: 23.20, 5: 7.90, 6: 4.35, 7: 1.36, 8: 0.68, 9: 0.19}
        if index in presets:
            spin_target.setValue(presets[index])

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
        primary_ceiling = int(self.spin_ceiling.value() * 1024 * 1024 * 1024)
        
        fallbacks = []
        if self.combo_fb1_media.currentIndex() > 0:
            fallbacks.append(int(self.spin_fb1_ceiling.value() * 1024 * 1024 * 1024))
        if self.combo_fb2_media.currentIndex() > 0:
            fallbacks.append(int(self.spin_fb2_ceiling.value() * 1024 * 1024 * 1024))
        if self.combo_fb3_media.currentIndex() > 0:
            fallbacks.append(int(self.spin_fb3_ceiling.value() * 1024 * 1024 * 1024))

        # Sort active ceilings strictly largest -> smallest
        raw_ceilings = [primary_ceiling] + fallbacks
        sorted_ceilings = sorted(list(set(raw_ceilings)), reverse=True)

        if not sorted_ceilings:
            return None

        max_capacity = sorted_ceilings[0]

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

        all_files.sort(key=lambda x: x[0])

        # Pre-check: Fail immediately if any file exceeds largest selected media capacity
        for rel_path, full_path, fsize in all_files:
            if fsize > max_capacity:
                fsize_gib = fsize / (1024**3)
                max_gib = max_capacity / (1024**3)
                QMessageBox.critical(
                    self, 
                    "File Exceeds Media Capacity", 
                    f"Unable to partition archive.\n\n"
                    f"The following file exceeds the largest selected media tier ({max_gib:.2f} GiB):\n"
                    f"• {rel_path} ({fsize_gib:.2f} GiB)\n\n"
                    f"Please select a larger media format or remove the oversized file."
                )
                return None

        discs = []
        start_disc_id = self.disc_id_input.text().strip() or "BD-0001"
        current_disc_label = start_disc_id

        # Determine initial disc capacity (step down if all data fits in a smaller fallback tier)
        total_remaining = sum(f[2] for f in all_files)
        valid_fallbacks = [c for c in sorted_ceilings if total_remaining <= c]
        initial_ceiling = min(valid_fallbacks) if valid_fallbacks else max_capacity

        current_disc = {"label": current_disc_label, "files": [], "size": 0, "ceiling": initial_ceiling}

        for i, (rel_path, full_path, fsize) in enumerate(all_files):
            # Check if file fits on current disc
            if current_disc["size"] + fsize <= current_disc["ceiling"]:
                current_disc["files"].append((rel_path, full_path, fsize))
                current_disc["size"] += fsize
            else:
                # Close current disc
                if current_disc["files"]:
                    discs.append(current_disc)
                    current_disc_label = increment_disc_id(current_disc_label)

                # Look ahead: calculate total remaining unallocated bytes (including current file)
                remaining_bytes = sum(f[2] for f in all_files[i:])

                # Default to largest media tier for all standard discs
                next_ceiling = max_capacity

                # If all remaining data can fit into a smaller active fallback tier, step down
                valid_fallbacks = [c for c in sorted_ceilings if remaining_bytes <= c]
                if valid_fallbacks:
                    next_ceiling = min(valid_fallbacks)

                # Ensure single file fits inside chosen ceiling
                if fsize > next_ceiling:
                    next_ceiling = next(c for c in sorted_ceilings if fsize <= c)

                current_disc = {
                    "label": current_disc_label,
                    "files": [(rel_path, full_path, fsize)],
                    "size": fsize,
                    "ceiling": next_ceiling
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
        tree.setHeaderLabels(["Disc / Relative Path", "Size", "Media Type"])
        tree.setColumnWidth(0, 420)
        tree.setColumnWidth(1, 100)

        total_bytes = 0

        for d in discs:
            disc_item = QTreeWidgetItem(tree)
            pct = (d["size"] / d["ceiling"]) * 100 if d["ceiling"] > 0 else 0.0
            media_name = self._get_media_name_from_ceiling(d["ceiling"])
            disc_item.setText(0, f"{d['label']} ({len(d['files'])} files) - {pct:.1f}% filled")
            disc_item.setText(1, f"{d['size'] / (1024**3):.2f} GiB")
            disc_item.setText(2, media_name)
            total_bytes += d["size"]

            for rel_path, _, fsize in d["files"]:
                file_item = QTreeWidgetItem(disc_item)
                file_item.setText(0, rel_path)
                file_item.setText(1, f"{fsize / (1024**2):.2f} MiB")
                file_item.setText(2, "")

        d_layout.addWidget(tree)
        
        summary_label = QLabel(f"Total Discs: {len(discs)} | Total Data: {total_bytes / (1024**3):.2f} GiB")
        d_layout.addWidget(summary_label)

        def save_index():
            if len(discs) == 1:
                suggested_filename = f"{discs[0]['label']}.txt"
            else:
                suggested_filename = f"{discs[0]['label']} - {discs[-1]['label']}.txt"

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
                    f.write(f"Total Discs: {len(discs)} | Total Data: {total_bytes / (1024**3):.2f} GiB\n")
                    f.write(f"Source: {self.source_directory}\n")
                    f.write(f"Staging Target: {self.target_directory}\n")
                    f.write("=" * 80 + "\n\n")

                    for d in discs:
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
        btn_save_index.clicked.connect(save_index)
        btn_layout.addWidget(btn_save_index)
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

            last_disc_id = discs[-1]["label"]
            self.lbl_last_disc.setText(f"Last Disc ID Created: {last_disc_id}")
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
                    self.spin_ceiling.setValue(config.get("ceiling_gib", 118.00))

                    idx_fb1 = min(config.get("fb1_media_index", 0), max_fallback)
                    self.combo_fb1_media.setCurrentIndex(idx_fb1)
                    self.spin_fb1_ceiling.setValue(config.get("fb1_ceiling_gib", 93.00))

                    idx_fb2 = min(config.get("fb2_media_index", 0), max_fallback)
                    self.combo_fb2_media.setCurrentIndex(idx_fb2)
                    self.spin_fb2_ceiling.setValue(config.get("fb2_ceiling_gib", 46.50))

                    idx_fb3 = min(config.get("fb3_media_index", 0), max_fallback)
                    self.combo_fb3_media.setCurrentIndex(idx_fb3)
                    self.spin_fb3_ceiling.setValue(config.get("fb3_ceiling_gib", 23.20))
                    
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

        self.settings.setValue("fb1_ceiling_gib", self.spin_fb1_ceiling.value())
        self.settings.setValue("fb1_media_index", self.combo_fb1_media.currentIndex())

        self.settings.setValue("fb2_ceiling_gib", self.spin_fb2_ceiling.value())
        self.settings.setValue("fb2_media_index", self.combo_fb2_media.currentIndex())

        self.settings.setValue("fb3_ceiling_gib", self.spin_fb3_ceiling.value())
        self.settings.setValue("fb3_media_index", self.combo_fb3_media.currentIndex())

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
        dialog.resize(650, 550)
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
            f"<p>VolumeSpan is an automated optical disc backup staging utility designed to partition local directory trees sequentially into fixed-capacity volumes (e.g., <b>BD-0001</b>, <b>BD-0002</b>) using native NTFS hardlinks.</p>"
            f"<h2>USAGE WORKFLOW</h2>"
            f"<div class='step-card'><b>1. Select Source:</b> Choose the local folder tree you wish to split and archive.</div>"
            f"<div class='step-card'><b>2. Select Staging Target:</b> Pick an output folder on the <b>same local drive volume</b> to store the generated disc structures.</div>"
            f"<div class='step-card'><b>3. Configure Media & Fallbacks:</b> Choose your primary media preset and optional fallback tiers for tail volumes, or define custom GiB ceilings.</div>"
            f"<div class='step-card'><b>4. Run Simulation & Export Index:</b> Click <b>'Run Simulation (Dry Run)'</b> to view a detailed allocation breakdown of discs and media sizes before writing. Click <b>'Save As Index'</b> to export a formatted text index file of the disc set.</div>"
            f"<div class='step-card'><b>5. Generate Hardlinks:</b> Click <b>'Generate Hardlink Backup Trees'</b> to assemble zero-byte staging folders ready for disc authoring.</div>"
            f"<div class='step-card'><b>6. Clean Staging:</b> Click <b>'Clean Staging Target (Remove Hardlinks)'</b> to safely delete staging trees after burning. Non-hardlinked files are preserved.</div>"
            f"<h2>CORE FEATURES</h2>"
            f"<p><b>Multi-Tier Media Fallbacks:</b> Automatically steps down the final volume (or small archives) to smaller optical formats to conserve media.</p>"
            f"<p><b>Zero Storage Duplication:</b> Utilizes native NTFS hardlinks so staging folders consume zero extra storage space on your drive.</p>"
            f"<p><b>Deterministic Sequential Splits:</b> Preserves alphabetical and directory order across disc volumes for straightforward data restoration.</p>"
            f"<p><b>Index Report Export:</b> Generates structured text index reports detailing the exact disc allocation and file paths across the entire backup set.</p>"
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
            f"<h1>VolumeSpan v{APP_VERSION}</h1>"
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
            "Used under CC0 License. Modified by pwshAgyjkcrg761.</p>"
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