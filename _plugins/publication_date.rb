# date on each publication — read by the jekyll-feed gem, not by any template here.
#
# Derives it from `year` alone — the only date a publication carries — preserving
# the homepage sort order (year desc, then the within-year tie-break
# publication_order.rb decides) in the RSS feed. Every entry of a given year is
# dated to its January 1st; what orders them inside it is the offset below, not a
# calendar date.
#
# Within a year, whichever title the canonical order puts first gets a slightly
# later timestamp so it appears first in the feed (which sorts newest-first).
class Jekyll::PublicationDateGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    docs = site.collections['publications']&.docs
    return unless docs

    # Grouping the canonically ordered list keeps each year's titles in exactly
    # the order the homepage shows (Jekyll::OrderedPublications, defined in
    # publication_order.rb), so the feed and the gallery can never disagree.
    Jekyll::OrderedPublications.order(docs, site).group_by { |doc| doc.data['year'].to_i }.each do |year, sorted|
      sorted.each_with_index do |doc, i|
        if year.zero?
          # A non-numeric year (e.g. "Forthcoming") yields 0. Date it at build
          # time so it sorts newest in the feed (matching the homepage, where
          # it sorts first) — but never in the future, which would trip
          # Jekyll's future-date filter and drop the page from the build.
          doc.data['date'] = site.time - i
        else
          # Add the offset as time arithmetic: a raw seconds argument to
          # Time.new would raise once a year holds more than 86400 titles.
          doc.data['date'] = Time.new(year, 1, 1, 12, 0, 0) + (sorted.size - 1 - i)
        end
      end
    end
  end
end
