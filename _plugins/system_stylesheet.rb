# | strip_css_comments — read by home.html, publication.html and 404.html.
#
# The stylesheets are inlined into every page's <head> (styles-*.css), and their
# comments are written for the maintainer, not the reader: about half the bytes of the
# homepage's <style> block, all of it ahead of first paint. The layouts capture their
# includes and pass them through this filter, so the source keeps every comment and the
# page ships none.
#
# Comments, then indentation and the blank lines they leave. CSS comments do not nest,
# so the non-greedy match is the language's own rule. It would misfire on a "/*" inside
# a string or an unquoted url(), which no stylesheet here contains — keep it that way.
# Usage: {% capture _css %}{% include styles-base.css %}{% endcapture %}{{ _css | strip_css_comments }}
module Jekyll::StylesheetFilter
  def strip_css_comments(css)
    css.to_s.gsub(%r{/\*.*?\*/}m, '').lines.map(&:strip).reject(&:empty?).join("\n")
  end
end

Liquid::Template.register_filter(Jekyll::StylesheetFilter)
