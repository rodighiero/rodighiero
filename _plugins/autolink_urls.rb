module Jekyll
  module AutolinkFilter
    URL_RE = /(<a\b[^>]*>.*?<\/a>)|(https?:\/\/[^\s<>"]+)/m

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
          "<a href=\"#{url}\">#{url}</a>#{trailing}"
        end
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::AutolinkFilter)
