# The site's canonical publication order — year descending with Forthcoming
# first, then title ascending within each year — defined once, here.
#
# Reaches three places: site.data.ordered_publications (read by home.html for
# the gallery flow), and the Jekyll::OrderedPublications module below, which
# publication_neighbors.rb and publication_date.rb both consume. So the
# gallery, the prev/next nav and the RSS feed cannot disagree.
module Jekyll::OrderedPublications
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

  def self.docs(site)
    site.collections['publications']&.docs || []
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  site.data['ordered_publications'] =
    Jekyll::OrderedPublications.order(Jekyll::OrderedPublications.docs(site))
end
