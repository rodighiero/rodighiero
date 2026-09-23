# date on each publication — read by the jekyll-feed gem, not by any template here.
#
# Derives it from `year` alone — the only date a publication carries — preserving
# the homepage sort order (year desc, then the within-year tie-break
# publication_order.rb decides) in the RSS feed. Every entry of a given year is
# dated to its January 1st; what orders them inside it is the offset below, not a
# calendar date. Forthcoming entries, which have no year, are dated to when they
# were added (see below).
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
    groups = Jekyll::OrderedPublications.order(docs, site).group_by { |doc| doc.data['year'].to_i }
    newest = nil
    groups.each do |year, sorted|
      next if year.zero?

      sorted.each_with_index do |doc, i|
        # Add the offset as time arithmetic: a raw seconds argument to
        # Time.new would raise once a year holds more than 86400 titles.
        doc.data['date'] = Time.new(year, 1, 1, 12, 0, 0) + (sorted.size - 1 - i)
        newest = doc.data['date'] if newest.nil? || doc.data['date'] > newest
      end
    end

    # A non-numeric year (e.g. "Forthcoming") yields 0. These are dated to the
    # most recent commit that added one of them — stable across deploys, where
    # the build clock this used to take re-dated them on every push and told
    # feed readers they had been republished. Never in the future (a commit
    # predates the build), which would trip Jekyll's future-date filter and drop
    # the page. Floored a day past the newest dated entry so they still sort
    # first in the feed, as on the homepage, even when added in an earlier year.
    forthcoming = groups[0]
    return unless forthcoming

    added = Jekyll::OrderedPublications.added_dates(site)
    stamps = forthcoming.map { |doc| added[doc.relative_path] }.compact
    base = stamps.empty? ? site.time : Time.at(stamps.max)
    base = [base, newest + 86_400].max if newest
    base = [base, site.time].min
    forthcoming.each_with_index { |doc, i| doc.data['date'] = base - i }
  end
end
