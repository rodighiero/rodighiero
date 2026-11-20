# translation_set / translated_by on each publication — read by publication.html
# (hreflang, og:locale:alternate, JSON-LD translationOfWork / workTranslation).
# publication_cluster — a publication's named cluster from network.json, or else
# its three closest works (the node's `related`), read by publication.html.
#
# A publication's links to other publications, worked out once per build instead of
# by Liquid scanning the whole collection three times on every page.
#
# translation_set is the work's language set, original first and then each
# translation in collection order — this page included, which gives hreflang its
# required self-reference. It is empty for a work with no translations. On a
# translation, its first entry is therefore the source. translated_by lists the
# publications whose translation_of names this particular work.
#
# Entries are plain hashes of what the layout reads (doi so a translation can tell
# whether it shares its source's identifier), not Documents, so no page
# references another through its data (as publication_order.rb does for prev/next).
class Jekyll::PublicationRelationsGenerator < Jekyll::Generator
  def generate(site)
    docs = site.collections['publications'].docs
    by_slug = docs.to_h { |doc| [slug(doc), doc] }
    translations = docs.select { |doc| doc.data['translation_of'] }
                       .group_by { |doc| doc.data['translation_of'].to_s }

    docs.each do |doc|
      origin = by_slug[doc.data['translation_of'].to_s] || doc
      siblings = translations.fetch(slug(origin), [])
      doc.data['translation_set'] = siblings.empty? ? [] : [origin, *siblings].map { |d| ref(d) }
      doc.data['translated_by'] = translations.fetch(slug(doc), []).map { |d| ref(d) }
      doc.data.delete('publication_cluster')
    end

    network = site.data['network'] || {}
    # number is the cluster's 1-based position in network.json, the same number
    # home.html prints on its cluster card ("Research cluster N").
    clusters = (network['clusters'] || []).each_with_index.each_with_object({}) do |(cluster, index), groups|
      members = cluster.fetch('slugs').filter_map { |member| by_slug[member] }
      next if members.size < 2

      items = members.map { |doc| citation_ref(doc) }
      group = { 'title' => cluster.fetch('title'), 'number' => index + 1, 'items' => items }
      members.each { |doc| groups[slug(doc)] = group }
    end

    # Outside a named cluster, the page's three closest works — the node's
    # `related` list, the same one the network view's details panel shows.
    network.fetch('nodes', []).each do |node|
      next if clusters.key?(node['slug'])

      items = (node['related'] || []).filter_map { |r| by_slug[r['slug']] }.map { |doc| citation_ref(doc) }
      clusters[node['slug']] = { 'title' => 'Related publications', 'items' => items } if items.any?
    end

    clusters.each do |member, group|
      by_slug.fetch(member).data['publication_cluster'] = group
    end
  end

  private

  def slug(doc)
    doc.url.delete_prefix('/')
  end

  def ref(doc)
    doc.data.slice('title', 'edition', 'lang', 'type', 'doi').merge('url' => doc.url)
  end

  def citation_ref(doc)
    ref(doc).merge(doc.data.slice('author', 'editor', 'translator', 'interviewer', 'year',
                                  'venue', 'publisher', 'place', 'volume', 'issue', 'pages'))
  end
end
