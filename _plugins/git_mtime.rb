require 'open3'

# Adds git_mtime (last commit date as YYYY-MM-DD) to each publication doc
# and to site.data, for accurate sitemap lastmod values. Falls back to
# page.year-01-01 (or today) when git history is unavailable — e.g. a
# shallow checkout that doesn't include the file's introducing commit.
class GitMtimeGenerator < Jekyll::Generator
  priority :high

  def generate(site)
    site.collections['publications']&.docs&.each do |doc|
      doc.data['git_mtime'] = git_mtime(doc.path) ||
                              "#{doc.data['year']}-01-01"
    end
    site.data['git_mtime'] = git_mtime('.') ||
                             Time.now.utc.strftime('%Y-%m-%d')
  end

  private

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
