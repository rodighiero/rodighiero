require 'open3'

# Adds git_mtime (last commit date as YYYY-MM-DD) to each publication doc
# and to site.data, for accurate sitemap lastmod values. Falls back to
# page.year-01-01 (or today) when git history is unavailable — e.g. a
# shallow checkout that doesn't include the file's introducing commit.
class GitMtimeGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    @source = site.source
    collection = site.collections['publications']
    docs = collection&.docs || []
    dates = git_mtimes_under(collection&.relative_directory || '_publications')
    docs.each do |doc|
      doc.data['git_mtime'] = dates[doc.relative_path] || fallback_date(doc.data['year'])
    end
    site.data['git_mtime'] = git_mtime('.') || Time.now.utc.strftime('%Y-%m-%d')
  end

  private

  # Only a four-digit year can stand in for a date. `year: Forthcoming` would
  # otherwise yield "Forthcoming-01-01" — an invalid <lastmod> and an invalid
  # dateModified — so it falls through to today instead.
  def fallback_date(year)
    year.to_s.match?(/\A\d{4}\z/) ? "#{year}-01-01" : Time.now.utc.strftime('%Y-%m-%d')
  end

  # One `git log` walk covering every file under `dir`, instead of a
  # separate subprocess per document (61+ forks/build otherwise). Keys are
  # paths relative to the repo root, matching Document#relative_path.
  def git_mtimes_under(dir)
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

  def git_mtime(path)
    stdout, status = capture_git('log', '-1', '--format=%cd', '--date=short', '--', path)
    status&.success? && !stdout.empty? ? stdout.strip : nil
  end

  # Always runs in the site source, so the relative paths above do not depend
  # on the working directory Jekyll happened to be invoked from.
  def capture_git(*args)
    Open3.capture2('git', *args, chdir: @source)
  rescue Errno::ENOENT
    Jekyll.logger.warn 'GitMtimeGenerator:', 'git not found on PATH'
    ['', nil]
  end
end
