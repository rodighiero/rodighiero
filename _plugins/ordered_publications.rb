# Publications ordered year-descending (Forthcoming first), then title-ascending
# within each year — the single ordering both the homepage gallery and the
# publication-page prev/next nav need. Mirrors what
# `site.publications | group_by: "year" | sort: "name" | reverse` plus a
# per-group title sort produces in Liquid (grouping on the stringified year,
# same as Jekyll's group_by filter, so "Forthcoming" sorts before any 4-digit
# year), computed once here instead of duplicated in each layout.
Jekyll::Hooks.register :site, :post_read do |site|
  docs = site.collections['publications']&.docs || []
  site.data['ordered_publications'] = docs
    .group_by { |doc| doc.data['year'].to_s }
    .sort_by { |year, _| year }
    .reverse
    .flat_map { |_, group| group.sort_by { |doc| doc.data['title'].to_s } }
end
