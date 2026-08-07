require 'open3'

# Adds git_mtime (last commit date as YYYY-MM-DD) to each publication doc
# and to site.data, for accurate sitemap lastmod values. Falls back to
# page.year-01-01 (or today) when git history is unavailable — e.g. a
# shallow checkout that doesn't include the file's introducing commit.
class GitMtimeGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    docs = site.collections['publications']&.docs
    if docs
      dates = git_mtimes_by_path(site, '_publications')
      docs.each do |doc|
        doc.data['git_mtime'] = dates[doc.relative_path] ||
                                "#{doc.data['year']}-01-01"
      end
    end
    site.data['git_mtime'] = git_mtime('.') ||
                             Time.now.utc.strftime('%Y-%m-%d')
  end

  private

  # One `git log` walk covering every file under `dir`, instead of a
  # separate subprocess per document (61+ forks/build otherwise).
  def git_mtimes_by_path(site, dir)
    stdout, status = Open3.capture2(
      'git', 'log', '--name-only', '--pretty=format:%x00%cd', '--date=short', '--', dir
    )
    return {} unless status.success?

    dates = {}
    stdout.split("\0").each do |chunk|
      lines = chunk.split("\n")
      date = lines.shift
      next unless date

      # git log is newest-first, so the first date seen per path wins.
      lines.each { |file| dates[file.strip] ||= date unless file.strip.empty? }
    end
    dates
  rescue Errno::ENOENT
    Jekyll.logger.warn 'GitMtimeGenerator:', 'git not found on PATH'
    {}
  end

  def git_mtime(path)
    stdout, status = Open3.capture2(
      'git', 'log', '-1', '--format=%cd', '--date=short', '--', path
    )
    status.success? && !stdout.empty? ? stdout.strip : nil
  rescue Errno::ENOENT
    Jekyll.logger.warn 'GitMtimeGenerator:', 'git not found on PATH'
    nil
  end
end
