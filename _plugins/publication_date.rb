# Sets page.date from page.year (+ optional month, day) for publications,
# preserving the homepage sort order (year desc, then alphabetical within each year)
# in the RSS feed.
#
# Front matter support:
#   year: 2024              # Required
#   month: 6                # Optional (1-12; default 1)
#   day: 15                 # Optional (1-31; default 1)
#
# Within a year, alphabetically-first titles get a slightly later timestamp
# so they appear first in the feed (which sorts newest-first).
class PublicationDateGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    docs = site.collections['publications']&.docs
    return unless docs

    docs.group_by { |doc| doc.data['year'].to_i }.each do |year, group|
      sorted = group.sort_by { |doc| doc.data['title'].to_s.downcase }
      sorted.each_with_index do |doc, i|
        if year.zero?
          # A non-numeric year (e.g. "Forthcoming") yields 0. Date it at build
          # time so it sorts newest in the feed (matching the homepage, where
          # it sorts first) — but never in the future, which would trip
          # Jekyll's future-date filter and drop the page from the build.
          doc.data['date'] = site.time - i
        else
          month = (doc.data['month'] || 1).to_i.clamp(1, 12)
          day = (doc.data['day'] || 1).to_i.clamp(1, 31)
          # Add the offset as time arithmetic: a raw seconds argument to
          # Time.new would raise once a year holds more than 86400 titles.
          doc.data['date'] = Time.new(year, month, day, 12, 0, 0) + (sorted.size - 1 - i)
        end
      end
    end
  end
end
