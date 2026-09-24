# prev_pub / next_pub on each publication — read by publication-nav.html.
#
# Gives every document its two neighbors up front, so the publication layout
# reads page.prev_pub / page.next_pub instead of scanning the whole collection
# in Liquid on each page. The order is site.data.ordered_publications, which
# publication_order.rb's post_read hook has published before any Generator runs.
class Jekyll::PublicationNeighborsGenerator < Jekyll::Generator
  def generate(site)
    ordered = site.data['ordered_publications']
    ordered.each_with_index do |doc, i|
      doc.data['prev_pub'] = nav_ref(i.zero? ? nil : ordered[i - 1])
      doc.data['next_pub'] = nav_ref(ordered[i + 1])
    end
  end

  # Only what publication-nav.html reads. Storing the neighboring Document
  # itself would make each pair reference the other through page data, so a
  # plain hash keeps the graph acyclic.
  def nav_ref(doc)
    doc && { 'url' => doc.url, 'title' => doc.data['title'] }
  end
end
