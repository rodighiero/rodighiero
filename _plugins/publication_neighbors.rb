# prev_pub / next_pub on each publication — read by publication-nav.html.
#
# Gives every document its two neighbors up front, so the publication layout
# reads page.prev_pub / page.next_pub instead of scanning the whole collection
# in Liquid on each of the 60-odd pages.
#
# The order comes from Jekyll::OrderedPublications (publication_order.rb),
# which this asks for directly rather than reading site.data.ordered_publications
# — both are post_read hooks, and calling the shared module keeps this one
# independent of which hook happens to run first.
module Jekyll::NeighborPublications
  # Only what publication-nav.html reads. Storing the neighboring Document
  # itself would make each pair reference the other through page data, so a
  # plain hash keeps the graph acyclic.
  def self.nav_ref(doc)
    doc && { 'url' => doc.url, 'title' => doc.data['title'] }
  end

  def self.link(ordered)
    ordered.each_with_index do |doc, i|
      doc.data['prev_pub'] = nav_ref(i.zero? ? nil : ordered[i - 1])
      doc.data['next_pub'] = nav_ref(ordered[i + 1])
    end
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  Jekyll::NeighborPublications.link(
    Jekyll::OrderedPublications.order(Jekyll::OrderedPublications.docs(site))
  )
end
