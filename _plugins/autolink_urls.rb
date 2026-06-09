module Jekyll
  module AutolinkFilter
    # Group 1 swallows existing anchors and any other HTML tag, so URLs
    # inside attributes (src, href, data-*) are never wrapped; only bare
    # URLs in text (group 2) get autolinked.
    URL_RE = /(<a\b[^>]*>.*?<\/a>|<[^>]*>)|(https?:\/\/[^\s<>"]+)/m

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
  end
end

Liquid::Template.register_filter(Jekyll::AutolinkFilter)
