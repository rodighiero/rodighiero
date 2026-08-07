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

  # Only what publication-nav.html reads. Storing the neighbouring Document
  # itself would make each pair reference the other through page data, so a
  # plain hash keeps the graph acyclic.
  def self.nav_ref(doc)
    doc && { 'url' => doc.url, 'title' => doc.data['title'] }
  end

  # Give each document its neighbours up front, so the publication layout can
  # read page.prev_pub / page.next_pub instead of scanning the whole ordered
  # list in Liquid on every one of the 61 pages.
  def self.link_neighbours(ordered)
    ordered.each_with_index do |doc, i|
      doc.data['prev_pub'] = nav_ref(i.zero? ? nil : ordered[i - 1])
      doc.data['next_pub'] = nav_ref(ordered[i + 1])
    end
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  docs = site.collections['publications']&.docs || []
  ordered = OrderedPublications.order(docs)
  OrderedPublications.link_neighbours(ordered)
  site.data['ordered_publications'] = ordered
end
