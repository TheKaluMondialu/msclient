# Simplified Azure Theme for CS 1.6 Master Server
# Based on Azure-ttk-theme by rdbende, modified to work without image assets

package require Tk 8.6

namespace eval ttk::theme::azure-light {
    variable version 2.0
    package provide ttk::theme::azure-light $version

    ttk::style theme create azure-light -parent clam -settings {
        array set colors {
            -fg             "#000000"
            -bg             "#ffffff"
            -disabledfg     "#737373"
            -disabledbg     "#ffffff"
            -selectfg       "#ffffff"
            -selectbg       "#007fff"
            -borderfg       "#d0d0d0"
            -btnfg          "#000000"
            -btnbg          "#ffffff"
            -btnhover       "#e5e5e5"
            -btnactive      "#d0d0d0"
        }

        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertcolor $colors(-fg) \
            -insertwidth 1 \
            -fieldbackground $colors(-bg) \
            -font {"Segoe UI" 9} \
            -borderwidth 1 \
            -relief flat

        ttk::style configure TButton \
            -padding {8 4} \
            -anchor center \
            -foreground $colors(-btnfg)

        ttk::style map TButton -background [list \
            pressed $colors(-btnactive) \
            active $colors(-btnhover) \
            !disabled $colors(-btnbg)]

        ttk::style configure Accent.TButton \
            -foreground $colors(-selectfg) \
            -background $colors(-selectbg) \
            -bordercolor $colors(-selectbg)

        ttk::style configure TEntry \
            -fieldbackground $colors(-bg) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-borderfg)

        ttk::style configure TCombobox \
            -fieldbackground $colors(-bg) \
            -foreground $colors(-fg) \
            -arrowcolor $colors(-fg)

        ttk::style configure TNotebook \
            -background $colors(-bg) \
            -bordercolor $colors(-borderfg)

        ttk::style configure TNotebook.Tab \
            -background $colors(-btnbg) \
            -foreground $colors(-fg)

        ttk::style map TNotebook.Tab \
            -background [list selected $colors(-selectbg) active $colors(-btnhover)] \
            -foreground [list selected $colors(-selectfg)]

        ttk::style configure Treeview \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -fieldbackground $colors(-bg)

        ttk::style map Treeview \
            -background [list selected $colors(-selectbg)] \
            -foreground [list selected $colors(-selectfg)]
    }
}

namespace eval ttk::theme::azure-dark {
    variable version 2.0
    package provide ttk::theme::azure-dark $version

    ttk::style theme create azure-dark -parent clam -settings {
        array set colors {
            -fg             "#ffffff"
            -bg             "#2b2b2b"
            -disabledfg     "#aaaaaa"
            -disabledbg     "#2b2b2b"
            -selectfg       "#ffffff"
            -selectbg       "#007fff"
            -borderfg       "#404040"
            -btnfg          "#ffffff"
            -btnbg          "#2b2b2b"
            -btnhover       "#3d3d3d"
            -btnactive      "#4a4a4a"
        }

        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertcolor $colors(-fg) \
            -insertwidth 1 \
            -fieldbackground $colors(-bg) \
            -font {"Segoe UI" 9} \
            -borderwidth 1 \
            -relief flat

        ttk::style configure TButton \
            -padding {8 4} \
            -anchor center \
            -foreground $colors(-btnfg)

        ttk::style map TButton -background [list \
            pressed $colors(-btnactive) \
            active $colors(-btnhover) \
            !disabled $colors(-btnbg)]

        ttk::style configure Accent.TButton \
            -foreground $colors(-selectfg) \
            -background $colors(-selectbg) \
            -bordercolor $colors(-selectbg)

        ttk::style configure TEntry \
            -fieldbackground $colors(-bg) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-borderfg)

        ttk::style configure TCombobox \
            -fieldbackground $colors(-bg) \
            -foreground $colors(-fg) \
            -arrowcolor $colors(-fg)

        ttk::style configure TNotebook \
            -background $colors(-bg) \
            -bordercolor $colors(-borderfg)

        ttk::style configure TNotebook.Tab \
            -background $colors(-btnbg) \
            -foreground $colors(-fg)

        ttk::style map TNotebook.Tab \
            -background [list selected $colors(-selectbg) active $colors(-btnhover)] \
            -foreground [list selected $colors(-selectfg)]

        ttk::style configure Treeview \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -fieldbackground $colors(-bg)

        ttk::style map Treeview \
            -background [list selected $colors(-selectbg)] \
            -foreground [list selected $colors(-selectfg)]
    }
}

# Theme switch procedure
proc set_theme {mode} {
    if {$mode == "dark"} {
        ttk::style theme use "azure-dark"
        
        array set colors {
            -fg             "#ffffff"
            -bg             "#2b2b2b"
            -selectbg       "#007fff"
            -selectfg       "#ffffff"
        }

        tk_setPalette background $colors(-bg) \
            foreground $colors(-fg) \
            highlightColor $colors(-selectbg) \
            selectBackground $colors(-selectbg) \
            selectForeground $colors(-selectfg) \
            activeBackground $colors(-selectbg) \
            activeForeground $colors(-selectfg)
            
    } elseif {$mode == "light"} {
        ttk::style theme use "azure-light"
        
        array set colors {
            -fg             "#000000"
            -bg             "#ffffff"
            -selectbg       "#007fff"
            -selectfg       "#ffffff"
        }

        tk_setPalette background $colors(-bg) \
            foreground $colors(-fg) \
            highlightColor $colors(-selectbg) \
            selectBackground $colors(-selectbg) \
            selectForeground $colors(-selectfg) \
            activeBackground $colors(-selectbg) \
            activeForeground $colors(-selectfg)
    }
}




