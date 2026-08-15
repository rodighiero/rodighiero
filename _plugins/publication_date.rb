# date on each publication — read by the jekyll-feed gem, not by any template here.
#
# Derives it from year (+ optional month, day), preserving the homepage sort
# order (year desc, then alphabetical within each year) in the RSS feed.
#
# Front matter support:
#   year: 2024              # Required
#   month: 6                # Optional (1-12; default 1)
#   day: 15                 # Optional (1-31; default 1)
#
# Within a year, alphabetically-first titles get a slightly later timestamp
# so they appear first in the feed (which sorts newest-first).
class Jekyll::PublicationDateGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    docs = site.collections['publications']&.docs
    return unless docs

    # Grouping the canonically ordered list keeps each year's titles in exactly
    # the order the homepage shows (Jekyll::OrderedPublications, defined in
    # publication_order.rb), so the feed and the gallery can never disagree.
    Jekyll::OrderedPublications.order(docs).group_by { |doc| doc.data['year'].to_i }.each do |year, sorted|
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
