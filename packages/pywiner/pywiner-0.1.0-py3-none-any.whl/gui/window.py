import ctypes
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID

class Window:
    def __init__(self, title=None, width=400, height=300):
        self.title = title if title else "My Winpy Window"
        self.width = width
        self.height = height
        self.hwnd = None

    def create(self):
        WNDPROC = ctypes.WINFUNCTYPE(LPVOID, HWND, UINT, WPARAM, LPARAM)
        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == 2:
                ctypes.windll.user32.PostQuitMessage(0)
                return 0
            return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        
        wc = ctypes.wintypes.WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(wc)
        wc.lpfnWndProc = WNDPROC(wnd_proc)
        wc.hInstance = ctypes.windll.kernel32.GetModuleHandleW(None)
        wc.lpszClassName = "WinpyWindowClass"
        ctypes.windll.user32.RegisterClassExW(ctypes.byref(wc))

        self.hwnd = ctypes.windll.user32.CreateWindowExW(
            0,
            "WinpyWindowClass",
            self.title,
            0x00C00000 | 0x00080000 | 0x00040000,
            ctypes.windll.user32.CW_USEDEFAULT,
            ctypes.windll.user32.CW_USEDEFAULT,
            self.width,
            self.height,
            None,
            None,
            wc.hInstance,
            None
        )

        ctypes.windll.user32.ShowWindow(self.hwnd, 1)
        ctypes.windll.user32.UpdateWindow(self.hwnd)

    def run(self):
        msg = ctypes.wintypes.MSG()
        lp_msg = ctypes.byref(msg)
        while ctypes.windll.user32.GetMessageW(lp_msg, 0, 0, 0) != 0:
            ctypes.windll.user32.TranslateMessage(lp_msg)
            ctypes.windll.user32.DispatchMessageW(lp_msg)

if __name__ == '__main__':
    win = Window()
    win.create()
    win.run()