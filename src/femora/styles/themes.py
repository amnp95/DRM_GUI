class Themes:
    # Refined dark theme colors
    DARK = {
        'bg_primary': '#1e1e1e',         # VSCode-like dark background
        'bg_secondary': '#252526',        # Slightly lighter
        'bg_tertiary': '#333333',         # For menus and highlights
        'text_primary': '#d4d4d4',        # Main text color
        'text_secondary': '#888888',      # Secondary text
        'accent_primary': '#0d7377',      # Teal accent
        'accent_secondary': '#007acc',    # Blue accent (VSCode-like)
        'accent_success': '#6a9955',      # Muted green
        'accent_warning': '#d19a66',      # Soft orange
        'accent_error': '#f14c4c',        # Soft red
        'border': '#454545',              # Subtle border
        'tab_active': '#1e1e1e',
        'tab_inactive': '#2d2d2d',
        'tooltip_bg': '#252526',
        'tooltip_text': '#d4d4d4',
        'tooltip_border': '#007acc'
    }
    
    # Light theme remains the same
    LIGHT = {
        'bg_primary': '#fafafa',
        'bg_secondary': '#f0f1f4',
        'bg_tertiary': '#e3e5e8',
        'text_primary': '#24283b',
        'text_secondary': '#565f89',
        'accent_primary': '#7c3aed',
        'accent_secondary': '#2563eb',
        'accent_success': '#059669',
        'accent_warning': '#d97706',
        'accent_error': '#dc2626',
        'border': '#e2e8f0',
        'tab_active': '#ffffff',
        'tab_inactive': '#f8fafc',
        'tooltip_bg': '#f8fafc',
        'tooltip_text': '#24283b',
        'tooltip_border': '#2563eb'
    }
        # Solarized theme
    # LIGHT = {
    #     'bg_primary': '#002b36',
    #     'bg_secondary': '#073642',
    #     'bg_tertiary': '#586e75',
    #     'text_primary': '#839496',
    #     'text_secondary': '#657b83',
    #     'accent_primary': '#b58900',
    #     'accent_secondary': '#268bd2',
    #     'accent_success': '#859900',
    #     'accent_warning': '#cb4b16',
    #     'accent_error': '#dc322f',
    #     'border': '#586e75',
    #     'tab_active': '#073642',
    #     'tab_inactive': '#002b36',
    #     'tooltip_bg': '#073642',
    #     'tooltip_text': '#839496',
    #     'tooltip_border': '#268bd2'
    # }
    
    # # Monokai theme
    # DARK = {
    #     'bg_primary': '#272822',
    #     'bg_secondary': '#3e3d32',
    #     'bg_tertiary': '#49483e',
    #     'text_primary': '#f8f8f2',
    #     'text_secondary': '#75715e',
    #     'accent_primary': '#a6e22e',
    #     'accent_secondary': '#66d9ef',
    #     'accent_success': '#a6e22e',
    #     'accent_warning': '#e6db74',
    #     'accent_error': '#f92672',
    #     'border': '#3e3d32',
    #     'tab_active': '#272822',
    #     'tab_inactive': '#3e3d32',
    #     'tooltip_bg': '#49483e',
    #     'tooltip_text': '#f8f8f2',
    #     'tooltip_border': '#66d9ef'
    # }

    # Nord theme
    # LIGHT = {
    #     'bg_primary': '#2E3440',           # Deep blue-gray background
    #     'bg_secondary': '#3B4252',         # Slightly lighter for widgets
    #     'bg_tertiary': '#434C5E',          # Light blue-gray for accents
    #     'text_primary': '#D8DEE9',         # Off-white text
    #     'text_secondary': '#B4BECC',       # Muted light blue
    #     'accent_primary': '#88C0D0',       # Soft cyan for accents
    #     'accent_secondary': '#81A1C1',     # Lighter blue
    #     'accent_success': '#A3BE8C',       # Green
    #     'accent_warning': '#EBCB8B',       # Yellow-orange
    #     'accent_error': '#BF616A',         # Soft red
    #     'border': '#4C566A',
    #     'tab_active': '#3B4252',
    #     'tab_inactive': '#2E3440',
    #     'tooltip_bg': '#4C566A',
    #     'tooltip_text': '#D8DEE9',
    #     'tooltip_border': '#81A1C1'
    # }
    
    # # Dracula theme
    # DARK = {
    #     'bg_primary': '#282A36',           # Dark background
    #     'bg_secondary': '#44475A',         # Slightly lighter dark
    #     'bg_tertiary': '#6272A4',          # Soft blue for highlights
    #     'text_primary': '#F8F8F2',         # Very light text
    #     'text_secondary': '#BD93F9',       # Lavender text
    #     'accent_primary': '#FF79C6',       # Bright pink
    #     'accent_secondary': '#8BE9FD',     # Cyan
    #     'accent_success': '#50FA7B',       # Green
    #     'accent_warning': '#F1FA8C',       # Yellow
    #     'accent_error': '#FF5555',         # Red
    #     'border': '#6272A4',
    #     'tab_active': '#44475A',
    #     'tab_inactive': '#282A36',
    #     'tooltip_bg': '#44475A',
    #     'tooltip_text': '#F8F8F2',
    #     'tooltip_border': '#8BE9FD'
    # }
    
    @staticmethod
    def get_base_style(colors):
        """
        Returns an enhanced base style without transitions
        """
        return f"""
        QMainWindow {{
            background-color: {colors['bg_primary']};
        }}
        
        QFrame {{
            background-color: {colors['bg_secondary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 4px;
        }}

        QHeaderView::section {{
            background-color: {colors['bg_tertiary']}; /* Or any suitable background */
            color: {colors['text_primary']};
            padding: 4px; /* Adjust vertical padding as needed */
            border: 1px solid {colors['border']};
            font-weight: bold; /* Optional: Make header text bold */
            min-height: 25px; /* Set a minimum height for the header */
        }}

        QTableWidget {{
            gridline-color: {colors['border']}; /* Optional: Set grid line color */
        }}

        QTableWidget QTableCornerButton::section {{
            background: {colors['bg_tertiary']}; /* Optional: Style the top-left corner */
            border: 1px solid {colors['border']};
        }}

        
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background-color: {colors['bg_secondary']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QTabBar {{
            background: transparent;
        }}
        
        QTabBar::tab {{
            background-color: {colors['tab_inactive']};
            color: {colors['text_secondary']};
            padding: 8px 16px;
            border: 1px solid {colors['border']};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['tab_active']};
            color: {colors['text_primary']};
            border-bottom: 2px solid {colors['accent_secondary']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_primary']};
        }}
        
        QSplitter::handle {{
            background-color: {colors['border']};
            margin: 1px;
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QMenuBar {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border-bottom: 1px solid {colors['border']};
            padding: 2px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['accent_secondary']};
        }}
        
        QMenu {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 24px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['accent_secondary']};
        }}
        
        QScrollBar:vertical {{
            border: none;
            background-color: {colors['bg_secondary']};
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['accent_secondary']};
            border-radius: 5px;
            min-height: 20px;
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {colors['bg_secondary']};
            height: 10px;
            border-radius: 5px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {colors['accent_secondary']};
            border-radius: 5px;
            min-width: 20px;
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        QPushButton {{
            background-color: {colors['accent_secondary']};
            color: {colors['bg_primary']};
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent_secondary']};
        }}
        
        QLineEdit {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {colors['accent_secondary']};
        }}
        
        QComboBox {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {colors['accent_secondary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}
        
        QSpinBox {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px;
        }}
        
        RichJupyterWidget {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            selection-background-color: {colors['accent_secondary']};
            border-radius: 8px;
        }}
        """
    
    @staticmethod
    def get_dynamic_style(theme, font_size=10):
        colors = theme
        
        dynamic_style = f"""
        * {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
            font-size: {font_size}pt !important;
        }}
        
        QMainWindow, QWidget {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            font-size: {font_size}pt !important;
        }}
        
        QToolTip {{
            background-color: {colors['tooltip_bg']};
            color: {colors['tooltip_text']};
            border: 2px solid {colors['tooltip_border']};
            border-radius: 8px;
            padding: 8px;
            font-size: {font_size}pt !important;
            opacity: 230;
        }}
        """
        
        return dynamic_style + Themes.get_base_style(colors)