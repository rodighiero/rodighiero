require 'json'

# | strip_css_comments — read by home.html, publication.html and 404.html.
# | strip_js_comments  — read by home.html, publication.html and site-analytics.html.
# | minify_json        — read by home.html, publication.html (JSON-LD) and site-speculation.html.
#
# What the pages inline, made as small as it can be without changing what it says. The
# stylesheets and scripts (styles-*.css, scripts-*.js) carry comments written for the
# maintainer, not the reader: about half the bytes of what the homepage inlines. The
# JSON-LD and the speculation rules are written indented, to be read and diffed as
# templates. Each <style>, <script>, JSON-LD and speculation-rules block is captured and passed through one of these filters, so
# the source keeps its comments and layout and the page ships neither. Usage:
#   {% capture _css %}{% include styles-base.css %}{% endcapture %}{{ _css | strip_css_comments }}
module Jekyll::InlineFilter
  # CSS comments do not nest, so the non-greedy match is the language's own rule. It
  # would misfire on a "/*" inside a string or an unquoted url(), which no stylesheet
  # here contains — keep it that way. Then indentation and the blank lines left behind.
  def strip_css_comments(css)
    css.to_s.gsub(%r{/\*.*?\*/}m, '').lines.map(&:strip).reject(&:empty?).join("\n")
  end

  # JS needs a lexer rather than a regexp: "//" opens a comment in code but not in a
  # string ('https://…'), a template literal or a regex literal (/\/\//), and only the
  # token before a "/" tells a regex from a division. Line breaks are kept, because
  # automatic semicolon insertion reads them (site-analytics.html relies on it); only
  # indentation, trailing space and blank lines go, and never inside a literal.
  def strip_js_comments(js)
    Jekyll::InlineFilter.js_segments(js.to_s).map do |code, text|
      code ? text.gsub(/[ \t]*\n\s*/, "\n") : text
    end.join.strip
  end

  # Parsed and re-serialised, so invalid JSON fails the build rather than shipping
  # structured data a crawler, or rules a browser, silently discards. Key order survives (Ruby hashes keep
  # it). "</" is escaped as "<\/", which JSON reads as the same string, so no value can
  # close the <script> early.
  def minify_json(json)
    JSON.generate(JSON.parse(json.to_s)).gsub('</', '<\\/')
  rescue JSON::ParserError => e
    raise "minify_json: invalid JSON on #{@context.registers[:page]['path']}: #{e.message}"
  end

  # Words after which a "/" starts a regex rather than dividing.
  REGEX_AFTER = %w[return typeof instanceof in of new delete void throw case do else yield await].freeze

  # [[code?, text], …] with comments dropped; literals are emitted whole as code = false.
  def self.js_segments(src)
    out = []
    code = +''
    flush = -> { out << [true, code.dup] unless code.empty?; code.clear }
    i = 0
    prev = nil      # last significant code character, for the regex/division call
    word = +''      # the identifier or keyword that ends at prev, if any
    braces = []     # brace depth at each open ${ in a template literal
    depth = 0
    n = src.length
    while i < n
      c = src[i]
      if c == '/' && src[i + 1] == '/'
        i += 1 until i >= n || src[i] == "\n"
      elsif c == '/' && src[i + 1] == '*'
        close = src.index('*/', i + 2) or raise "strip_js_comments: unterminated /* comment"
        code << ' ' unless code.end_with?(' ', "\n") # a/**/b must not become ab
        i = close + 2
      elsif c == '"' || c == "'" || c == '`' || (c == '}' && braces.last == depth)
        flush.call
        start = i
        if c == '}' # back into a template literal after its ${…}
          braces.pop
          c = '`'
        end
        i += 1
        opened = false # ended at a ${ rather than at the closing quote
        loop do
          raise "strip_js_comments: unterminated #{c} literal" if i >= n || (src[i] == "\n" && c != '`')
          if src[i] == '\\'
            i += 2
          elsif src[i] == c
            i += 1
            break
          elsif c == '`' && src[i] == '$' && src[i + 1] == '{'
            i += 2
            braces << depth
            opened = true
            break
          else
            i += 1
          end
        end
        out << [false, src[start...i]]
        prev = opened ? '{' : c
        word = +''
      elsif c == '/' && Jekyll::InlineFilter.regex_allowed?(prev, word)
        flush.call
        start = i
        i += 1
        klass = false
        loop do
          raise 'strip_js_comments: unterminated regex literal' if i >= n || src[i] == "\n"
          if src[i] == '\\'
            i += 2
            next
          end
          break if src[i] == '/' && !klass
          klass = true if src[i] == '['
          klass = false if src[i] == ']'
          i += 1
        end
        i += 1
        i += 1 while i < n && src[i] =~ /[a-z]/i # flags
        out << [false, src[start...i]]
        prev = '/'
        word = +''
      else
        depth += 1 if c == '{'
        depth -= 1 if c == '}'
        unless c =~ /\s/
          word = c =~ /[\w$]/ ? (prev =~ /[\w$]/ ? word + c : c.dup) : +''
          prev = c
        end
        code << c
        i += 1
      end
    end
    flush.call
    out
  end

  def self.regex_allowed?(prev, word)
    return true if prev.nil?
    return REGEX_AFTER.include?(word) if prev =~ /[\w$]/
    ![')', ']', '}', '"', "'", '`', '/'].include?(prev)
  end
end

Liquid::Template.register_filter(Jekyll::InlineFilter)
