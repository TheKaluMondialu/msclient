#!/usr/bin/env python3
"""
Theme and styling constants for CS 1.6 Master Server GUI.
Provides color schemes, fonts, and visual design system.
"""

# Color Schemes
class Colors:
    """Modern color palette for the application."""
    
    # Primary colors - Modern blue gradient
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1d4ed8"
    PRIMARY_LIGHT = "#3b82f6"
    PRIMARY_GRADIENT_START = "#3b82f6"
    PRIMARY_GRADIENT_END = "#2563eb"
    
    # Accent colors - Vibrant purple
    ACCENT = "#8b5cf6"
    ACCENT_DARK = "#7c3aed"
    ACCENT_LIGHT = "#a78bfa"
    
    # Status colors - Modern palette
    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    SUCCESS_LIGHT = "#34d399"
    WARNING = "#f59e0b"
    WARNING_DARK = "#d97706"
    WARNING_LIGHT = "#fbbf24"
    ERROR = "#ef4444"
    ERROR_DARK = "#dc2626"
    ERROR_LIGHT = "#f87171"
    INFO = "#3b82f6"
    INFO_DARK = "#2563eb"
    INFO_LIGHT = "#60a5fa"
    
    # Text colors
    TEXT_PRIMARY = "#1f2937"
    TEXT_SECONDARY = "#6b7280"
    TEXT_DISABLED = "#9ca3af"
    TEXT_WHITE = "#ffffff"
    TEXT_MUTED = "#9ca3af"
    
    # Background colors (Light theme) - Modern whites and grays
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f9fafb"
    BG_TERTIARY = "#f3f4f6"
    BG_DARK = "#e5e7eb"
    BG_CARD = "#ffffff"
    BG_HOVER = "#f3f4f6"
    
    # Background colors (Dark theme)
    BG_DARK_PRIMARY = "#111827"
    BG_DARK_SECONDARY = "#1f2937"
    BG_DARK_TERTIARY = "#374151"
    BG_DARK_LIGHT = "#4b5563"
    BG_DARK_CARD = "#1f2937"
    BG_DARK_HOVER = "#374151"
    
    # Border colors
    BORDER_LIGHT = "#e5e7eb"
    BORDER_DARK = "#374151"
    BORDER_ACCENT = "#3b82f6"
    
    # Special purpose
    HIGHLIGHT = "#fef3c7"
    SHADOW = "#00000015"
    OVERLAY = "#00000080"
    CARD_SHADOW = "#0000001a"
    
    # Gradient definitions
    GRADIENT_PRIMARY = "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
    GRADIENT_WARNING = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
    GRADIENT_ACCENT = "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"


class DarkColors:
    """Dark theme color palette."""
    
    PRIMARY = "#2196f3"
    PRIMARY_DARK = "#1976d2"
    PRIMARY_LIGHT = "#64b5f6"
    
    ACCENT = "#00bcd4"
    ACCENT_DARK = "#0097a7"
    ACCENT_LIGHT = "#4dd0e1"
    
    SUCCESS = "#66bb6a"
    SUCCESS_DARK = "#4caf50"
    WARNING = "#ffa726"
    WARNING_DARK = "#ff9800"
    ERROR = "#ef5350"
    ERROR_DARK = "#f44336"
    INFO = "#42a5f5"
    INFO_DARK = "#2196f3"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_DISABLED = "#6e6e6e"
    
    BG_PRIMARY = "#1e1e1e"
    BG_SECONDARY = "#2d2d2d"
    BG_TERTIARY = "#383838"
    BG_LIGHT = "#424242"
    
    BORDER = "#424242"
    HIGHLIGHT = "#ffeb3b"
    SHADOW = "#00000050"
    OVERLAY = "#000000a0"


# Font settings
class Fonts:
    """Font family and size constants."""
    
    # Font families
    FAMILY_DEFAULT = "Segoe UI"
    FAMILY_MONO = "Consolas"
    FAMILY_FALLBACK = ["Arial", "Helvetica", "sans-serif"]
    
    # Font sizes (reduced for compact UI)
    SIZE_TINY = 7
    SIZE_SMALL = 8
    SIZE_NORMAL = 9
    SIZE_MEDIUM = 10
    SIZE_LARGE = 11
    SIZE_XLARGE = 12
    SIZE_TITLE = 13
    SIZE_HEADER = 14
    SIZE_DISPLAY = 16
    
    # Font weights
    WEIGHT_LIGHT = "normal"
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"


# Layout constants
class Layout:
    """Layout spacing and sizing constants."""
    
    # Padding (reduced for compact UI)
    PADDING_TINY = 1
    PADDING_SMALL = 3
    PADDING_NORMAL = 5
    PADDING_MEDIUM = 8
    PADDING_LARGE = 10
    PADDING_XLARGE = 15
    
    # Margins (reduced for compact UI)
    MARGIN_TINY = 1
    MARGIN_SMALL = 3
    MARGIN_NORMAL = 5
    MARGIN_MEDIUM = 8
    MARGIN_LARGE = 10
    
    # Border radius
    RADIUS_SMALL = 2
    RADIUS_NORMAL = 3
    RADIUS_MEDIUM = 5
    RADIUS_LARGE = 8
    
    # Widget sizes (reduced for compact UI)
    BUTTON_HEIGHT = 24
    BUTTON_WIDTH = 80
    INPUT_HEIGHT = 22
    HEADER_HEIGHT = 35
    STATUSBAR_HEIGHT = 20
    TOOLBAR_HEIGHT = 30
    
    # Window dimensions (more compact)
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 500
    WINDOW_DEFAULT_WIDTH = 1000
    WINDOW_DEFAULT_HEIGHT = 600


# Log colors for console
class LogColors:
    """Color tags for log messages."""
    
    INFO = "#2196f3"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    SUCCESS = "#4caf50"
    PLAYER = "#00bcd4"
    DEBUG = "#9e9e9e"
    TIMESTAMP = "#757575"


class LogColorsDark:
    """Dark theme log colors."""
    
    INFO = "#42a5f5"
    WARNING = "#ffa726"
    ERROR = "#ef5350"
    SUCCESS = "#66bb6a"
    PLAYER = "#4dd0e1"
    DEBUG = "#9e9e9e"
    TIMESTAMP = "#b0b0b0"


# Icons (Unicode symbols as fallback if no icon files)
class Icons:
    """Unicode icon symbols."""
    
    SERVER = "🖥"
    START = "▶"
    STOP = "⏹"
    PAUSE = "⏸"
    RELOAD = "🔄"
    ADD = "➕"
    REMOVE = "➖"
    EDIT = "✏"
    SAVE = "💾"
    OPEN = "📂"
    EXPORT = "📤"
    IMPORT = "📥"
    SEARCH = "🔍"
    SETTINGS = "⚙"
    INFO = "ℹ"
    WARNING = "⚠"
    ERROR = "❌"
    SUCCESS = "✓"
    CHART = "📊"
    GLOBE = "🌍"
    NETWORK = "🌐"
    USER = "👤"
    USERS = "👥"
    TIME = "🕐"
    STATS = "📈"
    LOG = "📋"
    CLEAR = "🗑"
    HELP = "❓"
    ABOUT = "ℹ"
    EXIT = "🚪"


# Animation timings (milliseconds)
class Animations:
    """Animation timing constants."""
    
    FAST = 100
    NORMAL = 200
    SLOW = 300
    VERY_SLOW = 500
    
    # Update intervals
    STATS_UPDATE = 1000  # 1 second
    CHART_UPDATE = 2000  # 2 seconds
    LOG_UPDATE = 100     # 100ms


# Status indicators
class Status:
    """Status indicator constants."""
    
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    
    # Status colors
    COLOR_STOPPED = Colors.TEXT_DISABLED
    COLOR_STARTING = Colors.WARNING
    COLOR_RUNNING = Colors.SUCCESS
    COLOR_STOPPING = Colors.WARNING
    COLOR_ERROR = Colors.ERROR


def get_theme_colors(dark_mode=False):
    """Get appropriate color scheme based on theme."""
    if dark_mode:
        return DarkColors
    return Colors


def get_log_colors(dark_mode=False):
    """Get appropriate log colors based on theme."""
    if dark_mode:
        return LogColorsDark
    return LogColors

