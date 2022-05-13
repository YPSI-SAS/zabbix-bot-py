
ACK_MENU, CANCEL = map(chr, range(2))
#build_menu build a menu with buttons
def build_menu(buttons,
               n_cols,footer_buttons=None,cancel_button=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if footer_buttons:
        menu.append(footer_buttons)
    if cancel_button:
        menu.append(cancel_button)
    return menu