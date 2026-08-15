# | decode_numeric_entities — read by publication.html:4,11.
#
# Turns numeric character references (&#8217; / &#x2019;) into their UTF-8
# characters. Used on excerpts before escape_once, whose regexp exempts named
# and decimal entities but not hex ones — a hex entity surviving strip_html
# would otherwise double-escape into a visible "&amp;#x…;".
#
# No publication source currently contains one, so this is a guard rather than
# a live transformation: it defends the description meta tags, where the failure
# would be invisible on the page and show up only in a social card or a search
# snippet. Named entities are deliberately left alone — escape_once handles
# those correctly, so decoding them would only hand it a bare & to re-escape.
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
  end
end

Liquid::Template.register_filter(Jekyll::DecodeNumericEntitiesFilter)
