# Liquid filter to escape special characters for BibTeX output.
# Converts accented characters (é, ü, ñ, etc.) to BibTeX-safe sequences.
# Examples:
#   "Müller" => "M{\"u}ller"
#   "Schönberg" => "Sch{\"o}nberg"
#   "Français" => "Fran{\\c{c}}ais"
module Jekyll
  module BibTexEscapeFilter
    ESCAPE_MAP = {
      'á' => "{\\'a}",
      'à' => "{\\`a}",
      'ä' => "{\\\"a}",
      'â' => "{\\^a}",
      'ã' => "{\\~a}",
      'å' => "{\\aa}",
      'é' => "{\\'e}",
      'è' => "{\\`e}",
      'ë' => "{\\\"e}",
      'ê' => "{\\^e}",
      'í' => "{\\'i}",
      'ì' => "{\\`i}",
      'ï' => "{\\\"i}",
      'î' => "{\\^i}",
      'ó' => "{\\'o}",
      'ò' => "{\\`o}",
      'ö' => "{\\\"o}",
      'ô' => "{\\^o}",
      'õ' => "{\\~o}",
      'ø' => "{\\o}",
      'ú' => "{\\'u}",
      'ù' => "{\\`u}",
      'ü' => "{\\\"u}",
      'û' => "{\\^u}",
      'ñ' => "{\\~n}",
      'ç' => "{\\c{c}}",
      'Á' => "{\\'A}",
      'À' => "{\\`A}",
      'Ä' => "{\\\"A}",
      'Â' => "{\\^A}",
      'Ã' => "{\\~A}",
      'Å' => "{\\AA}",
      'É' => "{\\'E}",
      'È' => "{\\`E}",
      'Ë' => "{\\\"E}",
      'Ê' => "{\\^E}",
      'Í' => "{\\'I}",
      'Ì' => "{\\`I}",
      'Ï' => "{\\\"I}",
      'Î' => "{\\^I}",
      'Ó' => "{\\'O}",
      'Ò' => "{\\`O}",
      'Ö' => "{\\\"O}",
      'Ô' => "{\\^O}",
      'Õ' => "{\\~O}",
      'Ø' => "{\\O}",
      'Ú' => "{\\'U}",
      'Ù' => "{\\`U}",
      'Ü' => "{\\\"U}",
      'Û' => "{\\^U}",
      'Ñ' => "{\\~N}",
      'Ç' => "{\\c{C}}"
    }.freeze

    def bibtex_escape(str)
      return str if str.nil? || str.empty?
      ESCAPE_MAP.reduce(str) { |s, (char, escape)| s.gsub(char, escape) }
    end
  end
end

Liquid::Template.register_filter(Jekyll::BibTexEscapeFilter)
