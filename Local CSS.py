# -*- mode: python ; coding: utf-8 -*-
#
# © copyright 2012 Roland Sieker <ospalh@gmail.com>
# Contains snippets of code from anki proper,
# written by Damien Elmes <anki@ichi2.net>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html
# Insipired by CSS Modify Style-Sheet input by DAThomas

"""
Load local CSS and add it to the cards.

This is an add-on for Anki 2 SRS.
Load the file 'user_style.css' from the user’s profile folder
(e.g. "~/Anki/User 1/user_style.css") and add it to the cards, before
the style from the template.
"""

import os
import re
from anki.cards import Card
from anki.consts import MODEL_STD
from anki import hooks
from aqt import mw


__version__ = '1.2.4'

user_css_name = 'user_style.css'
"""File name of the user's CSS"""
css_encoding = 'utf-8'
"""Encoding of the user's CSS file"""
local_class = 'loc'
"""Class added to all cards"""

user_css = u''


def fix_body_class():
    u"""
    Add classes to body.

    Add classes to the html body, so the local CSS mechanism works
    together with CSS definitions for web review. Use
    ".loc.card"—without space—for the card and ".loc .classNN"—with a
    space—for sub-elements in you user_style.css.
    """
    # Gather all the A-Za-z0-9_ characters from the template and model
    # names and add those as class.
    model = mw.reviewer.card.model()
    if model['type'] == MODEL_STD:
        template_nr = mw.reviewer.card.ord
    else:
        template_nr = 0
    template_class = re.sub('[\W_]+', '',
                            model['tmpls'][template_nr]['name']).lower()
    model_class = re.sub('[\W_]+', '', model['name']).lower()
    body_class = '{0} card card{1} template_{2} model_{3}'.format(
        local_class, mw.reviewer.card.ord,
        template_class, model_class)
    mw.web.eval("document.body.className = '{0}';".format(body_class))


def get_user_css():
    """
    Load the user's CSS data from disk.
    """
    global user_css
    css_path = os.path.join(mw.pm.profileFolder(), user_css_name)
    try:
        with open(css_path, 'r') as f:
            user_css = unicode(f.read(), css_encoding)
    except IOError:
        pass


def localized_card_css(self):
    """Set the css for a card"""
    return_css = u''
    if user_css:
        return_css = '<style>%s</style>' % user_css
    return return_css + old_css(self)


old_css = Card.css
Card.css = localized_card_css

hooks.addHook("showQuestion", fix_body_class)
hooks.addHook("profileLoaded", get_user_css)
