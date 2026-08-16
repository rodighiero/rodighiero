# Validates every publication's front matter — required fields, valid type,
# referenced images on disk, ISSN/ISBN shape *and* check digit, and that
# translation_of resolves to a real publication. Introduces no identifier a
# template can read; its output is the build log.
#
# Warnings are advisory; an error raises and aborts the build, so bad metadata
# is caught on every deploy rather than shipped.
class Jekyll::FrontMatterValidator < Jekyll::Generator
  priority :high

  REQUIRED_FIELDS = %w[title year venue type author thumb].freeze

  def generate(site)
    @site = site
    @valid_types = site.data['publication_types']&.keys || []
    @errors = []
    @warnings = []

    docs = site.collections['publications']&.docs
    return unless docs

    # translation_of names another publication by slug, so the whole set has to
    # be known before any single document can be checked against it.
    @slugs = docs.map { |doc| slug_for(doc) }

    docs.each { |doc| validate_publication(doc) }

    report_issues
  end

  private

  def slug_for(doc)
    doc.data['slug'] || doc.basename
  end

  def validate_publication(doc)
    slug = slug_for(doc)
    data = doc.data

    # Check required fields (author can be replaced by editor)
    required = REQUIRED_FIELDS.dup
    if !data['author'].nil? || !data['editor'].nil?
      required.delete('author')
    end
    
    required.each do |field|
      if data[field].nil? || data[field].to_s.strip.empty?
        @errors << "#{slug}: missing required field '#{field}' (or author/editor for byline)"
      end
    end

    # Validate year is numeric or "Forthcoming"
    year = data['year'].to_s
    unless year =~ /\A\d{4}\z/ || year == 'Forthcoming'
      @errors << "#{slug}: year '#{year}' is invalid (must be 4 digits or 'Forthcoming')"
    end

    # Validate type
    if data['type'] && !@valid_types.include?(data['type'])
      @errors << "#{slug}: type '#{data['type']}' is not in publication_types.yml (valid: #{@valid_types.join(', ')})"
    end

    # Validate month/day if present
    check_range(data, slug, 'month', 1, 12)
    check_range(data, slug, 'day', 1, 31)

    # Validate DOI format if present (accept any https:// URL)
    if data['doi'] && !data['doi'].to_s.start_with?('https://', 'http://')
      @warnings << "#{slug}: doi '#{data['doi']}' doesn't look like a URL (should start with http:// or https://)"
    end

    # Check that thumb image exists
    if data['thumb']
      thumb_path = File.join(@site.source, 'images', data['thumb'])
      unless File.file?(thumb_path)
        @errors << "#{slug}: thumbnail image not found: images/#{data['thumb']}"
      end
    end

    # Validate ISSN format if present (journals have this). The check digit may be
    # an X — 0024-094X (Leonardo) and 2073-445X (Land) both are — so it is not \d.
    if data['issn']
      issn = data['issn'].to_s
      if !issn.match?(/\A\d{4}-\d{3}[\dX]\z/)
        @warnings << "#{slug}: issn '#{issn}' doesn't match format XXXX-XXXX"
      else
        expected = issn_check_digit(issn.delete('-'))
        unless issn[-1].upcase == expected
          @warnings << "#{slug}: issn '#{issn}' fails its check digit (mod 11 expects #{expected}) — likely a transcription error"
        end
      end
    end

    # ISBN-13 or ISBN-10 (whose check digit may also be an X), hyphens optional.
    if data['isbn']
      bare = data['isbn'].to_s.delete('- ')
      if !bare.match?(/\A(\d{13}|\d{9}[\dX])\z/)
        @warnings << "#{slug}: isbn '#{data['isbn']}' is neither a 13- nor a 10-digit ISBN"
      else
        expected = bare.length == 13 ? isbn13_check_digit(bare) : isbn10_check_digit(bare)
        unless bare[-1].upcase == expected
          @warnings << "#{slug}: isbn '#{data['isbn']}' fails its check digit (expects #{expected}) — likely a transcription error"
        end
      end
    end

    # A translation names its original by slug; an unresolved one silently costs
    # the page its hreflang alternates and its forced network edge.
    if data['translation_of'] && !@slugs.include?(data['translation_of'].to_s)
      @warnings << "#{slug}: translation_of '#{data['translation_of']}' matches no publication"
    end
  end

  # ISSN: seven digits weighted 8..2, check digit = 11 - (sum mod 11), where
  # 10 is written X and 11 is written 0.
  def issn_check_digit(bare)
    sum = bare[0, 7].chars.each_with_index.sum { |c, i| c.to_i * (8 - i) }
    mod_11_digit(sum)
  end

  # ISBN-10: nine digits weighted 10..2, same mod-11 rule as the ISSN.
  def isbn10_check_digit(bare)
    sum = bare[0, 9].chars.each_with_index.sum { |c, i| c.to_i * (10 - i) }
    mod_11_digit(sum)
  end

  # ISBN-13 (and every EAN-13): twelve digits weighted 1,3,1,3…, check digit
  # = (10 - sum mod 10) mod 10. No X is possible here.
  def isbn13_check_digit(bare)
    sum = bare[0, 12].chars.each_with_index.sum { |c, i| c.to_i * (i.even? ? 1 : 3) }
    ((10 - sum % 10) % 10).to_s
  end

  def mod_11_digit(sum)
    remainder = 11 - sum % 11
    case remainder
    when 11 then '0'
    when 10 then 'X'
    else remainder.to_s
    end
  end

  def check_range(data, slug, field, min, max)
    return unless data[field]

    value = data[field].to_i
    unless value >= min && value <= max
      @warnings << "#{slug}: #{field} '#{value}' is out of range (#{min}-#{max}), will be clamped"
    end
  end

  def report_issues
    return if @errors.empty? && @warnings.empty?

    Jekyll.logger.info 'publication_validator:', "Validation report for publications:"

    @warnings.each do |msg|
      Jekyll.logger.warn 'publication_validator:', msg
    end

    @errors.each do |msg|
      Jekyll.logger.error 'publication_validator:', msg
    end

    if @errors.any?
      raise Jekyll::Errors::FatalException, "Front matter validation failed with #{@errors.length} error(s)"
    end
  end
end
