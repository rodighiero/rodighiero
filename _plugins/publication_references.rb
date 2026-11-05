# | ordered_references — applied to publication bodies in publication.html.
#
# Turns the <ul> that follows a bibliography heading into <ol class="references">,
# the markup Google Scholar's inclusion guidelines name for HTML reference lists.
# The Markdown keeps writing `- ` bullets, so no publication file changes; the
# list still shows bullets through `.body ol.references` in styles-article.css,
# because Chicago author-date entries are alphabetical, not numbered.
#
# Only headings in the bibliography vocabulary match, in every language the
# corpus uses. The layout's own "Related publications" list is outside the
# body this filter sees, so it is never touched.
module Jekyll
  module ReferencesFilter
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

Liquid::Template.register_filter(Jekyll::ReferencesFilter)
