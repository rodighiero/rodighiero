# Liquid filter that drops a leading <figure>...</figure> block from a string.
# Some publications open their body with a caption-less lead figure (the same
# cover/map image used as the card thumb) before the excerpt separator, so
# Jekyll's auto-generated excerpt captures it. That's fine on the article page,
# but the homepage list view's card-desc has no room for a full-size image —
# strip it there rather than reordering the source Markdown.
module Jekyll
  module StripLeadingFigureFilter
    def strip_leading_figure(input)
      input.to_s.sub(/\A\s*<figure\b.*?<\/figure>\s*/m, '')
    end
  end
end

Liquid::Template.register_filter(Jekyll::StripLeadingFigureFilter)
