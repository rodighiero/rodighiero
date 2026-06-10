# Liquid filter that turns numeric character references (&#8217; / &#x2019;)
# into their UTF-8 characters. Used on excerpts before escape_once, whose
# regexp exempts named and decimal entities but not hex ones — a hex entity
# surviving strip_html would otherwise double-escape into visible "&amp;#x…;".
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
