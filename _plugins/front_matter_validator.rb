# Front matter validation plugin for publications.
# Checks required fields, valid values, and referenced images exist.
# Logs warnings during build; can be run in CI to catch errors before deploy.
class FrontMatterValidator < Jekyll::Generator
  priority :high

  REQUIRED_FIELDS = %w[title year venue type author thumb].freeze
  # Accept DOI, arXiv, hdl (handle), zenodo, EPFL, URLs as valid identifier patterns
  DOI_PATTERN = %r{\Ahttps?://(doi\.org|arxiv\.org|hdl\.handle\.net|zenodo\.org|infoscience\.epfl\.ch|library\.oapen\.org|publications\.jrc\.ec\.europa\.eu|pure\.rug\.nl|nightingaledvs\.com|metispresses\.ch|visap\.net|eticapubblica\.it|networkcultures\.org|antinomie\.it|journal\.dampress\.org|www\.up\.pt|www\.metispresses\.ch)}.freeze

  def generate(site)
    @site = site
    @valid_types = site.data['publication_types']&.keys || []
    @errors = []
    @warnings = []

    docs = site.collections['publications']&.docs
    return unless docs

    docs.each { |doc| validate_publication(doc) }

    report_issues
  end

  private

  def validate_publication(doc)
    slug = doc.data['slug'] || doc.basename
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
    if data['month']
      month = data['month'].to_i
      unless month >= 1 && month <= 12
        @warnings << "#{slug}: month '#{month}' is out of range (1-12), will be clamped"
      end
    end

    if data['day']
      day = data['day'].to_i
      unless day >= 1 && day <= 31
        @warnings << "#{slug}: day '#{day}' is out of range (1-31), will be clamped"
      end
    end

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

    # Validate ISSN format if present (journals have this)
    if data['issn'] && !data['issn'].to_s.match?(/\A\d{4}-\d{4}\z/)
      @warnings << "#{slug}: issn '#{data['issn']}' doesn't match format XXXX-XXXX"
    end
  end

  def report_issues
    return if @errors.empty? && @warnings.empty?

    Jekyll.logger.info 'FrontMatterValidator:', "Validation report for publications:"

    @warnings.each do |msg|
      Jekyll.logger.warn 'FrontMatterValidator:', msg
    end

    @errors.each do |msg|
      Jekyll.logger.error 'FrontMatterValidator:', msg
    end

    if @errors.any?
      raise Jekyll::Errors::FatalException, "Front matter validation failed with #{@errors.length} error(s)"
    end
  end
end
