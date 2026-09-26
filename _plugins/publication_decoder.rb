# | decode_numeric_entities — read by publication.html (the excerpt and the abstract).
# | snippet — read by publication.html (the excerpt).
# | doi_id — read by publication.html (citation_doi, the DOI button) and publication-cite.html.
# | page_range — read by publication.html (citation_firstpage / citation_lastpage).
#
# The filters that turn front-matter and body text into what a publication's
# machine-facing tags need — the ones a reader only ever sees in a search snippet,
# a social card or a Scholar record.
#
# decode_numeric_entities turns numeric character references (&#8217; / &#x2019;)
# into their UTF-8 characters. Used on excerpts before escape_once, whose regexp
# exempts named and decimal entities but not hex ones — a hex entity surviving
# strip_html would otherwise double-escape into a visible "&amp;#x…;".
#
# No publication source currently contains one, so this is a guard rather than
# a live transformation: it defends the description meta tags, where the failure
# would be invisible on the page and show up only in a social card or a search
# snippet. Named entities are deliberately left alone — escape_once handles
# those correctly, so decoding them would only hand it a bare & to re-escape.
#
# snippet cuts plain text to a search-snippet budget (160 characters, ellipsis
# included). It replaced `truncatewords: 22 | truncate: 160`, which could not see
# punctuation and left endings like "Consolascio,...", "global...." and
# "starting from ..." in every description tag. It ends on a full sentence when
# one closes in the second half of the budget; otherwise it cuts at the last
# whole word, drops the dangling punctuation, and appends a single "…". Text
# already inside the budget passes through untouched.
#
# doi_id reads the bare DOI off a doi.org URL ("https://doi.org/10.1/x" → "10.1/x"),
# and returns nil for any other link, which the templates test for: the `doi` field
# holds a handle or a repository URL when the work has no DOI.
#
# page_range splits `pages` into [first, last] for Scholar, which reads both as
# literal numbers: a Chicago-condensed "301–9" gives ["301", "309"], the missing
# leading digits borrowed from the first page. A single page gives [first].
module Jekyll
  module DecoderFilter
    def decode_numeric_entities(input)
      input.to_s.gsub(/&#(x[0-9a-fA-F]+|\d+);/) do
        code = Regexp.last_match(1)
        begin
          (code.start_with?('x') ? code[1..].to_i(16) : code.to_i).chr(Encoding::UTF_8)
        rescue RangeError
          Regexp.last_match(0)
        end
      end
    end

    def snippet(input, max = 160)
      text = input.to_s.gsub(/\s+/, ' ').strip
      return text if text.length <= max

      cut = text[0, max - 1]
      # A sentence end is a closing mark followed by a space (or a closing quote
      # then a space), in the back half — earlier, a whole sentence is too short
      # to stand as the description on its own.
      stop = cut.rindex(/[.!?][”’")]?(?= )/)
      if stop && stop >= max / 2
        close = cut[stop + 1]&.match?(/[”’")]/) ? 1 : 0
        return cut[0..stop + close]
      end

      cut = cut[0, cut.rindex(' ') || cut.length] unless text[max - 1] == ' '
      cut.sub(/[\s,;:.–—\-(“‘"']+\z/, '') + '…'
    end

    def doi_id(input)
      input.to_s[%r{\Ahttps?://(?:dx\.)?doi\.org/(.+)\z}, 1]
    end

    def page_range(input)
      parts = input.to_s.split(/[-–—]/).map(&:strip)
      first, last = parts.first, parts.last
      return [first] if parts.size < 2
      last = first[0, first.length - last.length] + last if last.length < first.length
      [first, last]
    end
  end
end

Liquid::Template.register_filter(Jekyll::DecoderFilter)
