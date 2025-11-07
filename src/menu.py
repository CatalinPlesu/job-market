import signal
import sys

class Menu:
    def __init__(self):
        self._selected_index = 0
        self._menu_title = "Menu"
        self._header = None
        self._footer = None
        self._menu_items = []
        self._menu_items_description = ["0. Exit"]

    def set_menu_title(self, title):
        self._menu_title = title

    def register_item(self, item):
        description = item.get_item_description()
        self._menu_items_description.append(f"{len(self._menu_items_description)}. {description}")
        self._menu_items.append(item)

    def run(self):
        running = True

        while running:
            try:
                self._draw_menu()
                
                key = self._get_key()
                
                if key == 'up' or key == 'k':
                    self._selected_index = (self._selected_index - 1 + len(self._menu_items_description)) % len(self._menu_items_description)
                elif key == 'down' or key == 'tab' or key == 'j':
                    self._selected_index = (self._selected_index + 1) % len(self._menu_items_description)
                elif key == 'enter' or key == 'right' or key == 'l':
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    if self._selected_index == 0:
                        running = False
                    else:
                        item = self._menu_items[self._selected_index - 1]
                        result = item.execute()
                        if result:
                            input("Press any key to return to menu...")
                elif key == 'escape' or key == 'left' or key == 'h':
                    running = False
                elif key.isdigit():
                    num = int(key)
                    if 0 <= num <= len(self._menu_items_description):
                        self._selected_index = num

            except KeyboardInterrupt:
                print("\n\nReceived interrupt signal (Ctrl+C). Exiting...")
                sys.exit(0)  # Changed from 'break' to 'sys.exit(0)'

        print("Exited Management Menu.")

    def set_item(self, item):
        for menu_item in self._menu_items:
            if hasattr(menu_item, 'load_item'):
                menu_item.load_item(item)

    def set_header(self, header):
        self._header = header

    def set_footer(self, footer):
        self._footer = footer

    def _get_key(self):
        import os
        if os.name == 'nt':  # Windows
            import msvcrt
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == '\r':  # Enter
                        return 'enter'
                    elif key == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    elif key == '\x08':  # Backspace
                        continue
                    elif key == '\x1b':  # Escape sequence
                        key2 = msvcrt.getch().decode('utf-8')
                        if key2 == '[':
                            key3 = msvcrt.getch().decode('utf-8')
                            if key3 == 'A':
                                return 'up'
                            elif key3 == 'B':
                                return 'down'
                            elif key3 == 'C':
                                return 'right'
                            elif key3 == 'D':
                                return 'left'
                        return 'escape'
                    elif key == '\t':  # Tab
                        return 'tab'
                    else:
                        return key
        else:  # Unix/Linux/Mac
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1).lower()
                if ord(key) == 13:  # Enter
                    return 'enter'
                elif ord(key) == 3:  # Ctrl+C
                    raise KeyboardInterrupt
                elif ord(key) == 27:  # Escape sequence
                    key2 = sys.stdin.read(1)
                    if key2 == '[':
                        key3 = sys.stdin.read(1)
                        if key3 == 'A':
                            return 'up'
                        elif key3 == 'B':
                            return 'down'
                        elif key3 == 'C':
                            return 'right'
                        elif key3 == 'D':
                            return 'left'
                    return 'escape'
                elif ord(key) == 9:  # Tab
                    return 'tab'
                elif ord(key) == 127:  # Backspace
                    return 'backspace'
                else:
                    return key
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _draw_menu(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        title = f"=== {self._menu_title} ==="
        print(title)
        
        if self._header:
            print('-' * len(title))
            print(self._header)
            print('-' * len(title))
        
        print()

        for i, description in enumerate(self._menu_items_description):
            if i == self._selected_index:
                print(f"\033[7m {description} \033[0m")
            else:
                print(f" {description} ")

        print("\nUse  ←↓↑→  to navigate, Enter to select, or type number. Esc to exit.")

        if self._footer:
            print('-' * len(title))
            print(self._footer)
            print('-' * len(title))
