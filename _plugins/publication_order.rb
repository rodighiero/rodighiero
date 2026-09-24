# The site's canonical publication order, defined once, here, and published as
# site.data.ordered_publications — read by home.html for the gallery flow and by
# two Generators, publication_neighbors.rb and publication_date.rb, which run
# after every post_read hook. So the gallery, the prev/next nav and the RSS feed
# cannot disagree.
require 'open3'

module Jekyll::OrderedPublications
  # Works run newest year first. Forthcoming — the one non-numeric year the
  # validator allows — counts as the current year, so it sits among this year's
  # additions by when it was added rather than pinned above everything; giving
  # it its real year once it is out leaves it where it was.
  #
  # The tie-break inside a year is where the two rules part. The current year is
  # the block a returning reader scans for what is new, so it is ordered by when
  # the file was added. Every other year is an archive arrived at already knowing
  # the year, so it keeps the alphabetical index. The test is Time.now.year, so
  # on 1 January the outgoing year falls back to alphabetical of its own accord —
  # nothing to remember at the turn of a year.
  def self.year_of(doc)
    doc.data['year'].to_i.nonzero? || Time.now.year
  end

  def self.sort_key(doc, added)
    year = year_of(doc)
    # Negated so the newest addition sorts first. Every other year puts 0 here,
    # which is inert and lets the title decide — and keeps the tuple one shape,
    # so no two keys ever compare an Integer against a String.
    recency = year == Time.now.year ? -(added[doc.relative_path] || 0) : 0
    [-year, recency, doc.data['title'].to_s.downcase]
  end

  def self.order(site)
    added = walk_added(site.source)
    (site.collections['publications']&.docs || []).sort_by { |doc| sort_key(doc, added) }
  end

  # Epoch seconds of the commit that introduced each publication, keyed by the
  # path Document#relative_path reports — one `git log` walk per build. It walks
  # git rather than reading the commit_date system_commit_date.rb attaches: that
  # value is the *last* commit touching a file, so ordering by it would reshuffle
  # the year on every typo fix, and it is attached by a Generator, after this
  # post_read hook has run.
  #
  # --diff-filter=AR keeps only adds and renames. Both sides of a rename inside
  # _publications/ fall under the pathspec, so git reports a rename, not an add,
  # and the new path takes the old one's date — renaming a publication never
  # moves it. Oldest commit first: the first add of a path is its earliest (a
  # delete and re-add adds it twice), and a rename finds its old path already
  # dated, down a chain a→b→c.
  #
  # No git, or a shallow checkout missing the introducing commit, yields no
  # entry; the recency slot stays 0 and the year falls back to alphabetical —
  # the same degradation system_commit_date.rb takes.
  def self.walk_added(source)
    stdout, status = Open3.capture2(
      'git', 'log', '--reverse', '--name-status', '--diff-filter=AR', '--pretty=format:%ct',
      '--', '_publications', chdir: source
    )
    return {} unless status&.success?

    added = {}
    stamp = nil
    stdout.each_line(chomp: true) do |line|
      kind, from, to = line.split("\t")
      case kind
      when /\A\d+\z/ then stamp = kind.to_i
      when 'A' then added[from] ||= stamp
      when /\AR/ then added[to] = added[from] if added[from]
      end
    end
    added
  rescue Errno::ENOENT
    Jekyll.logger.warn 'publication_order:', 'git not found on PATH'
    {}
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  site.data['ordered_publications'] = Jekyll::OrderedPublications.order(site)
end
