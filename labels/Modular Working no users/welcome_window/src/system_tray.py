"""
System tray icon implementation using win32gui.
Provides functionality for adding the application to the system tray with a context menu.
"""

import win32gui
import win32con
import win32api
import os

class SystemTrayIcon:
    WM_NOTIFY_ICON = win32con.WM_USER + 20
    WM_TASKBAR_RESTART = win32gui.RegisterWindowMessage("TaskbarCreated")
    
    def __init__(self, window):
        """Initialize system tray icon."""
        self.window = window
        self.hwnd = window.winfo_id()  # Use the main window's handle
        self.icon = None  # Store icon handle
        self.visible = True  # Track icon visibility
        self._create_icon()
        
        # Create message map
        message_map = {
            self.WM_NOTIFY_ICON: self._on_notify,
            self.WM_TASKBAR_RESTART: self._create_icon,
            win32con.WM_DISPLAYCHANGE: self._create_icon  # Handle display changes
        }
        
        # Replace the window's original WndProc
        self.oldWndProc = win32gui.SetWindowLong(
            self.hwnd,
            win32con.GWL_WNDPROC,
            self._create_window_proc(message_map)
        )
    
    def __del__(self):
        """Clean up resources."""
        try:
            self.remove_icon()
        except:
            pass

    def remove_icon(self):
        """Remove the tray icon."""
        if self.icon:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 0))
            win32gui.DestroyIcon(self.icon)
            self.icon = None
    
    def _create_window_proc(self, message_map):
        """Create a window procedure function."""
        def wnd_proc(hwnd, msg, wparam, lparam):
            # Handle registered messages
            if msg in message_map:
                message_map[msg](hwnd, msg, wparam, lparam)
            # Call the original window procedure for other messages
            return win32gui.CallWindowProc(self.oldWndProc, hwnd, msg, wparam, lparam)
        return wnd_proc
    
    def _create_icon(self, *args):
        """Create and add the tray icon."""
        if not self.visible:
            return

        try:
            # Remove existing icon if any
            self.remove_icon()
            
            # Use custom icon from assets
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'window.ico')
            self.icon = win32gui.LoadImage(
                0, icon_path, win32con.IMAGE_ICON,
                16, 16,  # Specify size explicitly
                win32con.LR_LOADFROMFILE
            )
            
            flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
            nid = (
                self.hwnd,
                0,
                flags,
                self.WM_NOTIFY_ICON,
                self.icon,
                "Label Maker V3"
            )
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        except Exception as e:
            print(f"Error creating tray icon: {e}")
            if self.icon:
                try:
                    win32gui.DestroyIcon(self.icon)
                except:
                    pass
                self.icon = None
    
    def _on_notify(self, hwnd, msg, wparam, lparam):
        """Handle tray icon notifications."""
        if lparam == win32con.WM_LBUTTONUP:
            # Single left click - toggle window visibility
            if self.window.state() == 'iconic':
                self.window._show_window()
            else:
                self.window.iconify()
                self.window._on_minimize()
        elif lparam == win32con.WM_LBUTTONDBLCLK:
            # Double click - always show window
            self.window._show_window()
        elif lparam == win32con.WM_RBUTTONUP:
            self._show_menu()
    
    def _exit_application(self):
        """Exit the application properly."""
        if self.window:
            self.window._on_close()

    def _restore_window(self):
        """Restore the window properly."""
        if self.window:
            if self.window.state() == 'iconic':
                self.window.deiconify()
            elif self.window.state() == 'withdrawn':
                self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
    
    def _show_menu(self):
        """Show context menu."""
        menu = win32gui.CreatePopupMenu()
        try:
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "Show")
            win32gui.AppendMenu(menu, win32con.MF_STRING, 2, "Exit")
            
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            
            selected = win32gui.TrackPopupMenu(
                menu,
                win32con.TPM_LEFTALIGN | win32con.TPM_BOTTOMALIGN | win32con.TPM_RETURNCMD,
                pos[0],
                pos[1],
                0,
                self.hwnd,
                None
            )
            
            if selected == 1:  # Show
                self.window._show_window()
            elif selected == 2:  # Exit
                self._exit_application()
        finally:
            win32gui.DestroyMenu(menu)  # Always cleanup the menu
    
    def destroy(self):
        """Remove tray icon and cleanup resources."""
        try:
            # Remove the tray icon
            self.remove_icon()
            
            # Restore original WndProc if it exists
            if hasattr(self, 'oldWndProc'):
                try:
                    win32gui.SetWindowLong(
                        self.hwnd,
                        win32con.GWL_WNDPROC,
                        self.oldWndProc
                    )
                except:
                    pass  # Window might already be destroyed
        except Exception as e:
            print(f"Error cleaning up tray icon: {e}")
