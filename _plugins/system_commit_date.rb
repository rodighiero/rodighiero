# commit_date on each publication and on site.data — read by sitemap.xml (lastmod)
# and publication.html (article:modified_time, JSON-LD dateModified).
#
# Per publication: that file's last commit date as YYYY-MM-DD. Falls back to
# page.year-01-01 (or today) when git history is unavailable — e.g. a
# shallow checkout that doesn't include the file's introducing commit.
#
# On site.data: the last commit touching anything that reaches _site, which is
# not the same as HEAD — see PUBLISHED_ANYWAY below.
require 'open3'

class Jekyll::CommitDateGenerator < Jekyll::Generator
  priority :high

  # site.data.commit_date is the homepage's <lastmod>, so it must move only
  # when something a reader can see moves. HEAD alone would report a commit
  # touching CLAUDE.md, a skill or a build script as a change to the page.
  #
  # Jekyll's own `exclude:` already names most of what never reaches _site, so
  # the list is read from the config rather than kept in step with it by hand.
  # Two adjustments it cannot supply:
  UNPUBLISHED = %w[.claude .github .gitignore].freeze          # dot-paths Jekyll drops implicitly
  PUBLISHED_ANYWAY = %w[README.md].freeze                      # excluded from the build, but it *is* the bio

  def generate(site)
    @source = site.source
    collection = site.collections['publications']
    docs = collection&.docs || []
    dates = commit_dates_under(collection&.relative_directory || '_publications')
    docs.each do |doc|
      doc.data['commit_date'] = dates[doc.relative_path] || fallback_date(doc.data['year'])
    end
    site.data['commit_date'] = published_commit_date(site) ||
                               Time.now.utc.strftime('%Y-%m-%d')
  end

  private

  # The newest commit touching anything that ends up in _site. A repo whose
  # every commit is excluded (or no git at all) returns nil and falls back to
  # today, as before — a missing lastmod is worse than an imprecise one.
  def published_commit_date(site)
    excluded = (Array(site.config['exclude']) + UNPUBLISHED - PUBLISHED_ANYWAY)
               .map { |path| ":(exclude)#{path.to_s.chomp('/')}" }
    commit_date('.', *excluded)
  end

  # Only a four-digit year can stand in for a date. `year: Forthcoming` would
  # otherwise yield "Forthcoming-01-01" — an invalid <lastmod> and an invalid
  # dateModified — so it falls through to today instead.
  def fallback_date(year)
    year.to_s.match?(/\A\d{4}\z/) ? "#{year}-01-01" : Time.now.utc.strftime('%Y-%m-%d')
  end

  # One `git log` walk covering every file under `dir`, instead of a
  # separate subprocess per document (61+ forks/build otherwise). Keys are
  # paths relative to the repo root, matching Document#relative_path.
  def commit_dates_under(dir)
    stdout, status = capture_git(
      'log', '--name-only', '--pretty=format:%x00%cd', '--date=short', '--', dir
    )
    return {} unless status&.success?

    dates = {}
    stdout.split("\0").each do |chunk|
      lines = chunk.split("\n")
      date = lines.shift
      next unless date

      # git log is newest-first, so the first date seen per path wins.
      lines.each do |line|
        file = line.strip
        dates[file] ||= date unless file.empty?
      end
    end
    dates
  end

  def commit_date(*pathspecs)
    stdout, status = capture_git('log', '-1', '--format=%cd', '--date=short', '--', *pathspecs)
    status&.success? && !stdout.empty? ? stdout.strip : nil
  end

  # Always runs in the site source, so the relative paths above do not depend
  # on the working directory Jekyll happened to be invoked from.
  def capture_git(*args)
    Open3.capture2('git', *args, chdir: @source)
  rescue Errno::ENOENT
    Jekyll.logger.warn 'system_commit_date:', 'git not found on PATH'
    ['', nil]
  end
end
