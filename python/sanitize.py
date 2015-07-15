# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Escaping functions for compiled soy templates.

This module contains the public functions and classes to sanitize content for
different contexts.

The bulk of the logic resides in generated_sanitize.py which is generated by
GeneratePySanitizeEscapingDirectiveCode.java to match other implementations.
Please keep as much escaping and filtering logic/regex in there as possible.
"""

# Emulate Python 3 style unicode string literals.
from __future__ import unicode_literals

__author__ = 'dcphillips@google.com (David Phillips)'

import functools
import re

from . import generated_sanitize

# To allow the rest of the file to assume Python 3 strings, we will assign str
# to unicode for Python 2. This will error in 3 and be ignored.
try:
  str = unicode
except NameError:
  pass


#############
# Constants #
#############


# Matches html attribute endings which are ambiguous (not ending with space or
# quotes).
_AMBIGUOUS_ATTR_END_RE = re.compile(r'([^"\'\s])$')


# Matches any/only HTML5 void elements' start tags.
# See http://www.w3.org/TR/html-markup/syntax.html#syntax-elements
_HTML5_VOID_ELEMENTS_RE = re.compile(
    '^<(?:area|base|br|col|command|embed|hr|img|input'
    '|keygen|link|meta|param|source|track|wbr)\\b')


# An innocuous output to replace filtered content with.
# For details on its usage, see the description in
_INNOCUOUS_OUTPUT = 'zSoyz'


# Regex for various newline combinations.
_NEWLINE_RE = re.compile('(\r\n|\r|\n)')


# Regex for finding replacement tags.
_REPLACEMENT_TAG_RE = re.compile(r'\[(\d+)\]')


#######################################
# Soy public directives and functions #
#######################################


def change_newline_to_br(value):
  result = _NEWLINE_RE.sub('<br>', str(value))

  if is_content_kind(value, CONTENT_KIND.HTML):
    approval = IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval(
        'Persisting existing sanitization.')
    return SanitizedHtml(result, get_content_dir(value), approval=approval)

  return result


def clean_html(value, safe_tags=None):
  if not safe_tags:
    safe_tags = generated_sanitize._SAFE_TAG_WHITELIST

  if is_content_kind(value, CONTENT_KIND.HTML):
    return value

  approval = IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval(
      'Escaped html is by nature sanitized.')
  return SanitizedHtml(_strip_html_tags(value, safe_tags),
                       get_content_dir(value), approval=approval)


def escape_css_string(value):
  return generated_sanitize.escape_css_string_helper(value)


def escape_html(value):
  if is_content_kind(value, CONTENT_KIND.HTML):
    return value

  approval = IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval(
      'Escaped html is by nature sanitized.')
  return SanitizedHtml(generated_sanitize.escape_html_helper(value),
                       get_content_dir(value), approval=approval)


def escape_html_attribute(value):
  if is_content_kind(value, CONTENT_KIND.HTML):
    return generated_sanitize.normalize_html_helper(
        _strip_html_tags(value.content))

  return generated_sanitize.escape_html_helper(value)


def escape_html_attribute_nospace(value):
  if is_content_kind(value, CONTENT_KIND.HTML):
    return generated_sanitize.normalize_html_nospace_helper(
        _strip_html_tags(value.content))

  return generated_sanitize.escape_html_nospace_helper(value)


def escape_html_rcdata(value):
  if is_content_kind(value, CONTENT_KIND.HTML):
    return generated_sanitize.normalize_html_helper(value.content)

  return generated_sanitize.escape_html_helper(value)


def escape_js_regex(value):
  return generated_sanitize.escape_js_regex_helper(value)


def escape_js_string(value):
  if is_content_kind(value, CONTENT_KIND.JS_STR_CHARS):
    return value.content

  return generated_sanitize.escape_js_string_helper(value)


def escape_js_value(value):
  if value is None:
    # We output null for compatibility with Java, as it returns null from maps
    # where there is no corresponding key.
    return ' null '

  if is_content_kind(value, CONTENT_KIND.JS):
    return value.content

  # We surround values with spaces so that they can't be interpolated into
  # identifiers by accident.
  # We could use parentheses but those might be interpreted as a function call.
  # This matches the JS implementation in javascript/template/soy/soyutils.js.
  if isinstance(value, (int, long, float, complex)):
    return ' ' + str(value) + ' '

  return "'" + generated_sanitize.escape_js_string_helper(value) + "'"


def escape_uri(value):
  return generated_sanitize.escape_uri_helper(value)


def filter_css_value(value):
  if is_content_kind(value, CONTENT_KIND.CSS):
    return value.content

  if value is None:
    return ''

  return generated_sanitize.filter_css_value_helper(value)


def filter_html_attributes(value):
  # NOTE: Explicitly no support for SanitizedContentKind.HTML, since that is
  # meaningless in this context, which is generally *between* html attributes.
  if is_content_kind(value, CONTENT_KIND.ATTRIBUTES):
    # Add a space at the end to ensure this won't get merged into following
    # attributes, unless the interpretation is unambiguous (ending with quotes
    # or a space).
    return _AMBIGUOUS_ATTR_END_RE.sub(r'\1 ', value.content)

  # TODO(gboyer): Replace this with a runtime exception along with other
  return generated_sanitize.filter_html_attributes_helper(value)


def filter_html_element_name(value):
  # NOTE: We don't accept any SanitizedContent here. HTML indicates valid
  # PCDATA, not tag names. A sloppy developer shouldn't be able to cause an
  # exploit:
  # ... {let userInput}script src=http://evil.com/evil.js{/let} ...
  # ... {param tagName kind="html"}{$userInput}{/param} ...
  # ... <{$tagName}>Hello World</{$tagName}>
  return generated_sanitize.filter_html_element_name_helper(value)


def filter_image_data_uri(value):
  approval = IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval(
      'Filtered URIs are by nature sanitized.')
  return SanitizedUri(
      generated_sanitize.filter_image_data_uri_helper(value), approval=approval)


def filter_no_auto_escape(value):
  if is_content_kind(value, CONTENT_KIND.TEXT):
    return _INNOCUOUS_OUTPUT

  return value


def filter_normalize_uri(value):
  if is_content_kind(value, CONTENT_KIND.URI):
    return normalize_uri(value)

  return generated_sanitize.filter_normalize_uri_helper(value)


def normalize_html(value):
  return generated_sanitize.normalize_html_helper(value)


def normalize_uri(value):
  return generated_sanitize.normalize_uri_helper(value)


############################
# Public Utility Functions #
############################


def get_content_dir(value):
  if isinstance(value, SanitizedContent):
    return value.content_dir

  return None


def is_content_kind(value, content_kind):
  return (isinstance(value, SanitizedContent) and
          value.content_kind == content_kind)


#############################
# Private Utility Functions #
#############################

def _get_content_kind(value):
  """Get human-readable name for the kind of value.

  Args:
    value: A input string.
  Returns:
    A string name represented the type of value.
  """
  if isinstance(value, SanitizedContent):
    return CONTENT_KIND.decodeKind(value.content_kind)
  else:
    return type(value)


def _strip_html_tags(value, tag_whitelist=None):
  """Strip any html tags not present on the whitelist.

  If there's a whitelist present, the handler will use a marker for whitelisted
  tags, strips all others, and then reinserts the originals.

  Args:
    value: The input string.
    tag_whitelist: A list of safe tag names.
  Returns:
    A string with non-whitelisted tags stripped.
  """
  if not tag_whitelist:
    # The second level (replacing '<' with '&lt;') ensures that non-tag uses of
    # '<' do not recombine into tags as in
    # '<<foo>script>alert(1337)</<foo>script>'
    return generated_sanitize._LT_REGEX.sub(
        '&lt;', generated_sanitize._HTML_TAG_REGEX.sub('', value))

  # Escapes '[' so that we can use [123] below to mark places where tags
  # have been removed.
  html = str(value).replace('[', '&#91;')

  # Consider all uses of '<' and replace whitelisted tags with markers like
  # [1] which are indices into a list of approved tag names.
  # Replace all other uses of < and > with entities.
  tags = []
  tag_handler = functools.partial(_tag_sub_handler, tag_whitelist, tags)
  html = generated_sanitize._HTML_TAG_REGEX.sub(tag_handler, html)

  # Escape HTML special characters. Now there are no '<' in html that could
  # start a tag.
  html = generated_sanitize.normalize_html_helper(html)

  # Discard any dead close tags and close any hanging open tags before
  # reinserting white listed tags.
  final_close_tags = _balance_tags(tags)

  # Now html contains no tags or less-than characters that could become
  # part of a tag via a replacement operation and tags only contains
  # approved tags.
  # Reinsert the white-listed tags.
  html = _REPLACEMENT_TAG_RE.sub(lambda match: tags[int(match.group(1))], html)

  # Close any still open tags.
  # This prevents unclosed formatting elements like <ol> and <table> from
  # breaking the layout of containing HTML.
  return html + final_close_tags


def _tag_sub_handler(tag_whitelist, tags, match):
  """Replace whitelisted tags with markers and update the tag list.

  Args:
    tag_whitelist: A list containing all whitelisted html tags.
    tags: The list of all whitelisted tags found in the text.
    match: The current match element with a subgroup containing the tag name.

  Returns:
    The replacement content, a index marker for whitelisted tags, or an empty
    string.
  """
  tag = match.group(0)
  name = match.group(1)
  name = name.lower()
  if name in tag_whitelist:
    start = '</' if tag[1] == '/' else '<'
    index = len(tags)
    tags.append(start + name + '>')
    return '[%d]' % index

  return ''


def _balance_tags(tags):
  """Throw out any close tags without an open tag.

  If {@code <table>} is used for formatting, embedded HTML shouldn't be able
  to use a mismatched {@code </table>} to break page layout.

  Args:
    tags: The list of all tags in this text.

  Returns:
    A string containing zero or more closed tags that close all elements that
    are opened in tags but not closed.
  """
  open_tags = []
  for i, tag in enumerate(tags):
    if tag[1] == '/':
      index = len(open_tags) - 1
      while index >= 0 and open_tags[index] != tag:
        index -= 1

      if index < 0:
        tags[i] = ''  # Drop close tag.
      else:
        tags[i] = ''.join(reversed(open_tags[index:]))
        del open_tags[index:]

    elif not _HTML5_VOID_ELEMENTS_RE.match(tag):
      open_tags.append('</' + tag[1:])

  return ''.join(reversed(open_tags))


#####################
# Sanitized Classes #
#####################


class IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval:
  justification = None

  def __init__(self, justification=None):
    if justification:
      self.justification = justification


class CONTENT_KIND:
  HTML, JS, JS_STR_CHARS, URI, ATTRIBUTES, CSS, TEXT = range(1, 8)

  @staticmethod
  def decodeKind(i):
    i = i - 1;
    return ['HTML', 'JS', 'JS_STR_CHARS', 'URI', 'ATTRIBUTES', 'CSS', 'TEXT'][i]


class DIR:
  LTR, NEUTRAL, RTL = (1, 0, -1)


class SanitizedContent(object):
  content_kind = None

  def __new__(cls, *args, **kwargs):
    if cls is SanitizedContent or not cls.content_kind:
      raise TypeError('SanitizedContent cannot be instantiated directly. '
                      'Instantiate a child class with a valid content_kind.')
    return object.__new__(cls, *args, **kwargs)

  def __init__(self, content=None, content_dir=None, approval=None):
    if not isinstance(approval,
                      IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval):
      raise TypeError('Caller does not have sanitization approval.')
    elif not approval.justification or len(approval.justification) < 20:
      raise TypeError('A justification of at least 20 characters must be'
                      'provided with the approval.')
    self.content = content
    self.content_dir = content_dir

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not self.__eq__(other)

  def __len__(self):
    return len(self.content)

  def __nonzero__(self):
    return bool(self.content)

  def __str__(self):
    return str(self.content)

  def __unicode__(self):
    return str(self.content)


class SanitizedCss(SanitizedContent):
  content_kind = CONTENT_KIND.CSS

  def __init__(self, content=None, approval=None):
    super(SanitizedCss, self).__init__(content, DIR.LTR, approval)


class SanitizedHtml(SanitizedContent):
  content_kind = CONTENT_KIND.HTML


class SanitizedHtmlAttribute(SanitizedContent):
  content_kind = CONTENT_KIND.ATTRIBUTES

  def __init__(self, content=None, approval=None):
    super(SanitizedHtmlAttribute, self).__init__(
        content, DIR.LTR, approval)


class SanitizedJs(SanitizedContent):
  content_kind = CONTENT_KIND.JS

  def __init__(self, content=None, approval=None):
    super(SanitizedJs, self).__init__(content, DIR.LTR, approval)


class SanitizedJsStrChars(SanitizedContent):
  content_kind = CONTENT_KIND.JS_STR_CHARS


class SanitizedUri(SanitizedContent):
  content_kind = CONTENT_KIND.URI

  def __init__(self, content=None, approval=None):
    super(SanitizedUri, self).__init__(content, DIR.LTR, approval)


class UnsanitizedText(SanitizedContent):
  content_kind = CONTENT_KIND.TEXT

  def __init__(self, content=None, content_dir=None, approval=None):
    # approval is still in the api for consistency, but unsanitized text is
    # always approved.
    approval = IActuallyUnderstandSoyTypeSafetyAndHaveSecurityApproval(
        'Unsanitized Text does not require approval.')
    super(UnsanitizedText, self).__init__(str(content), content_dir,
                                          approval=approval)
