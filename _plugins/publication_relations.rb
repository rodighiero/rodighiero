# translation_set / translated_by on each publication — read by publication.html
# (hreflang, og:locale:alternate, JSON-LD translationOfWork / workTranslation).
# related on each publication — read by publication.html ("Related publications").
# publication_series — curated edition/research links from publication_series.yml.
#
# A publication's links to other publications, worked out once per build instead of
# by Liquid scanning the whole collection three times on every page.
#
# translation_set is the work's language set, original first and then each
# translation in collection order — this page included, which gives hreflang its
# required self-reference. It is empty for a work with no translations. On a
# translation, its first entry is therefore the source. translated_by is the set's
# translations minus this page: on the original all of them, on a translation its
# siblings.
#
# related is the page's node's `related` list from _data/network.json, the same list
# the network view's details panel shows; empty for a page with no node.
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
    related = (site.data.dig('network', 'nodes') || []).to_h { |node| [node['url'], node['related']] }

    docs.each do |doc|
      origin = by_slug[doc.data['translation_of'].to_s] || doc
      siblings = translations.fetch(slug(origin), [])
      doc.data['translation_set'] = siblings.empty? ? [] : [origin, *siblings].map { |d| ref(d) }
      doc.data['translated_by'] = (siblings - [doc]).map { |d| ref(d) }
      doc.data['related'] = related[doc.url] || []
    end

    (site.data['publication_series'] || []).each do |series|
      members = series.fetch('publications').map do |member|
        by_slug.fetch(member) do
          raise Jekyll::Errors::FatalException, "publication_relations: unknown series publication '#{member}'"
        end
      end
      group = { 'title' => series.fetch('title'), 'items' => members.map { |d| ref(d).merge('year' => d.data['year']) } }
      members.each { |doc| doc.data['publication_series'] = group }
    end
  end

  private

  def slug(doc)
    doc.url.delete_prefix('/')
  end

  def ref(doc)
    doc.data.slice('title', 'lang', 'type', 'doi').merge('url' => doc.url)
  end
end
