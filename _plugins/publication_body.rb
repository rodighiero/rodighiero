# | autolink_urls — applied to publication full-text bodies in publication.html.
# | ordered_references — applied to publication bodies in publication.html.
#
# The two filters that rewrite a rendered body's HTML.
#
# autolink_urls wraps bare http(s) URLs in anchors, leaving any URL already inside
# markup alone.
#
# ordered_references turns the <ul> that follows a bibliography heading into
# <ol class="references">, the markup Google Scholar's inclusion guidelines name
# for HTML reference lists. The Markdown keeps writing `- ` bullets, so no
# publication file changes; the list still shows bullets through
# `.body ol.references` in styles-article.css, because Chicago author-date entries
# are alphabetical, not numbered. Only headings in the bibliography vocabulary
# match, in every language the corpus uses. The layout's own "Related publications"
# list is outside the body this filter sees, so it is never touched.
module Jekyll
  module BodyFilter
    # Group 1 swallows existing anchors and any other HTML tag, so URLs
    # inside attributes (src, href, data-*) are never wrapped; only bare
    # URLs in text (group 2) get autolinked.   (non-breaking space) is
    # excluded explicitly: kramdown inserts one before the footnote return
    # arrow, and Ruby's \s does not match it, so without this the URL would
    # swallow the nbsp (and a preceding period).
    URL_RE = /(<a\b[^>]*>.*?<\/a>|<[^>]*>)|(https?:\/\/[^\s\u00A0<>"]+)/m

    def autolink_urls(input)
      input.to_s.gsub(URL_RE) do |match|
        if $1
          match
        else
          url = $2
          trailing = ''
          while url =~ /[.,;:!?)]\z/
            trailing = url[-1] + trailing
            url = url[0..-2]
          end
          escaped = url.gsub('&', '&amp;')
          "<a href=\"#{escaped}\">#{escaped}</a>#{trailing}"
        end
      end
    end

    HEADINGS = /\A(?:references|références|referenties|bibliography|bibliographie|bibliografia)\b/i
    # The heading text may not cross another heading tag; a plain lazy `.*?`
    # would start at an earlier <h2> and swallow the body up to the list.
    HEADING_LIST_RE = %r{(<h([1-6])\b[^>]*>((?:(?!</?h[1-6]\b).)*?)</h\2>\s*)<ul>(.*?)</ul>}m

    def ordered_references(input)
      input.to_s.gsub(HEADING_LIST_RE) do |match|
        head, _level, text, items = $1, $2, $3, $4
        # A nested list would make the lazy match stop at the inner </ul>.
        if text.gsub(/<[^>]*>/, '').strip.match?(HEADINGS) && !items.include?('<ul')
          "#{head}<ol class=\"references\">#{items}</ol>"
        else
          match
        end
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::BodyFilter)
