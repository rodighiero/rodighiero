# The site's canonical publication order — year descending, with Forthcoming
# counted as the current year, then, within a year, newest-added first for the
# current year and title ascending for every other — defined once, here.
#
# Reaches three places: site.data.ordered_publications (read by home.html for
# the gallery flow, and by publication_date.rb, a Generator that runs after
# every post_read hook), and the Jekyll::OrderedPublications module below,
# which publication_neighbors.rb — a post_read hook itself — calls directly. So
# the gallery, the prev/next nav and the RSS feed cannot disagree.
require 'open3'

module Jekyll::OrderedPublications
  # Works run newest year first. Forthcoming — any year that is not four digits
  # — counts as the current year, so it sits among this year's additions by
  # when it was added rather than pinned above everything; giving it its real
  # year once it is out leaves it where it was.
  #
  # The tie-break inside a year is where the two rules part. The current year is
  # the block a returning reader scans for what is new, so it is ordered by when
  # the file was added. Every other year is an archive arrived at already knowing
  # the year, so it keeps the alphabetical index. The test is Time.now.year, so
  # on 1 January the outgoing year falls back to alphabetical of its own accord —
  # nothing to remember at the turn of a year.
  def self.year_of(doc)
    year = doc.data['year'].to_s
    year.match?(/\A\d{4}\z/) ? year.to_i : Time.now.year
  end

  def self.sort_key(doc, added)
    year = year_of(doc)
    # Negated so the newest addition sorts first. Every other year puts 0 here,
    # which is inert and lets the title decide — and keeps the tuple one shape,
    # so no two keys ever compare an Integer against a String.
    recency = year == Time.now.year ? -(added[doc.relative_path] || 0) : 0
    [-year, recency, doc.data['title'].to_s.downcase]
  end

  def self.order(docs, site)
    added = walk_added(site.source)
    docs.sort_by { |doc| sort_key(doc, added) }
  end

  def self.docs(site)
    site.collections['publications']&.docs || []
  end

  # Epoch seconds of the commit that introduced each publication, keyed by the
  # path Document#relative_path reports. One `git log` walk for the whole
  # collection, about 20 ms, redone on each order() call rather than memoized: a
  # module-level memo outlives the build under `jekyll serve`, so a publication
  # committed mid-session would get no date and sink until a restart.
  #
  # This walks git rather than reading the commit_date system_commit_date.rb
  # attaches, for two reasons. That value is the *last* commit touching a file,
  # so ordering by it would reshuffle the year on every typo fix. And it is
  # attached by a Generator, which runs after the post_read hooks that ask for
  # this order — it does not exist yet when the question is put.

  # --diff-filter=AR asks only for the commits that introduce or rename a file.
  # Both sides of a rename inside _publications/ fall under the pathspec, so git
  # reports it as a rename, not an add — an add-only walk would leave the new
  # path with no entry and sink it to the bottom of the current year. Instead a
  # rename hands the new path the add date of the old one, so renaming a
  # publication never moves it.
  #
  # No git, or a shallow checkout missing the introducing commit, yields no
  # entry; the recency slot stays 0 and the year falls back to alphabetical —
  # the same degradation system_commit_date.rb takes.
  def self.walk_added(source)
    stdout, status = Open3.capture2(
      'git', 'log', '--name-status', '--diff-filter=AR', '--pretty=format:%x00%ct',
      '--', '_publications', chdir: source
    )
    return {} unless status&.success?

    added = {}
    renames = []
    stdout.split("\0").each do |chunk|
      lines = chunk.split("\n")
      stamp = lines.shift
      next unless stamp

      lines.each do |line|
        kind, *paths = line.strip.split("\t")
        next unless kind

        # git log is newest-first, and a path can be added more than once (a
        # delete and re-add), so the last one seen is the earliest add.
        if kind == 'A'
          added[paths.first] = stamp.to_i
        elsif kind.start_with?('R')
          renames << paths
        end
      end
    end
    # Oldest rename first, so a chain a→b→c carries a's date all the way to c.
    renames.reverse_each { |from, to| added[to] = added[from] if added[from] }
    added
  rescue Errno::ENOENT
    Jekyll.logger.warn 'publication_order:', 'git not found on PATH'
    {}
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  site.data['ordered_publications'] =
    Jekyll::OrderedPublications.order(Jekyll::OrderedPublications.docs(site), site)
end
