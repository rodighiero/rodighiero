# | decode_numeric_entities — read by publication.html (the excerpt and the abstract).
# | snippet — read by publication.html (the excerpt).
#
# The two text filters behind a publication's description tags, the ones a reader
# only ever sees in a search snippet or a social card.
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
module Jekyll
  module DecodeNumericEntitiesFilter
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
  end
end

Liquid::Template.register_filter(Jekyll::DecodeNumericEntitiesFilter)
