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
    # Published by publication_order.rb's post_read hook, which has run by the
    # time any Generator does.
    site.data['ordered_publications'].group_by { |doc| Jekyll::OrderedPublications.year_of(doc) }.each do |year, sorted|
      # Add the offset as time arithmetic: a raw seconds argument to
      # Time.new would raise once a year holds more than 86400 titles.
      sorted.reverse.each_with_index { |doc, i| doc.data['date'] = Time.new(year, 1, 1, 12) + i }
    end
  end
end
