# -*- mode: python ; coding: utf-8 -*-
# © 2012 Roland Sieker <ospalh@gmail.com>
# Provenance:
# Via libanki/anki/template/furigana.py by Damien Elmes <anki@ichi2.net>
# Based off Kieran Clancy's initial implementation.
# License:
# GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


"""
Addon for Anki 2 for Furikanji and other purposes

This provides a way to show kanji above the kana.
The addon uses the Unicode word character class to decide what to
display as base text and what as ruby. This bit works only with Python
2.7.

Also add a few other templates.
"""

import re
from anki import hooks


__version__ = "1.2.1"

# Check which pattern we should use, with or without the re.UNICODE flag.
try:
    # Just a dummy call to re.sub to see if the flags work. I think it
    # works with python 2.7 and doesn't work with python 2.6, but i
    # don't really care about verson numbers. (There may be a way to
    # inspect the argument list, but doing it EAFP is fine by me.)
    re.sub('test', 'for', 'flags', flags=re.UNICODE)
except TypeError:
    # Pattern close to the original one, but using named goups and
    # excluding newlines.
    split_pat = r' ?(?P<kanji>[^ >\n]+?)\[(?P<kana>.+?)\]'
    # Use our own name for re.sub, so that bending the call below
    # works.
    re_sub_flag = re.sub
else:
    # Pretty much what this is about. Use unicode word characters in
    # the pattern. Also name the groups so the code below becomes a
    # bit more readable.
    split_pat = u' ?(?P<kanji>\w+?)\[(?P<kana>.+?)\]'
    # Add flag parameter to calls to re.sub.
    re_sub_flag = lambda pattern, repl, string, flags=re.UNICODE: \
        re.sub(pattern, repl, string, flags=flags)

furigana_pat = r'<ruby class="furigana"><rb>\g<kanji></rb>'\
    '<rt>\g<kana></rt></ruby>'
"""
Pattern to produce the furigana.

What is called ruby in the old code, but using named groups and
adding a class.
"""
furikanji_pat = r'<ruby class="furikanji"><rb>\g<kana></rb>'\
    '<rt>\g<kanji></rt></ruby>'
"""
Pattern to produce the furikanji.

This is pretty much the reason for this add-on.
"""


def no_sound(repl):
    """Do re replacement only when the text is not a media file."""
    def func(match):
        if match.group('kana').startswith("sound:"):
            # return without modification
            return match.group(0)
        else:
            # I used another if here. Use different values for re_flag
            # in a variable now.
            return re_sub_flag(split_pat, repl, match.group(0))

    return func


def kanji_word_re(txt, *args):
    """Strip kana and wrap base text in class kanji."""
    return re_sub_flag(
        split_pat, no_sound(r'<span class="kanji">\g<kanji></span>'), txt)


def kana_word_re(txt, *args):
    """Strip base text and wrap kana in class kana."""
    return re_sub_flag(
        split_pat, no_sound(r'<span class="kana">\g<kana></span>'), txt)


def furigana_word_re(txt, *args):
    """
    Format text for ruby display.

    Put text with square brackets in <ruby> tags, using text before
    the brackets as <rb>, the text in the brackets as <rt>. Add class
    furigana to the ruby tag.
    """
    return re_sub_flag(split_pat, no_sound(furigana_pat), txt)


def furikanji(txt, *args):
    """
    Format text for ruby display, kanji above kana.

    Put text with square brackets in <ruby> tags, using text before
    the brackets as <rt>, the text in the brackets as <rb>. Add class
    furikanji to the ruby tag. This is reversed from the standard way
    and typically shows small kanji above their reading.
    """
    return re_sub_flag(split_pat, no_sound(furikanji_pat), txt)


def box_kana(txt, *args):
    u"""
    Show text above an empty, dashed box.

    Put text in a <ruby> block as <rt> with a an "IDEOGRAPHIC SPACE",
    "　" as <rb>, drawn with a frame. Add class boxkana to the ruby
    tag.
    """
    return u'<ruby class="boxkana">'\
        u'<rb style="border:dashed; border-width: 1px">　</rb>'\
        u'<rt>%s</rt></ruby>' % txt


def boxed(txt, *args):
    """
    Draw a dashed box around the text.

    Draw a dashed box around the text and add class boxed to the span
    element.
    """
    return u'<span class="boxed" style="border:dashed; border-width: 1px">'\
        u'%s</span>' % txt


hooks.addHook('fmod_furikanji', furikanji)
hooks.addHook('fmod_boxkana', box_kana)
hooks.addHook('fmod_boxed', boxed)
if hooks._hooks['fmod_kanji']:
    hooks._hooks['fmod_kanji'][0] = kanji_word_re
if hooks._hooks['fmod_kana']:
    hooks._hooks['fmod_kana'][0] = kana_word_re
if hooks._hooks['fmod_furigana']:
    hooks._hooks['fmod_furigana'][0] = furigana_word_re
