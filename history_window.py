#!/usr/bin/env python3
"""
History window UI for clipboard history picker
"""

import tkinter as tk
from tkinter import ttk, font
import time
from datetime import datetime

class HistoryWindow:
    def __init__(self, history_manager, on_select_callback=None):
        self.history = history_manager
        self.on_select = on_select_callback
        self.selected_item = None
        
        # Create window
        self.window = tk.Tk()
        self.window.title("Clipboard History")
        self.window.geometry("600x500")
        
        # Set window to float above others
        self.window.attributes('-topmost', True)
        self.window.lift()
        
        # Configure style
        self.setup_style()
        
        # Build UI
        self.build_ui()
        
        # Load history
        self.refresh_history()
        
        # Bind shortcuts
        self.bind_shortcuts()
    
    def setup_style(self):
        """Configure the visual style"""
        self.window.configure(bg='#f0f0f0')
        
        # Create custom fonts
        self.title_font = font.Font(family="SF Pro Display", size=14, weight="bold")
        self.item_font = font.Font(family="SF Mono", size=11)
        self.meta_font = font.Font(family="SF Pro Text", size=9)
    
    def build_ui(self):
        """Build the user interface"""
        # Top frame with search
        top_frame = tk.Frame(self.window, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search bar
        tk.Label(top_frame, text="Search:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.focus()
        
        # Filter buttons
        self.filter_frame = tk.Frame(top_frame, bg='#f0f0f0')
        self.filter_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.show_bitcoin = tk.BooleanVar(value=False)
        bitcoin_btn = tk.Checkbutton(
            self.filter_frame, 
            text="₿ Bitcoin", 
            variable=self.show_bitcoin,
            command=self.refresh_history,
            bg='#f0f0f0'
        )
        bitcoin_btn.pack(side=tk.LEFT, padx=2)
        
        self.show_sensitive = tk.BooleanVar(value=False)
        sensitive_btn = tk.Checkbutton(
            self.filter_frame,
            text="🔒 Sensitive",
            variable=self.show_sensitive,
            command=self.refresh_history,
            bg='#f0f0f0'
        )
        sensitive_btn.pack(side=tk.LEFT, padx=2)
        
        # History list frame
        list_frame = tk.Frame(self.window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # History listbox with custom rendering
        self.history_list = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=self.item_font,
            selectmode=tk.SINGLE,
            height=15,
            bg='white',
            selectbackground='#007AFF',
            selectforeground='white'
        )
        self.history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_list.yview)
        
        # Bind selection
        self.history_list.bind('<<ListboxSelect>>', self.on_select_item)
        self.history_list.bind('<Double-Button-1>', self.on_double_click)
        
        # Bottom frame with actions
        bottom_frame = tk.Frame(self.window, bg='#f0f0f0')
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Statistics label
        self.stats_label = tk.Label(
            bottom_frame,
            text="0 items",
            font=self.meta_font,
            bg='#f0f0f0',
            fg='#666'
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        button_frame.pack(side=tk.RIGHT)
        
        self.paste_btn = tk.Button(
            button_frame,
            text="Paste (⏎)",
            command=self.paste_selected,
            state=tk.DISABLED
        )
        self.paste_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_btn = tk.Button(
            button_frame,
            text="Delete (⌫)",
            command=self.delete_selected,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        self.pin_btn = tk.Button(
            button_frame,
            text="Pin (P)",
            command=self.toggle_pin,
            state=tk.DISABLED
        )
        self.pin_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            button_frame,
            text="Clear Sensitive",
            command=self.clear_sensitive,
            fg='red'
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            button_frame,
            text="Close (Esc)",
            command=self.close_window
        ).pack(side=tk.LEFT, padx=2)
        
        # Preview area
        preview_frame = tk.LabelFrame(self.window, text="Preview", bg='#f0f0f0')
        preview_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.preview_text = tk.Text(
            preview_frame,
            height=3,
            font=self.item_font,
            wrap=tk.WORD,
            bg='#f9f9f9',
            state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.X, padx=5, pady=5)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.window.bind('<Escape>', lambda e: self.close_window())
        self.window.bind('<Return>', lambda e: self.paste_selected())
        self.window.bind('<BackSpace>', lambda e: self.delete_selected())
        self.window.bind('<Delete>', lambda e: self.delete_selected())
        self.window.bind('p', lambda e: self.toggle_pin())
        self.window.bind('P', lambda e: self.toggle_pin())
        
        # Number shortcuts for quick paste
        for i in range(1, 10):
            self.window.bind(str(i), lambda e, idx=i-1: self.quick_paste(idx))
    
    def refresh_history(self):
        """Refresh the history list"""
        self.history_list.delete(0, tk.END)
        self.history_items = []
        
        # Get items based on filters
        if self.show_bitcoin.get():
            items = self.history.get_bitcoin_items()
        elif self.search_var.get():
            items = self.history.search(
                self.search_var.get(),
                include_sensitive=self.show_sensitive.get()
            )
        else:
            items = self.history.get_recent(
                count=50,
                include_sensitive=self.show_sensitive.get()
            )
        
        # Add items to list
        for idx, item in enumerate(items):
            # Format display text
            display = self.format_item_display(item, idx + 1)
            self.history_list.insert(tk.END, display)
            self.history_items.append(item)
            
            # Color code based on type
            if item.get('is_sensitive'):
                self.history_list.itemconfig(idx, fg='#d00')
            elif item.get('icon') == '₿':
                self.history_list.itemconfig(idx, fg='#f7931a')  # Bitcoin orange
            elif item.get('icon') == '⚡':
                self.history_list.itemconfig(idx, fg='#792de4')  # Lightning purple
        
        # Update statistics
        stats = self.history.get_statistics()
        self.stats_label.config(
            text=f"{len(items)} items | {stats['sensitive_items']} sensitive | "
                 f"{stats['bitcoin_items']} Bitcoin"
        )
    
    def format_item_display(self, item, number):
        """Format item for display in list"""
        icon = item.get('icon', '📋')
        display_text = item.get('display_text', item['text'][:50])
        
        # Add timestamp
        timestamp = datetime.fromtimestamp(item['timestamp'])
        time_str = timestamp.strftime('%H:%M')
        
        # Check if pinned
        pin_marker = '📌 ' if item['id'] in self.history.pinned_items else ''
        
        # Check if expiring
        expire_marker = ''
        if item.get('expire_at'):
            remaining = item['expire_at'] - time.time()
            if remaining > 0:
                expire_marker = f' ⏱{int(remaining)}s'
        
        # Format: [1] icon display_text (time) pin expire
        return f"[{number}] {pin_marker}{icon} {display_text} ({time_str}){expire_marker}"
    
    def on_search_change(self, *args):
        """Handle search text change"""
        self.refresh_history()
    
    def on_select_item(self, event):
        """Handle item selection"""
        selection = self.history_list.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.history_items):
                self.selected_item = self.history_items[idx]
                
                # Enable action buttons
                self.paste_btn.config(state=tk.NORMAL)
                self.delete_btn.config(state=tk.NORMAL)
                self.pin_btn.config(state=tk.NORMAL)
                
                # Update pin button text
                if self.selected_item['id'] in self.history.pinned_items:
                    self.pin_btn.config(text="Unpin (P)")
                else:
                    self.pin_btn.config(text="Pin (P)")
                
                # Show preview
                self.show_preview(self.selected_item)
    
    def show_preview(self, item):
        """Show item preview"""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        # Show limited preview for sensitive items
        if item.get('is_sensitive'):
            preview = item.get('display_text', '***hidden***')
        else:
            preview = item['text'][:500]
            if len(item['text']) > 500:
                preview += '...'
        
        self.preview_text.insert(1.0, preview)
        self.preview_text.config(state=tk.DISABLED)
    
    def on_double_click(self, event):
        """Handle double click - paste and close"""
        self.paste_selected()
    
    def paste_selected(self):
        """Paste selected item"""
        if self.selected_item and self.on_select:
            self.on_select(self.selected_item)
            self.close_window()
    
    def delete_selected(self):
        """Delete selected item"""
        if self.selected_item:
            self.history.delete_item(self.selected_item['id'])
            self.refresh_history()
            self.selected_item = None
            self.paste_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.pin_btn.config(state=tk.DISABLED)
    
    def toggle_pin(self):
        """Toggle pin status of selected item"""
        if self.selected_item:
            item_id = self.selected_item['id']
            if item_id in self.history.pinned_items:
                self.history.unpin_item(item_id)
            else:
                self.history.pin_item(item_id)
            self.refresh_history()
    
    def clear_sensitive(self):
        """Clear all sensitive items"""
        if tk.messagebox.askyesno("Clear Sensitive", 
                                  "Remove all sensitive items from history?"):
            self.history.clear_sensitive()
            self.refresh_history()
    
    def quick_paste(self, index):
        """Quick paste by number key"""
        if index < len(self.history_items):
            self.selected_item = self.history_items[index]
            self.paste_selected()
    
    def close_window(self):
        """Close the window"""
        self.window.destroy()
    
    def show(self):
        """Show the window"""
        self.window.mainloop()