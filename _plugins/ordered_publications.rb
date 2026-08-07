# The site's canonical publication order: year descending with Forthcoming
# first, then title ascending within each year.
#
# Exposed as site.data.ordered_publications for the layouts (the gallery flow
# and the prev/next nav) and reused by PublicationDateGenerator for the feed,
# so the rule lives in exactly one place.
module OrderedPublications
  # Forthcoming — any year that is not four digits — sorts ahead of every dated
  # work; dated works then run newest first, ties broken alphabetically.
  def self.sort_key(doc)
    year = doc.data['year'].to_s
    dated = year.match?(/\A\d{4}\z/)
    [dated ? 1 : 0, dated ? -year.to_i : 0, doc.data['title'].to_s.downcase]
  end

  def self.order(docs)
    docs.sort_by { |doc| sort_key(doc) }
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  docs = site.collections['publications']&.docs || []
  site.data['ordered_publications'] = OrderedPublications.order(docs)
end
