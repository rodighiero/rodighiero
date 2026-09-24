# date on each publication — read by the jekyll-feed gem, not by any template here.
#
# Derives it from `year` alone — the only date a publication carries — preserving
# the homepage sort order (year desc, then the within-year tie-break
# publication_order.rb decides) in the RSS feed. Every entry of a given year is
# dated to its January 1st; what orders them inside it is the offset below, not a
# calendar date. Forthcoming entries, which have no year, are dated inside the
# current year, where the homepage places them.
#
# Within a year, whichever title the canonical order puts first gets a slightly
# later timestamp so it appears first in the feed (which sorts newest-first).
class Jekyll::PublicationDateGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    # The list the homepage renders (publication_order.rb's post_read hook, which
    # has run by the time any Generator does), grouped by year, keeps each year's
    # titles in exactly the gallery's order, so the feed and the gallery can never
    # disagree. year_of is the same year the order sorts on, so Forthcoming groups
    # with the current year here as well.
    site.data['ordered_publications'].group_by { |doc| Jekyll::OrderedPublications.year_of(doc) }.each do |year, sorted|
      sorted.each_with_index do |doc, i|
        # Add the offset as time arithmetic: a raw seconds argument to
        # Time.new would raise once a year holds more than 86400 titles.
        doc.data['date'] = Time.new(year, 1, 1, 12, 0, 0) + (sorted.size - 1 - i)
      end
    end
  end
end
