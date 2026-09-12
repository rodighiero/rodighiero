# The site's canonical publication order — year descending with Forthcoming
# first, then, within a year, newest-added first for the current year and title
# ascending for every other — defined once, here.
#
# Reaches three places: site.data.ordered_publications (read by home.html for
# the gallery flow), and the Jekyll::OrderedPublications module below, which
# publication_neighbors.rb and publication_date.rb both consume. So the
# gallery, the prev/next nav and the RSS feed cannot disagree.
require 'open3'

module Jekyll::OrderedPublications
  # Forthcoming — any year that is not four digits — sorts ahead of every dated
  # work; dated works then run newest first.
  #
  # The tie-break inside a year is where the two rules part. The current year is
  # the block a returning reader scans for what is new, so it is ordered by when
  # the file was added. Every other year is an archive arrived at already knowing
  # the year, so it keeps the alphabetical index. The test is Time.now.year, so
  # on 1 January the outgoing year falls back to alphabetical of its own accord —
  # nothing to remember at the turn of a year.
  def self.sort_key(doc, added)
    year = doc.data['year'].to_s
    dated = year.match?(/\A\d{4}\z/)
    current = dated && year.to_i == Time.now.year
    # Negated so the newest addition sorts first. Every other year puts 0 here,
    # which is inert and lets the title decide — and keeps the tuple one shape,
    # so no two keys ever compare an Integer against a String.
    recency = current ? -(added[doc.relative_path] || 0) : 0
    [dated ? 1 : 0, dated ? -year.to_i : 0, recency, doc.data['title'].to_s.downcase]
  end

  def self.order(docs, site)
    added = added_dates(site)
    docs.sort_by { |doc| sort_key(doc, added) }
  end

  def self.docs(site)
    site.collections['publications']&.docs || []
  end

  # Epoch seconds of the commit that introduced each publication, keyed by the
  # path Document#relative_path reports. One `git log` walk for the whole
  # collection, memoized because order() is asked for three times per build.
  #
  # This walks git rather than reading the commit_date system_commit_date.rb
  # attaches, for two reasons. That value is the *last* commit touching a file,
  # so ordering by it would reshuffle the year on every typo fix. And it is
  # attached by a Generator, which runs after the post_read hooks that ask for
  # this order — it does not exist yet when the question is put.
  def self.added_dates(site)
    @added_dates ||= walk_added(site.source)
  end

  # --diff-filter=A asks only for the commits that introduce a file, so the walk
  # is the adds and nothing else. A rename registers as an add at the new path
  # (--follow cannot be combined with a whole-directory pathspec), so renaming a
  # publication of the current year moves it to the top of that year. Renames
  # are rare and the slot is only a tie-break, so this stays a known edge rather
  # than a second git walk per file.
  #
  # No git, or a shallow checkout missing the introducing commit, yields no
  # entry; the recency slot stays 0 and the year falls back to alphabetical —
  # the same degradation system_commit_date.rb takes.
  def self.walk_added(source)
    stdout, status = Open3.capture2(
      'git', 'log', '--name-only', '--diff-filter=A', '--pretty=format:%x00%ct',
      '--', '_publications', chdir: source
    )
    return {} unless status&.success?

    added = {}
    stdout.split("\0").each do |chunk|
      lines = chunk.split("\n")
      stamp = lines.shift
      next unless stamp

      lines.each do |line|
        file = line.strip
        # git log is newest-first, and a path can be added more than once (a
        # delete and re-add), so the last one seen is the earliest add.
        added[file] = stamp.to_i unless file.empty?
      end
    end
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
