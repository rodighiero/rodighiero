# | credit_short — read by credit-short.html (homepage publication and event cards).
# | chicago_names — read by publication-cite.html (the Chicago reference).
#
# The short credit voice, written from Dario's point of view with his own name
# stripped: "with X and Y". It replaced two includes' worth of Liquid, which had to
# fake arrays with a "~~~" sentinel string.
#
# Each credit field is " and "-joined in the front matter. Per field, the names that
# are not Dario are joined with ", " and a final " and " (no Oxford comma), behind a
# prefix that depends on whether Dario was among them: "edited with X" when he was,
# "edited by X" when he was not. A field left with no one but Dario emits nothing.
# Editors appear only when there is no co-author; the publication page always shows
# them. The parts join with ". ", each after the first capitalised.
#
# The surname match is deliberately loose (contains "Rodighiero"): it only decides
# whose name to strip from a byline, where a false positive costs nothing. The
# exact match that hangs an ORCID on a name lives in jsonld-person.html.
#
# chicago_names joins one " and "-joined field for the Chicago reference. Passed
# true, it is the leading author block: the first name inverted to "Family, Given"
# and a serial comma from two names up, which the inversion needs ("Rodighiero,
# Dario, and X"). Otherwise it is a secondary role — editors, translators,
# interviewers — in normal order, with the serial comma from three names up, so a
# pair joins on a bare " and ". An absent field gives an empty string.
module Jekyll
  module CreditFilter
    ME = 'Rodighiero'

    # [field, prefix when Dario is among the names, prefix when he is not], in the
    # order a card lists them.
    ROLES = [
      ['author',      'with ',            ''],
      ['editor',      'edited with ',     'edited by '],
      ['preface',     'preface with ',    'preface by '],
      ['translator',  'translated with ', 'translated by '],
      ['interviewer', 'interview with ',  'interview by '],
    ].freeze

    def credit_short(item)
      parts = ROLES.to_h do |field, with, by|
        names = item[field].to_s.split(' and ').map(&:strip)
        others = names.reject { |n| n.include?(ME) }
        next [field, ''] if others.empty?

        [field, (others.size < names.size ? with : by) + join_names(others)]
      end
      parts.delete('editor') unless parts['author'].empty?
      parts.values.reject(&:empty?)
           .each_with_index.map { |p, i| i.zero? ? p : p[0].upcase + p[1..] }
           .join('. ')
    end

    def chicago_names(input, lead = false)
      names = input.to_s.split(' and ').map(&:strip)
      return '' if names.empty?

      if lead
        *given, family = names[0].split(' ')
        names[0] = given.empty? ? family : "#{family}, #{given.join(' ')}"
      end
      return names.join(' and ') if names.size < 2 || (names.size == 2 && !lead)

      "#{names[0..-2].join(', ')}, and #{names[-1]}"
    end

    private

    def join_names(names)
      names.size < 2 ? names.join : "#{names[0..-2].join(', ')} and #{names[-1]}"
    end
  end
end

Liquid::Template.register_filter(Jekyll::CreditFilter)
